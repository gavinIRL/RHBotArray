import socket
import select
import threading
import pydirectinput
import time
import subprocess
import os
from win32api import GetSystemMetrics
from windowcapture import WindowCapture
import ctypes
from cryptography.fernet import Fernet
from vision import Vision
from hsvfilter import grab_object_preset, HsvFilter
import cv2
import pytesseract
from quest_handle import QuestHandle
from sell_repair import SellRepair

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class RHBotArrayServer():
    def __init__(self, print_only=False, move_only=False) -> None:
        self.print_only = print_only
        self.move_only = move_only
        self.move_only_exclude_keys = ["a", "s", "d", "f", "g", "h"]

        self.scaling = self.get_monitor_scaling()
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        # initialise the window centre for the mouse resetter
        self.centre_x = 900
        self.centre_y = 500
        if not self.print_only:
            self.game_wincap = WindowCapture(self.gamename)
            self.centre_x = int(0.5 * self.game_wincap.w +
                                self.game_wincap.window_rect[0])
            self.centre_y = int(0.5 * self.game_wincap.h +
                                self.game_wincap.window_rect[1])

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

        with open("key.key") as f:
            key = f.read()
        self.fern = Fernet(key)

        self.last_mouse_move = time.time() - 10

        self.xprompt_filter, xprompt_custom_rect = grab_object_preset(
            object_name="prompt_press_x_pickup")
        self.xprompt_wincap = WindowCapture(
            self.gamename, xprompt_custom_rect)
        self.xprompt_vision = Vision("xprompt67filtv2.jpg")

        # These are related to the regroup command
        if not self.print_only:
            # These are related to auto playername detect
            plyrname_rect = [165, 45, 320, 65]
            self.plyrname_wincap = WindowCapture(self.gamename, plyrname_rect)
            self.plyrname_filt = HsvFilter(0, 0, 103, 89, 104, 255, 0, 0, 0, 0)
            self.plyrmname_vision = Vision('xprompt67filtv2.jpg')
            self.main_player = self.detect_name()
        with open("currplayer.txt") as f:
            self.curr_player = f.readline()
        self.regroup_wincap = WindowCapture(
            self.gamename, [210, 60, 1455, 650])
        self.regroup_vision = Vision('xprompt67filtv2.jpg')
        self.regroup_filter = HsvFilter(
            94, 188, 255, 137, 255, 255, 0, 0, 0, 0)

        # These are related to the autoloot function
        self.autoloot_enabled = False

        # These are related to the questhandling
        self.quest_handle = QuestHandle()

        # These are related to sell and repair
        self.sell_repair = SellRepair()

        # These are related to allow x in all cases
        self.allowx = False

    def move_mouse_centre(self):
        ctypes.windll.user32.SetCursorPos(self.centre_x, self.centre_y)

    def detect_name(self):
        # get an updated image of the game
        image = self.plyrname_wincap.get_screenshot()
        # pre-process the image
        image = self.plyrmname_vision.apply_hsv_filter(
            image, self.plyrname_filt)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        return results["text"][4]

    def grab_current_lan_ip(self):
        output = subprocess.run(
            "ipconfig", capture_output=True).stdout.decode()
        _, output = output.split("IPv4 Address. . . . . . . . . . . : 169")
        output, _ = output.split("Subnet Mask", maxsplit=1)
        current_lan_ip = "169" + output.strip()
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
        truex = int((relx + self.game_wincap.window_rect[0]))
        truey = int((rely + self.game_wincap.window_rect[1]))
        return truex, truey

    def get_relative_dists(self):
        # format is currplayer x, y, mainplayer x, y
        positions = [0, 0, 0, 0]
        # get an updated image of the game
        image = self.regroup_wincap.get_screenshot()
        # pre-process the image
        image = self.regroup_vision.apply_hsv_filter(
            image, self.regroup_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')

        no_find_curr = True
        no_find_main = True
        for i in range(0, len(results["text"])):
            if self.main_player in results["text"][i]:
                no_find_main = False
                positions[2] = results["left"][i] + (results["width"][i]/2)
                positions[3] = results["top"][i] + (results["height"][i]/2)
            elif self.curr_player in results["text"][i]:
                no_find_curr = False
                positions[0] = results["left"][i] + (results["width"][i]/2)
                positions[1] = results["top"][i] + (results["height"][i]/2)
        xrel = positions[2] - positions[0]
        yrel = positions[1] - positions[3]
        if no_find_curr or no_find_main:
            return False
        else:
            return[xrel, yrel]

    def move_towards(self, dir, dists):
        if dir == "x":
            dist = dists[0]
            if dist > 0:
                key = "left"
            else:
                key = "right"
        elif dir == "y":
            dist = dists[1]
            if dist > 0:
                key = "down"
            else:
                key = "up"
        if abs(dist) > 5:
            pydirectinput.keyDown(key)

    def resolve_direction(self, dir):
        if dir == "x":
            key1 = "left"
            key2 = "right"
            index = 0
        elif dir == "y":
            key1 = "down"
            key2 = "up"
            index = 1
        else:
            return False
        # grab the first relative distance values
        first_rel_dists = self.get_relative_dists()
        # if was able to detect both
        if first_rel_dists:
            # then start resolving the x direction
            start_time = time.time()
            self.move_towards(dir, first_rel_dists)
            move_time = time.time() - start_time()
            if not move_time < 0.1:
                time.sleep(0.1-move_time)
            for key in ["up", "down", "left", "right"]:
                pydirectinput.keyUp(key)
            end_time = time.time() - start_time()

            last_rel_dists = self.get_relative_dists()
            if not last_rel_dists:
                return False
            dist_moved = abs(last_rel_dists[index] - first_rel_dists[index])
            percent_moved = dist_moved / abs(first_rel_dists[index])
            if percent_moved > 1.1:
                # Need to reverse direction
                if first_rel_dists[index] > 0:
                    pydirectinput.keyDown(key1)
                    time.sleep((end_time-start_time)/percent_moved)
                    pydirectinput.keyUp(key1)
                else:
                    pydirectinput.keyDown(key2)
                    time.sleep((end_time-start_time)/percent_moved)
                    pydirectinput.keyUp(key2)
            elif percent_moved < 0.9:
                # Need to continue
                travel_time_reqd = (1-percent_moved)*(end_time-start_time)
                start_time = time.time()
                self.move_towards(dir, last_rel_dists)
                move_time = time.time() - start_time()
                if not move_time < travel_time_reqd:
                    time.sleep(travel_time_reqd-move_time)
                for key in ["up", "down", "left", "right"]:
                    pydirectinput.keyUp(key)

    def regroup(self):
        # first resolve the x direction
        self.resolve_direction("x")
        # and now resolve the y direction
        self.resolve_direction("y")

    def auto_loot(self):
        while self.autoloot_enabled:
            if self.loot_if_available():
                time.sleep(0.01)
                pydirectinput.keyUp("x")
                time.sleep(0.15)

    def autoloot_thread_start(self):
        t = threading.Thread(target=self.auto_loot, daemon=True)
        self.autoloot_enabled = True
        t.start()

    def loot_if_available(self):
        # get an updated image of the game at specified area
        xprompt_screenshot = self.xprompt_wincap.get_screenshot()
        # pre-process the image to help with detection
        xprompt_output_image = self.xprompt_vision.apply_hsv_filter(
            xprompt_screenshot, self.xprompt_filter)
        # do object detection, this time grab rectangles
        xprompt_rectangles = self.xprompt_vision.find(
            xprompt_output_image, threshold=0.61, epsilon=0.5)
        # then return answer to whether currently in dungeon
        if len(xprompt_rectangles) == 1:
            pydirectinput.keyDown("x")
            # keyup performed in main loop
            # return True for autoloot
            return True

    def get_monitor_scaling(self):
        user32 = ctypes.windll.user32
        w_orig = GetSystemMetrics(0)
        user32.SetProcessDPIAware()
        [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        return float(("{:.2f}".format(w/w_orig)))

    def batch_handle(self, lines: str):
        data = lines.split("\n")
        data.pop(0)
        converted = []
        # now convert each line into a list
        for line in data:
            converted.append(line.rstrip('\n').split("|"))
        # first sleep until the first action time
        # print(converted)
        time.sleep(float(converted[0][2]))
        for idx, line in enumerate(converted):
            action_start_time = time.time()
            # do the action
            if line[1] == "keyDown":
                # print("Would press {} down now".format(line[0]))
                pydirectinput.keyDown(line[0])
            elif line[1] == "keyUp":
                # print("Would press {} down now".format(line[0]))
                pydirectinput.keyUp(line[0])
            elif line[1] == "click":
                xrat, yrat = line[3].split(",")
                # print("Would click at {},{} now".format(x, y))
                x, y = self.convert_ratio_to_click(
                    float(xrat), float(yrat))
                x = int(x)
                y = int(y)
                # pydirectinput.click(x, y, duration=0.025)
                ctypes.windll.user32.SetCursorPos(x, y)
                if line[0] == "Button.left":
                    ctypes.windll.user32.mouse_event(
                        0x0002, 0, 0, 0, 0)
                    ctypes.windll.user32.mouse_event(
                        0x0004, 0, 0, 0, 0)
                elif line[0] == "Button.right":
                    ctypes.windll.user32.mouse_event(
                        0x0008, 0, 0, 0, 0)
                    ctypes.windll.user32.mouse_event(
                        0x0010, 0, 0, 0, 0)
            if line[1] == "questhandle":
                self.quest_handle.start_quest_handle()
            try:
                next_action = converted[idx + 1]
                if next_action[0] == "":
                    break
            except IndexError:
                # this was the last action in the list
                break
            elapsed_time = float(next_action[2]) - float(line[2])
            elapsed_time -= (time.time() - action_start_time)
            if elapsed_time < 0:
                elapsed_time = 0

            time.sleep(elapsed_time)

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
                    decrypted = self.fern.decrypt(message["data"])
                    self.do_message_checks(decrypted)

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients[notified_socket]

    def do_message_checks(self, decrypted: bytes):
        if self.print_only:
            print(decrypted.decode())
        else:
            if (time.time() - self.last_mouse_move) >= 10:
                self.move_mouse_centre()
                self.last_mouse_move = time.time()
            button, direction = str(
                decrypted.decode("utf-8")).split(",", 1)
            if button == "Button.left":
                xrat, yrat = direction.split("|")
                # Need to convert from ratio to click
                x, y = self.convert_ratio_to_click(
                    float(xrat), float(yrat))
                # and then click at that location
                x = int(x)
                y = int(y)
                # pydirectinput.click(x, y, duration=0.025)
                ctypes.windll.user32.SetCursorPos(x, y)
                ctypes.windll.user32.mouse_event(
                    0x0002, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(
                    0x0004, 0, 0, 0, 0)
            elif button == "Button.right":
                xrat, yrat = direction.split("|")
                x, y = self.convert_ratio_to_click(
                    float(xrat), float(yrat))
                x = int(x)
                y = int(y)
                ctypes.windll.user32.SetCursorPos(x, y)
                ctypes.windll.user32.mouse_event(
                    0x0008, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(
                    0x00010, 0, 0, 0, 0)
            elif button == "quit":
                print("Shutting down server")
                os._exit(1)
            elif button == "revive":
                pydirectinput.keyDown("x")
                time.sleep(0.1)
                pydirectinput.keyUp("x")
            elif button == "'x'":
                if self.allowx:
                    if direction == "down":
                        pydirectinput.keyDown("x")
                    else:
                        pydirectinput.keyUp("x")
                elif direction == "down":
                    self.loot_if_available()
                else:
                    pydirectinput.keyUp("x")
            elif button == "regroup":
                self.regroup()
            elif button == "autoloot":
                if direction == "on":
                    self.autoloot_thread_start()
                else:
                    self.autoloot_enabled = False
            elif button == "questhandle":
                self.quest_handle.start_quest_handle()
            elif button == "batch":
                self.batch_handle(direction)
            elif button == "sellrepair":
                self.sell_repair.ident_sell_repair()
            elif button == "mainplayer":
                self.main_player = direction
                print("Mainplayer={}".format(direction))
            elif button == "xallow":
                if direction == "1":
                    self.allowx = True
                else:
                    self.allowx = False
            elif direction == "down":
                key = self.convert_pynput_to_pag(
                    button.replace("'", ""))
                if self.move_only:
                    if button in self.move_only_exclude_keys:
                        pydirectinput.keyDown(key)
                else:
                    pydirectinput.keyDown(key)
            elif direction == "up":
                key = self.convert_pynput_to_pag(
                    button.replace("'", ""))
                if self.move_only:
                    if button in self.move_only_exclude_keys:
                        pydirectinput.keyUp(key)
                else:
                    pydirectinput.keyUp(key)


if __name__ == "__main__":
    lst = RHBotArrayServer(print_only=False)
    lst.start()
