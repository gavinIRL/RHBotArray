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
from random import randint
import subprocess
import threading
import time
import os
from cryptography.fernet import Fernet

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
    def __init__(self, list_servers, test=False, delay_min=0, delay_spacing=5) -> None:
        self.test = test
        self.list_servers = list_servers
        self.listener = None
        self.unreleased_keys = []

        # Hotkey handling
        self.transmitting = True
        self.single_server = None
        self.delay_min = delay_min
        self.delay_spacing = delay_spacing
        if self.delay_min == 0:
            self.delay_enabled = False
        else:
            self.delay_enabled = True
        self.x_loot_only = True

        self.scaling = ClientUtils.get_monitor_scaling()
        # print("Scaling={}".format(self.scaling))
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        if not self.test:
            self.game_wincap = WindowCapture(self.gamename)

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
                    for server in self.list_servers:
                        server.send_message(
                            "click,"+str(xratio)+"|"+str(yratio))

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
        if key == keyboard.Key.f4:
            print("Exiting bot")
            for server in self.list_servers:
                server.delay = 0
                server.send_message("quit,1")
            os._exit(1)
        if self.transmitting:
            if key == keyboard.Key.f1:
                self.transmitting = False
                print("TRANSMIT OFF")
            elif key == keyboard.Key.f2:
                self.delay_enabled = not self.delay_enabled
                if self.delay_enabled:
                    for i, server in enumerate(self.list_servers):
                        server.delay = self.delay_min+i*self.delay_spacing
                    print("DELAY ON")
                else:
                    for server in self.list_servers:
                        server.delay = 0
                    print("DELAY OFF")
            elif key == keyboard.Key.f3:
                self.x_loot_only = not self.x_loot_only
                if self.x_loot_only:
                    for server in self.list_servers:
                        server.send_message("xlootonly,on")
                    print("LOOT ON")
                else:
                    for server in self.list_servers:
                        server.send_message("xlootonly,off")
                    print("LOOT OFF")
            elif GetWindowText(GetForegroundWindow()) == self.gamename:
                if str(key) not in self.unreleased_keys:
                    for server in self.list_servers:
                        server.send_message(str(key)+",down")
                    self.unreleased_keys.append(str(key))
        elif key == keyboard.Key.f1:
            self.transmitting = True
            self.delay_enabled = False
            for server in self.list_servers:
                server.delay = 0
            print("TRANSMIT ON")

    def on_release(self, key):
        if key == keyboard.Key.f1:
            pass
        elif key == keyboard.Key.f2:
            pass
        elif key == keyboard.Key.f3:
            pass
        elif self.transmitting:
            if GetWindowText(GetForegroundWindow()) == self.gamename:
                for server in self.list_servers:
                    server.send_message(str(key)+",up")
                self.unreleased_keys.remove(str(key))

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

    def start_server_thread(server):
        t = threading.Thread(target=server.main_loop(), daemon=True)
        t.start()

    def get_monitor_scaling():
        user32 = ctypes.windll.user32
        w_orig = GetSystemMetrics(0)
        user32.SetProcessDPIAware()
        [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        return float(("{:.2f}".format(w/w_orig)))


class RHBotClient():
    def start(delay_min=0, delay_spacing=5, test=False):
        list_ips = ClientUtils.grab_online_servers()
        list_servers = []
        for i, ip in enumerate(list_ips):
            if delay_min == 0:
                list_servers.append(RHBotClientConnection(ip))
            else:
                list_servers.append(RHBotClientConnection(
                    ip, delay_min+i*delay_spacing))
        ckl = ClientKeypressListener(
            list_servers, test, delay_min, delay_spacing)
        ckl.start_mouse_listener()
        ckl.start_keypress_listener()
        for server in list_servers:
            ClientUtils.start_server_thread(server)
        while True:
            time.sleep(1)


if __name__ == "__main__":
    RHBotClient.start(test=False)
