import socket
import select
import pydirectinput
import pyautogui
import time
import subprocess
import os
from win32api import GetSystemMetrics
from windowcapture import WindowCapture
import ctypes

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class ListenServerTest2():
    def __init__(self, print_only=False) -> None:
        self.print_only = print_only

        self.scaling = self.get_monitor_scaling()
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        if not self.print_only:
            self.game_wincap = WindowCapture(self.gamename)

        self.HEADER_LENGTH = 10
        self.IP = self.grab_current_lan_ip()
        self.PORT = 1351

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        self.sockets_list = [self.server_socket]
        self.clients = {}
        print(f'Listening for connections on {self.IP}:{self.PORT}...')

    def grab_current_lan_ip(self):
        output = subprocess.run(
            "ipconfig", capture_output=True).stdout.decode()
        _, output = output.split("IPv4 Address. . . . . . . . . . . : 192")
        output, _ = output.split("Subnet Mask")
        current_lan_ip = "192" + output.strip()
        return current_lan_ip

    def convert_pynput_to_pag(self, button):
        PYNPUT_SPECIAL_CASE_MAP = {
            'alt_l': 'altleft',
            'alt_r': 'altright',
            'alt_gr': 'altright',
            'caps_lock': 'capslock',
            'ctrl_l': 'ctrlleft',
            'ctrl_r': 'ctrlright',
            'page_down': 'pagedown',
            'page_up': 'pageup',
            'shift_l': 'shiftleft',
            'shift_r': 'shiftright',
            'num_lock': 'numlock',
            'print_screen': 'printscreen',
            'scroll_lock': 'scrolllock',
        }

        # example: 'Key.F9' should return 'F9', 'w' should return as 'w'
        cleaned_key = button.replace('Key.', '')

        if cleaned_key in PYNPUT_SPECIAL_CASE_MAP:
            return PYNPUT_SPECIAL_CASE_MAP[cleaned_key]

        return cleaned_key

    def convert_ratio_to_click(self, ratx, raty):
        # This will grab the current rectangle coords of game window
        # and then turn the ratio of positions versus the game window
        # into true x,y coords
        self.game_wincap.update_window_position(border=False)
        # Turn the ratios into relative
        relx = int(ratx * self.game_wincap.w)
        rely = int(raty * self.game_wincap.h)
        # Turn the relative into true
        truex = int((relx + self.game_wincap.window_rect[0]) * self.scaling)
        truey = int((rely + self.game_wincap.window_rect[1]) * self.scaling)
        return truex, truey

    def get_monitor_scaling(self):
        user32 = ctypes.windll.user32
        w_orig = GetSystemMetrics(0)
        user32.SetProcessDPIAware()
        [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        return float(("{:.2f}".format(w/w_orig)))

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(self.HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except:
            return False

    def start(self):
        while True:
            read_sockets, _, exception_sockets = select.select(
                self.sockets_list, [], self.sockets_list)
            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()
                    user = self.receive_message(client_socket)
                    if user is False:
                        continue
                    self.sockets_list.append(client_socket)
                    self.clients[client_socket] = user
                    print('Accepted new connection from {}:{}, username: {}'.format(
                        *client_address, user['data'].decode('utf-8')))
                # Else existing socket is sending a message
                else:
                    message = self.receive_message(notified_socket)
                    if message is False:
                        print('Closed connection from: {}'.format(
                            self.clients[notified_socket]['data'].decode('utf-8')))
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

                    if self.print_only:
                        print(message["data"].decode())
                    else:
                        button, direction = str(
                            message["data"].decode("utf-8")).split(",")
                        if button == "click":
                            xrat, yrat = direction.split("|")
                            # Need to convert from ratio to click
                            x, y = self.convert_ratio_to_click(xrat, yrat)
                            # and then click at that location
                            x = int(x/self.scaling)
                            y = int(y/self.scaling)
                            pydirectinput.click(x, y, duration=0.025)
                        elif button == "quit":
                            print("Shutting down server")
                            os._exit(1)
                        elif direction == "down":
                            key = self.convert_pynput_to_pag(
                                button.replace("'", ""))
                            print(key)
                            pyautogui.keyDown(key)
                        elif direction == "up":
                            key = self.convert_pynput_to_pag(
                                button.replace("'", ""))
                            pyautogui.keyUp(key)

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients[notified_socket]


if __name__ == "__main__":
    lst = ListenServerTest2(print_only=True)
    lst.start()
