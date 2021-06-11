from re import S
import socket
import select
import threading
from v12.rhba_utils import BotUtils, Events
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
import numpy as np
from fuzzywuzzy import process
from custom_input import CustomInput

# Change directory to current file location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Required code for custom input
SendInput = ctypes.windll.user32.SendInput
MapVirtualKey = ctypes.windll.user32.MapVirtualKeyW
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_UNICODE = 0x0004
MAPVK_VK_TO_CHAR = 2
MAPVK_VK_TO_VSC = 0
MAPVK_VSC_TO_VK = 1
MAPVK_VSC_TO_VK_EX = 3
# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


class RHBotArrayServer():
    def __init__(self, print_only=False, move_only=False) -> None:
        self.print_only = print_only
        self.move_only = move_only
        self.move_only_exclude_keys = ["a", "s", "d", "f", "g", "h"]

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

        # These are related to the v1 regroup command
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

        # These are for the v2 regroup command
        self.map_rect = None
        self.level_name = None
        self.speed = 20
        self.rects = {}
        self.speeds = {}
        self.num_names = []
        self.load_level_rects()
        self.key_map = self.load_key_dict()
        self.player_pos = None
        self.regroup_try_count = 0

        # This is for the pag vs custom input town mode
        # False means custom mode, true means pag
        self.inputmode = False

        # This is for follow mode
        self.followmode = False

    def try_toggle_map(self):
        # pydirectinput.keyDown("m")
        CustomInput.press_key(CustomInput.key_map["m"])
        time.sleep(0.05)
        # pydirectinput.keyUp("m")
        CustomInput.release_key(CustomInput.key_map["m"])
        time.sleep(0.08)

    def string_to_rect(self, string: str):
        return [int(i) for i in string.split(',')]

    def load_level_rects(self):
        # Load the translation from name to num
        with open("lvl_name_num.txt") as f:
            self.num_names = f.readlines()
        for i, entry in enumerate(self.num_names):
            self.num_names[i] = entry.split("-")
        # Load the num to rect catalogue
        with open("catalogue.txt") as f:
            nums_rects = f.readlines()
        for i, entry in enumerate(nums_rects):
            nums_rects[i] = entry.split("-")
        # Finally load the level speeds
        with open("lvl_speed.txt") as f:
            num_speeds = f.readlines()
        for i, entry in enumerate(num_speeds):
            num_speeds[i] = entry.split("|")
        # Then add each rect to the rects dict against name
        # Also add each speed to the speed dict against name
        for number, name in self.num_names:
            for num, area, rect in nums_rects:
                if area == "FM" and num == number:
                    self.rects[name.rstrip().replace(" ", "")] = rect.rstrip()
                    if "1" in name:
                        self.rects[name.rstrip().replace(
                            " ", "").replace("1", "L")] = rect.rstrip()
                    if "ri" in name:
                        self.rects[name.rstrip().replace(
                            " ", "").replace("ri", "n").replace("1", "L")] = rect.rstrip()
                    break
            for num, speed in num_speeds:
                if num == number:
                    self.speeds[name.rstrip().replace(
                        " ", "")] = float(speed.rstrip())
                    if "1" in name:
                        self.speeds[name.rstrip().replace(
                            " ", "").replace("1", "L")] = float(speed.rstrip())
                    if "ri" in name:
                        self.speeds[name.rstrip().replace(
                            " ", "").replace("ri", "n").replace("1", "L")] = float(speed.rstrip())
                    break

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
        str_list = filter(None, results["text"])
        with open("mainplayer.txt") as f:
            longest = f.readline()
        # try:
        #     longest = max(str_list, key=len)
        # except:
        #     with open("mainplayer.txt") as f:
        #         longest = f.readline()
        return longest

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
        print(self.main_player)
        print(self.curr_player)
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
            # pydirectinput.keyDown(key)
            CustomInput.press_key(CustomInput.key_map[key], key)

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
            move_time = time.time() - start_time
            if move_time < 0.05:
                time.sleep(0.05-move_time)
            for key in ["up", "down", "left", "right"]:
                # pydirectinput.keyUp(key)
                CustomInput.release_key(CustomInput.key_map[key], key)
            end_time = time.time() - start_time

            last_rel_dists = self.get_relative_dists()
            if not last_rel_dists:
                return False
            dist_moved = abs(last_rel_dists[index] - first_rel_dists[index])
            percent_moved = dist_moved / abs(first_rel_dists[index])
            if percent_moved > 1.1:
                # Need to reverse direction
                if first_rel_dists[index] > 0:
                    # pydirectinput.keyDown(key1)
                    CustomInput.press_key(CustomInput.key_map[key1], key1)
                    time.sleep((end_time)/percent_moved)
                    # pydirectinput.keyUp(key1)
                    CustomInput.release_key(CustomInput.key_map[key1], key1)
                else:
                    # pydirectinput.keyDown(key2)
                    CustomInput.press_key(CustomInput.key_map[key2], key2)
                    time.sleep((end_time)/percent_moved)
                    # pydirectinput.keyUp(key2)
                    CustomInput.release_key(CustomInput.key_map[key2], key2)
            elif percent_moved < 0.9:
                # Need to continue
                travel_time_reqd = (1-percent_moved)*(end_time)
                start_time = time.time()
                self.move_towards(dir, last_rel_dists)
                move_time = time.time() - start_time
                if move_time < travel_time_reqd:
                    time.sleep(travel_time_reqd-move_time)
                for key in ["up", "down", "left", "right"]:
                    # pydirectinput.keyUp(key)
                    CustomInput.release_key(CustomInput.key_map[key], key)

    def regroup(self):
        # first resolve the x direction
        self.resolve_direction("x")
        # and now resolve the y direction
        self.resolve_direction("y")

    def auto_loot(self):
        consec_xpress = 0
        while self.autoloot_enabled:
            if self.loot_if_available():
                consec_xpress += 1
                if not consec_xpress > 6:
                    time.sleep(0.01)
                    # pydirectinput.keyUp("x")
                    CustomInput.release_key(CustomInput.key_map["x"])
                    time.sleep(0.225)
                else:
                    time.sleep(0.4)
            else:
                time.sleep(0.1)
                consec_xpress = 0

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
            CustomInput.press_key(CustomInput.key_map["x"])
            # pydirectinput.keyDown("x")
            # keyup performed in main loop
            # return True for autoloot
            return True

    def batch_handle(self, lines: str):
        data = lines.split("\n")
        data.pop(0)
        converted = []
        # now convert each line into a list
        for line in data:
            converted.append(line.rstrip('\n').split("|"))
        # first sleep until the first action time
        # print(converted)
        try:
            time.sleep(float(converted[0][2]))
            for idx, line in enumerate(converted):
                action_start_time = time.time()
                # do the action
                if line[1] == "keyDown":
                    # print("Would press {} down now".format(line[0]))
                    k = self.convert_pynput_to_pag(line[0].strip("'"))
                    pydirectinput.keyDown(k)
                    # self.press_key(self.key_map[k], k)
                elif line[1] == "keyUp":
                    # print("Would press {} down now".format(line[0]))
                    k = self.convert_pynput_to_pag(line[0].strip("'"))
                    pydirectinput.keyUp(k)
                    # self.press_key(self.key_map[k], k)
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
                        pydirectinput.rightClick(duration=0.01)
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
        except:
            # This will only occur if there is an empty batch
            pass

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
                time.sleep(0.03)
                ctypes.windll.user32.mouse_event(
                    0x00010, 0, 0, 0, 0)
            elif button == "quit":
                print("Shutting down server")
                os._exit(1)
            elif button == "mainplayer":
                self.curr_player = direction
                print("Admin player name is "+direction)
            elif button == "'x'":
                if self.allowx:
                    if direction == "down":
                        if self.inputmode:
                            pydirectinput.keyDown("x")
                        else:
                            CustomInput.press_key(CustomInput.key_map["x"])
                    else:
                        if self.inputmode:
                            pydirectinput.keyUp("x")
                        else:
                            CustomInput.release_key(CustomInput.key_map["x"])
                elif direction == "down":
                    self.loot_if_available()
                else:
                    if self.inputmode:
                        pydirectinput.keyUp("x")
                    else:
                        CustomInput.release_key(CustomInput.key_map["x"])
            elif button == "regroup":
                self.regroup(direction)
            elif button == "autoloot":
                if direction == "on":
                    self.autoloot_thread_start()
                else:
                    self.autoloot_enabled = False
            elif button == "inputmode":
                if direction == "1":
                    self.inputmode = True
                else:
                    self.inputmode = False
            elif button == "questhandle":
                self.quest_handle.start_quest_handle()
            elif button == "batch":
                self.batch_handle(direction)
            elif button == "clearall":
                BotUtils.close_map_and_menu(self.gamename)
            elif button == "sellrepair":
                os.popen('python sell_repair.py')
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
                        if self.inputmode:
                            pydirectinput.keyDown(key)
                        else:
                            CustomInput.press_key(
                                CustomInput.key_map[key], key)
                else:
                    if self.inputmode:
                        pydirectinput.keyDown(key)
                    else:
                        CustomInput.press_key(CustomInput.key_map[key], key)
            elif direction == "up":
                key = self.convert_pynput_to_pag(
                    button.replace("'", ""))
                if self.move_only:
                    if button in self.move_only_exclude_keys:
                        if self.inputmode:
                            pydirectinput.keyUp(key)
                        else:
                            CustomInput.release_key(
                                CustomInput.key_map[key], key)
                else:
                    if self.inputmode:
                        pydirectinput.keyUp(key)
                    else:
                        CustomInput.release_key(CustomInput.key_map[key], key)

    def pre_regroup_updates(self, x, y):
        self.level_name = BotUtils.detect_level_name(self.gamename)
        # Then grab the right rect for the level
        try:
            self.map_rect = self.string_to_rect(self.rects[self.level_name])
            self.speed = self.speeds[self.level_name]
        except:
            try:
                best_match = process.extractOne(
                    self.level_name, self.rects, score_cutoff=0.8)
                self.map_rect = self.string_to_rect(
                    self.rects[best_match])
                self.speed = self.speeds[best_match]
            except:
                self.map_rect = [362, 243, 1105, 748]
                self.speed = 30
        # Then open the map
        if not BotUtils.detect_bigmap_open():
            BotUtils.try_toggle_map()
        self.player_pos = BotUtils.grab_player_pos(
            self.gamename, [x-100, y-100, x+100, y+100])

    def regroup(self, coords: str):
        x, y = coords.split("|")
        # first perform the pre-regroup updates
        self.pre_regroup_updates(int(x), int(y))
        # Then calculate the relative positions
        try:
            relx = self.player_pos[0] - int(x)
            rely = int(y) - self.player_pos[1]
            BotUtils.move_diagonal(self.gamename, relx,
                                   rely, 90, self.speed, True)
        except:
            if self.regroup_try_count < 2:
                self.regroup_try_count += 1
                key = "right"
                CustomInput.press_key(CustomInput.key_map[key])
                CustomInput.release_key(CustomInput.key_map[key])
                self.regroup(coords)
        # Finally close the map
        # if self.detect_bigmap_open():
        #     self.try_toggle_map()
        self.player_pos = [0, 0]
        self.regroup_try_count = 0

    def create_follower_thread(self):
        t = threading.Thread(target=self.follower)
        t.start()

    def follower(self):
        dung_cap = WindowCapture(self.gamename, [1090, 331, 1092, 353])
        detect_count = 0
        while self.followmode:
            if Events.detect_in_dungeon(dung_cap):
                loc = BotUtils.find_other_player(self.gamename)
                if loc:
                    BotUtils.navigate_towards(loc)
                    detect_count += 1
                elif detect_count > 0:
                    detect_count -= 1
                else:
                    BotUtils.stop_movement()
            time.sleep(0.005)
        BotUtils.stop_movement()

    def create_support_thread(self):
        t = threading.Thread(target=self.support_MS)
        t.start()

    def support_MS(self):
        while self.followmode:
            for key in ["h", "a", "f", "s"]:
                CustomInput.press_key(CustomInput.key_map[key])
                CustomInput.release_key(CustomInput.key_map[key])
            time.sleep(0.005)

    def create_revive_thread(self):
        t = threading.Thread(target=self.auto_revive)
        t.start()

    def auto_revive(self):
        dung_cap = WindowCapture(self.gamename, [1090, 331, 1092, 353])
        while True:
            try:
                if Events.detect_in_dungeon(dung_cap):
                    if Events.detect_resurrect_prompt(self.gamename):
                        CustomInput.press_key(CustomInput.key_map["x"])
                        CustomInput.release_key(CustomInput.key_map["x"])
            except:
                time.sleep(2)


if __name__ == "__main__":
    lst = RHBotArrayServer(print_only=False)
    lst.start()
