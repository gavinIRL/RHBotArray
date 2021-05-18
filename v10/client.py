import socket
import select
import errno
import sys
from win32gui import GetWindowText, GetForegroundWindow
from win32api import GetSystemMetrics
from windowcapture import WindowCapture
import ctypes
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
from random import randint, random, uniform
import subprocess
import threading
import time
import os
from cryptography.fernet import Fernet
from quest_handle import QuestHandle
from sell_repair import SellRepair
from hsvfilter import HsvFilter
from vision import Vision
import cv2
import pytesseract

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
    def __init__(self, list_servers, test=False, delay_spacing=12) -> None:
        self.test = test
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

        self.scaling = ClientUtils.get_monitor_scaling()
        # print("Scaling={}".format(self.scaling))
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        if not self.test:
            self.game_wincap = WindowCapture(self.gamename)

        # These are for batch recording and sending
        self.batch_recording_ongoing = False
        self.batch_start_time = 0
        self.batch = ""
        self.delay_spread = []
        self.create_random_delays()

        # These are for the sell and repair logic
        self.sell_repair = SellRepair(last_row_protect=True)

        # These are for allowing x in all cases
        self.xallow = False

    def detect_name(self):
        plyrname_rect = [165, 45, 320, 65]
        plyrname_wincap = WindowCapture(self.gamename, plyrname_rect)
        plyrname_filt = HsvFilter(0, 0, 103, 89, 104, 255, 0, 0, 0, 0)
        plyrmname_vision = Vision('xprompt67filtv2.jpg')
        # get an updated image of the game
        image = plyrname_wincap.get_screenshot()
        # pre-process the image
        image = plyrmname_vision.apply_hsv_filter(
            image, plyrname_filt)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        biggest = 0
        for entry in results["text"]:
            if len(entry) > biggest:
                name = entry
                biggest = len(entry)
        return name

    def start_mouse_listener(self):
        if not self.test:
            self.mouse_listener = mouse.Listener(
                on_click=self.on_click)
        else:
            self.mouse_listener = mouse.Listener(
                on_click=self.on_click_test)
        self.mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        # First off need to check if transmitting is enabled
        if self.transmitting:
            # Need to then check if the click was in the right window
            # Do this by checking if window focused
            if GetWindowText(GetForegroundWindow()) == self.gamename:
                # when pressed is False, that means it's a release event.
                # let's listen only to mouse click releases
                if not pressed:
                    # Need to get the ratio compared to window top left
                    # This will allow common usage on other size monitors
                    # print("x={}, y={}".format(x, y))
                    xratio, yratio = self.convert_click_to_ratio(x, y)
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
            if not self.test:
                self.listener = Listener(on_press=self.on_press,
                                         on_release=self.on_release)
            else:
                self.listener = Listener(on_press=self.on_press_test,
                                         on_release=self.on_release_test)
            self.listener.start()

    def on_press(self, key):
        if key == KeyCode(char='0'):
            print("Exiting bot")
            for server in self.list_servers:
                server.delay = 0
                server.send_message("quit,1")
            os._exit(1)
        if self.transmitting:
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
                for server in self.list_servers:
                    server.send_message("revive,1")
                print("Reviving...")
            elif key == KeyCode(char='5'):
                for server in self.list_servers:
                    server.send_message("regroup,1")
                print("Regrouping...")
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
                for server in self.list_servers:
                    server.send_message("sellrepair,1")
                print("Selling and repairing...")
                self.sell_repair.ident_sell_repair()
            elif key == KeyCode(char='8'):
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

    def on_release(self, key):
        if key == KeyCode(char='1'):
            pass
        elif key == KeyCode(char='2'):
            pass
        elif key == KeyCode(char='3'):
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

    # def convert_ratio_to_click(self, ratx, raty):
    #     # This will grab the current rectangle coords of game window
    #     # and then turn the ratio of positions versus the game window
    #     # into true x,y coords
    #     self.game_wincap.update_window_position(border=False)
    #     # Turn the ratios into relative
    #     relx = int(ratx * self.game_wincap.w)
    #     rely = int(raty * self.game_wincap.h)
    #     # Turn the relative into true
    #     truex = int((relx + self.game_wincap.window_rect[0]))
    #     truey = int((rely + self.game_wincap.window_rect[1]))
    #     return truex, truey

    def create_random_delays(self):
        for index, _ in enumerate(self.list_servers):
            self.delay_spread.append(
                self.delay_spacing + (index * self.delay_spacing * uniform(0.6, 1.8)))

    def send_batch(self, server, batch, index):
        delay = self.delay_spread[index]
        time.sleep(delay)
        server.send_message("batch,1\n"+batch)

    def convert_click_to_ratio(self, truex, truey):
        # This will grab the current rectangle coords of game window
        # and then turn the click values into a ratio of positions
        # versus the game window
        self.game_wincap.update_window_position(border=False)
        # Turn the screen pos into window pos
        relx = (truex - self.game_wincap.window_rect[0]) * self.scaling
        rely = (truey - self.game_wincap.window_rect[1]) * self.scaling
        # print("relx={}, rely={}".format(relx, rely))
        # print("winx={}, winy={}".format(
        #     self.game_wincap.window_rect[0], self.game_wincap.window_rect[1]))
        # print("winwidth={}".format(self.game_wincap.w))
        # Then convert to a ratio
        ratx = relx/(self.game_wincap.w*self.scaling)
        raty = rely/(self.game_wincap.h*self.scaling)
        # Test convert back to a click
        # convx, convy = self.convert_ratio_to_click(ratx, raty)
        # print("convx={}, convy={}".format(convx, convy))
        return ratx, raty

    def on_click_test(self, x, y, button, pressed):
        # when pressed is False, that means it's a release event.
        # let's listen only to mouse click releases
        if self.transmitting:
            if not pressed:
                # Need to get the ratio compared to window top left
                # This will allow common usage on other size monitors
                # xratio, yratio = self.convert_click_to_ratio(x, y)
                for server in self.list_servers:
                    server.send_message("click,"+str(x)+"|"+str(y))

    def on_press_test(self, key):
        if key == keyboard.Key.f4:
            print("Exiting bot")
            for server in self.list_servers:
                server.delay = 0
                server.send_message("quit,1")
            os._exit(1)
        if self.transmitting:
            if str(key) not in self.unreleased_keys:
                for server in self.list_servers:
                    server.send_message(str(key)+",down")
                self.unreleased_keys.append(str(key))

    def on_release_test(self, key):
        if self.transmitting:
            for server in self.list_servers:
                server.send_message(str(key)+",up")
            self.unreleased_keys.remove(str(key))


class ClientUtils():
    def grab_online_servers():
        output = subprocess.run("arp -a", capture_output=True).stdout.decode()
        list_ips = []
        with open("servers.txt", "r") as f:
            lines = f.readlines()
            for ip in lines:
                if ip.strip() in output:
                    list_ips.append(ip.strip())
        return list_ips

    def start_server_threads(list_servers):
        for server in list_servers:
            t = threading.Thread(target=server.main_loop)
            t.start()

    def get_monitor_scaling():
        user32 = ctypes.windll.user32
        w_orig = GetSystemMetrics(0)
        user32.SetProcessDPIAware()
        [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        return float(("{:.2f}".format(w/w_orig)))


class RHBotClient():
    def start(delay_spacing=12, test=False):
        list_ips = ClientUtils.grab_online_servers()
        list_servers = []
        for ip in list_ips:
            list_servers.append(RHBotClientConnection(ip))
        ckl = ClientKeypressListener(
            list_servers, test, delay_spacing)
        ckl.start_mouse_listener()
        ckl.start_keypress_listener()

        with open("mainplayer.txt") as f:
            mainplayer = f.readline()
        try:
            mainplayer = ckl.detect_name()
        except:
            pass
        # for server in list_servers:
        ClientUtils.start_server_threads(list_servers)
        print("Got to here")
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
    RHBotClient.start(test=False)
