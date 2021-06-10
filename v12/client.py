import socket
from win32gui import GetWindowText, GetForegroundWindow
from win32api import GetSystemMetrics
import ctypes
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
from random import uniform
import subprocess
import threading
import time
import os
from cryptography.fernet import Fernet
import cv2
import pytesseract
from fuzzywuzzy import process
import pydirectinput
import numpy as np
from rhba_utils import BotUtils, WindowCapture, HsvFilter, Vision, SellRepair, QuestHandle

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class RHBotClientConnection():
    def __init__(self, ip, delay=0) -> None:
        self.delay = delay
        self.HEADER_LENGTH = 10
        self.IP = ip
        self.PORT = 1351
        self.my_username = "Admin"

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket.connect((self.IP, self.PORT))

        self.client_socket.setblocking(False)

        username = self.my_username.encode('utf-8')
        username_header = f"{len(username):<{self.HEADER_LENGTH}}".encode(
            'utf-8')
        self.client_socket.send(username_header + username)

        with open("key.key") as f:
            key = f.read()
        self.fern = Fernet(key)

    def send_message(self, message):
        if self.delay > 0:
            self.send_message_delayed(message, self.delay)
        else:
            message = message.encode('utf-8')
            message = self.fern.encrypt(message)
            message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode(
                'utf-8')
            self.client_socket.send(message_header + message)

    def send_message_delayed(self, message, delay):
        start_time = time.time()
        t = threading.Thread(target=self.delay_thread,
                             args=(message, delay, start_time))
        t.start()

    def delay_thread(self, message, delay, start_time):
        message = message.encode('utf-8')
        message = self.fern.encrypt(message)
        message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode(
            'utf-8')
        time.sleep(delay - (time.time()-start_time))
        self.client_socket.send(message_header + message)

    def main_loop(self):
        while True:
            time.sleep(0.5)


class ClientKeypressListener():
    def __init__(self, list_servers, delay_spacing=12) -> None:
        self.list_servers = list_servers
        self.listener = None
        self.unreleased_keys = []

        # Hotkey handling
        self.transmitting = True
        self.single_server = None
        self.delay_spacing = delay_spacing
        self.x_loot_only = True
        self.autoloot_enabled = False

        self.quest_handle = QuestHandle()
        self.quest_handle_clicks = 0

        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.game_wincap = WindowCapture(self.gamename)

        # These are for batch recording and sending
        self.batch_recording_ongoing = False
        self.batch_start_time = 0
        self.batch = ""
        self.delay_spread = []
        self.create_random_delays()

        # These are for the sell and repair logic
        self.sell_repair = SellRepair(last_row_protect=True)
        self.selling_ongoing = 0

        # These are for allowing x in all cases
        self.xallow = False

        self.level_name = None
        self.speed = 20
        self.rects, self.speeds = BotUtils.grab_level_rects_and_speeds()

        # Input mode, true = pag, false = custom
        self.inputmode = False

        # Follower mode
        self.followmode = False

    def start_mouse_listener(self):
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click)
        self.mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        if self.selling_ongoing != 0:
            if self.selling_ongoing < time.time() - 4:
                self.selling_ongoing = 0
        elif self.quest_handle_clicks > 0:
            self.quest_handle_clicks -= 1
        # First off need to check if transmitting is enabled
        elif self.transmitting:
            # Need to then check if the click was in the right window
            # Do this by checking if window focused
            if GetWindowText(GetForegroundWindow()) == self.gamename:
                # when pressed is False, that means it's a release event.
                # let's listen only to mouse click releases
                if not pressed:
                    # Need to get the ratio compared to window top left
                    # This will allow common usage on other size monitors
                    # print("x={}, y={}".format(x, y))
                    xratio, yratio = BotUtils.convert_click_to_ratio(
                        self.gamename, x, y)
                    # print("xrat={}, yrat={}".format(xratio, yratio))
                    if self.batch_recording_ongoing:
                        self.batch += str(button) + "|click|" + \
                            "{:.3f}".format((time.time() - self.batch_start_time)) + \
                            "|"+"{:.5f},{:.5f}\n".format(xratio, yratio)
                    else:
                        for server in self.list_servers:
                            server.send_message(
                                str(button) + ","+str(xratio)+"|"+str(yratio))

    def start_keypress_listener(self):
        if self.listener == None:
            self.listener = Listener(on_press=self.on_press,
                                     on_release=self.on_release)
            self.listener.start()

    def on_press(self, key):
        if self.selling_ongoing != 0:
            if self.selling_ongoing < time.time() - 4:
                self.selling_ongoing = 0
        elif key == KeyCode(char='0'):
            print("Exiting bot")
            for server in self.list_servers:
                server.delay = 0
                server.send_message("quit,1")
            os._exit(1)
        elif self.transmitting:
            if key == KeyCode(char='1'):
                self.transmitting = False
                print("TRANSMIT OFF")
            elif key == KeyCode(char='2'):
                self.batch_recording_ongoing = not self.batch_recording_ongoing
                if self.batch_recording_ongoing:
                    print("Starting batch record")
                    self.batch_start_time = time.time()
                else:
                    # todo - create threads to send the batches
                    for i, server in enumerate(self.list_servers):
                        t = threading.Thread(
                            target=self.send_batch, args=(server, self.batch, i))
                        t.start()
                    print("Ending batch record")
                    self.batch = ""
            elif key == KeyCode(char='3'):
                # This will be changed to follower on/off
                self.followmode = not self.followmode
                if self.followmode:
                    for server in self.list_servers:
                        server.send_message("follow,1")
                        print("FOLLOW ON")
                else:
                    for server in self.list_servers:
                        server.send_message("follow,0")
                        print("FOLLOW OFF")
            elif key == KeyCode(char='4'):
                self.inputmode = not self.inputmode
                for server in self.list_servers:
                    if self.inputmode:
                        server.send_message("inputmode,1")
                    else:
                        server.send_message("inputmode,0")
                if self.inputmode:
                    print("Swapping to PAG")
                else:
                    print("Swapping to Custom")
            elif key == KeyCode(char='5'):
                try:
                    x, y = self.find_player()
                    for server in self.list_servers:
                        server.send_message("regroup,{}|{}".format(x, y))
                    print("Regrouping...")
                    time.sleep(0.01)
                    BotUtils.close_map()
                except:
                    print("Unable to find player right now")
            elif key == KeyCode(char='6'):
                self.autoloot_enabled = not self.autoloot_enabled
                if self.autoloot_enabled:
                    for server in self.list_servers:
                        server.send_message("autoloot,on")
                    print("AUTOLOOT ON")
                else:
                    for server in self.list_servers:
                        server.send_message("autoloot,off")
                    print("AUTOLOOT OFF")
            elif key == KeyCode(char='7'):
                self.selling_ongoing = time.time()
                for server in self.list_servers:
                    server.send_message("sellrepair,1")
                print("Selling and repairing...")
                os.popen('python sell_repair.py')
                # self.sell_repair.ident_sell_repair()
            elif key == KeyCode(char='8'):
                self.quest_handle_clicks += 1
                if not self.batch_recording_ongoing:
                    for server in self.list_servers:
                        server.send_message("questhandle,1")
                else:
                    self.batch += str(key) + "|questhandle|" + \
                        "{:.3f}".format(
                            (time.time() - self.batch_start_time)) + "|0,0\n"
                self.quest_handle.start_quest_handle()
            elif key == KeyCode(char='9'):
                self.xallow = not self.xallow
                if self.xallow:
                    for server in self.list_servers:
                        server.send_message("xallow,1")
                    print("XALLOW ON")
                else:
                    for server in self.list_servers:
                        server.send_message("xallow,0")
                    print("XALLOW OFF")
            elif key == KeyCode(char='-'):
                for server in self.list_servers:
                    server.send_message("clearall,1")
                print("Clearing All...")
            elif self.autoloot_enabled and key == KeyCode(char='x'):
                pass
            elif GetWindowText(GetForegroundWindow()) == self.gamename:
                if str(key) not in self.unreleased_keys:
                    if not self.batch_recording_ongoing:
                        for server in self.list_servers:
                            server.send_message(str(key)+",down")
                        self.unreleased_keys.append(str(key))
                    else:
                        self.batch += str(key) + "|keyDown|" + \
                            "{:.3f}".format(
                                (time.time() - self.batch_start_time)) + "|0,0\n"
                        self.unreleased_keys.append(str(key))
        elif key == KeyCode(char='1'):
            self.transmitting = True
            if self.batch_recording_ongoing:
                for i, server in enumerate(self.list_servers):
                    t = threading.Thread(
                        target=self.send_batch, args=(server, self.batch, i))
                    t.start()
            self.batch_recording_ongoing = False
            print("TRANSMIT ON")

    def find_player(self):
        self.level_name = BotUtils.detect_level_name()
        # Then grab the right rect for the level
        try:
            map_rect = BotUtils.string_to_rect(self.rects[self.level_name])
            self.speed = self.speeds[self.level_name]
        except:
            try:
                best_match = process.extractOne(
                    self.level_name, self.rects, score_cutoff=0.8)
                map_rect = self.string_to_rect(
                    self.rects[best_match])
                self.speed = self.speeds[best_match]
            except:
                map_rect = [362, 243, 1105, 748]
                self.speed = 30
        # Then open the map
        if not BotUtils.detect_bigmap_open(self.gamename):
            BotUtils.try_toggle_map()
        return BotUtils.grab_player_pos(self.gamename, map_rect)

    def on_release(self, key):
        if key == KeyCode(char='1'):
            pass
        elif key == KeyCode(char='2'):
            pass
        elif key == KeyCode(char='3'):
            pass
        elif key == KeyCode(char='4'):
            pass
        elif key == KeyCode(char='5'):
            pass
        elif key == KeyCode(char='6'):
            pass
        elif key == KeyCode(char='7'):
            pass
        elif key == KeyCode(char='8'):
            pass
        elif key == KeyCode(char='9'):
            pass
        elif self.autoloot_enabled and key == KeyCode(char='x'):
            pass
        elif self.transmitting:
            if GetWindowText(GetForegroundWindow()) == self.gamename:
                if not self.batch_recording_ongoing:
                    for server in self.list_servers:
                        server.send_message(str(key)+",up")
                else:
                    self.batch += str(key) + "|keyUp|" + \
                        "{:.3f}".format(
                            (time.time() - self.batch_start_time)) + "|0,0\n"
                try:
                    self.unreleased_keys.remove(str(key))
                except:
                    pass
                if len(self.batch) > 2500:
                    # need to first check if there are still keys pressed down
                    if len(self.unreleased_keys) == 0:
                        print("Sending batch now due to size")
                        self.batch_start_time = time.time()
                        # print(self.batch)
                        self.batch = ""

    def create_random_delays(self):
        for index, _ in enumerate(self.list_servers):
            self.delay_spread.append(
                self.delay_spacing + (index * self.delay_spacing * uniform(0.8, 1.2)))

    def send_batch(self, server, batch, index):
        delay = self.delay_spread[index]
        time.sleep(delay)
        if len(batch) > 1:
            server.send_message("batch,1\n"+batch)


class RHBotClient():
    def start(delay_spacing=12):
        list_ips = BotUtils.grab_online_servers()
        list_servers = []
        for ip in list_ips:
            list_servers.append(RHBotClientConnection(ip))
        ckl = ClientKeypressListener(
            list_servers, delay_spacing)
        ckl.start_mouse_listener()
        ckl.start_keypress_listener()

        with open("mainplayer.txt") as f:
            mainplayer = f.readline()
        BotUtils.start_server_threads(list_servers)
        time.sleep(0.25)
        for server in list_servers:
            server.send_message("mainplayer,"+mainplayer)
        while True:
            time.sleep(0.25)
            if ckl.batch_recording_ongoing:
                if time.time() > ckl.batch_start_time + 10:
                    if len(ckl.unreleased_keys) == 0:
                        ckl.batch_start_time = time.time()
                        for i, server in enumerate(list_servers):
                            t = threading.Thread(
                                target=ckl.send_batch, args=(server, ckl.batch, i))
                            t.start()
                        ckl.batch = ""


if __name__ == "__main__":
    RHBotClient.start()
