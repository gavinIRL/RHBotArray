import os
import cv2
import time
import math
import ctypes
import random
import win32ui
import win32gui
import warnings
import win32con
import threading
import subprocess
import pytesseract
import numpy as np
import pydirectinput
from fuzzywuzzy import process
from custom_input import CustomInput
from win32api import GetSystemMetrics
os.chdir(os.path.dirname(os.path.abspath(__file__)))
warnings.simplefilter("ignore", DeprecationWarning)


class HsvFilter:
    def __init__(self, hMin=None, sMin=None, vMin=None, hMax=None, sMax=None, vMax=None,
                 sAdd=None, sSub=None, vAdd=None, vSub=None):
        self.hMin = hMin
        self.sMin = sMin
        self.vMin = vMin
        self.hMax = hMax
        self.sMax = sMax
        self.vMax = vMax
        self.sAdd = sAdd
        self.sSub = sSub
        self.vAdd = vAdd
        self.vSub = vSub


class WindowCapture:
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    def __init__(self, window_name=None, custom_rect=None):
        self.custom_rect = custom_rect
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        # Declare all the class variables
        self.w, self.h, self.cropped_x, self.cropped_y
        self.offset_x, self.offset_y
        self.update_window_position()

    def get_screenshot(self):
        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj,
                   (self.cropped_x, self.cropped_y), win32con.SRCCOPY)
        # convert the raw data into a format opencv can read
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)
        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        # drop the alpha channel
        img = img[..., :3]
        # make image C_CONTIGUOUS
        img = np.ascontiguousarray(img)

        return img

    def focus_window(self):
        win32gui.SetForegroundWindow(self.hwnd)

    def update_window_position(self, border=True):
        self.window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = self.window_rect[2] - self.window_rect[0]
        self.h = self.window_rect[3] - self.window_rect[1]
        border_pixels = 8
        titlebar_pixels = 30
        if self.custom_rect is None:
            if border:
                self.w = self.w - (border_pixels * 2)
                self.h = self.h - titlebar_pixels - border_pixels
                self.cropped_x = border_pixels
                self.cropped_y = titlebar_pixels
            else:
                self.cropped_x = 0
                self.cropped_y = 0
                self.w += 3
        else:
            self.w = self.custom_rect[2] - self.custom_rect[0]
            self.h = self.custom_rect[3] - self.custom_rect[1]
            self.cropped_x = self.custom_rect[0]
            self.cropped_y = self.custom_rect[1]
        self.offset_x = self.window_rect[0] + self.cropped_x
        self.offset_y = self.window_rect[1] + self.cropped_y

    # WARNING: need to call the update_window_position function to prevent errors
    # That would come from moving the window after starting the bot
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)


class BotUtils:
    def grab_online_servers():
        output = subprocess.run("arp -a", capture_output=True).stdout.decode()
        list_ips = []
        with open("servers.txt", "r") as f:
            lines = f.readlines()
            for ip in lines:
                if ip.strip() in output:
                    list_ips.append(ip.strip())
        return list_ips

    def grab_current_lan_ip():
        output = subprocess.run(
            "ipconfig", capture_output=True).stdout.decode()
        _, output = output.split("IPv4 Address. . . . . . . . . . . : 169")
        output, _ = output.split("Subnet Mask", maxsplit=1)
        current_lan_ip = "169" + output.strip()
        return current_lan_ip

    def start_server_threads(list_servers):
        for server in list_servers:
            t = threading.Thread(target=server.main_loop)
            t.start()

    def grab_closest(rel_list: list):
        closest_index = False
        smallest_dist = 100000
        for i, pair in enumerate(rel_list):
            x = abs(pair[0])
            y = abs(pair[1])
            hypot = math.hypot(x, y)
            if hypot < smallest_dist:
                smallest_dist = hypot
                closest_index = i
        return closest_index

    def grab_order_closeness(relatives):
        dists = []
        for x, y in relatives:
            dists.append(math.hypot(x, y))
        return sorted(range(len(dists)), key=dists.__getitem__)

    def grab_order_lowest_y(coords):
        y_only = []
        for _, y in coords:
            y_only.append(y)
        return sorted(range(len(y_only)), key=y_only.__getitem__)

    # Angle is left->right travel of room angle, north being 0deg
    def move_diagonal(gamename, x, y, angle=90, speed=20, rel=False):
        # If not a direct relative move command
        if not rel:
            if not BotUtils.detect_bigmap_open(gamename):
                BotUtils.try_toggle_map()
            player_pos = BotUtils.grab_player_pos(gamename)
            start_time = time.time()
            while not player_pos:
                time.sleep(0.05)
                if not BotUtils.detect_bigmap_open(gamename):
                    BotUtils.try_toggle_map()
                time.sleep(0.05)
                player_pos = BotUtils.grab_player_pos(gamename)
                if time.time() - start_time > 5:
                    print("Error with finding player")
                    os._exit(1)
            BotUtils.close_map_and_menu(gamename)
            relx = player_pos[0] - int(x)
            rely = int(y) - player_pos[1]
            while abs(relx) > 100 or abs(rely > 100):
                CustomInput.press_key(CustomInput.key_map["right"], "right")
                CustomInput.release_key(CustomInput.key_map["right"], "right")
                time.sleep(0.02)
                player_pos = BotUtils.grab_player_pos(gamename)
                relx = player_pos[0] - int(x)
                rely = int(y) - player_pos[1]
        # Otherwise treat x,y as direct commands
        else:
            relx = x
            rely = y
        mult = 0.707
        if relx > 0:
            keyx = "left"
            CustomInput.press_key(CustomInput.key_map["left"], "left")
            timeleftx = float("{:.4f}".format(abs(relx/(speed*mult))))
        elif relx < 0:
            keyx = "right"
            CustomInput.press_key(CustomInput.key_map["right"], "right")
            timeleftx = float("{:.4f}".format(abs(relx/(speed*mult))))
        else:
            timeleftx = 0
            mult = 1
        if rely > 0:
            keyy = "down"
            CustomInput.press_key(CustomInput.key_map["down"], "down")
            timelefty = float("{:.4f}".format(abs(rely/(speed*mult))))
        elif rely < 0:
            keyy = "up"
            CustomInput.press_key(CustomInput.key_map["up"], "up")
            timelefty = float("{:.4f}".format(abs(rely/(speed*mult))))
        else:
            timelefty = 0
            if relx != 0:
                timeleftx = float("{:.4f}".format(abs(relx/speed)))
        first_sleep = min([timeleftx, timelefty])
        second_sleep = max([timeleftx, timelefty])
        first_key = [keyx, keyy][[timeleftx, timelefty].index(first_sleep)]
        second_key = [keyx, keyy][[timeleftx, timelefty].index(second_sleep)]
        if first_sleep < 0.009:
            if second_sleep < 0.009:
                pass
            else:
                time.sleep(second_sleep-0.009)
                CustomInput.release_key(
                    CustomInput.key_map[second_key], second_key)
        elif timelefty == timeleftx:
            time.sleep(first_sleep-0.009)
            CustomInput.release_key(CustomInput.key_map[first_key], first_key)
            CustomInput.release_key(
                CustomInput.key_map[second_key], second_key)
        else:
            time.sleep(first_sleep - 0.009)
            CustomInput.release_key(CustomInput.key_map[first_key], first_key)
            time.sleep((second_sleep-first_sleep-0.009)*mult)
            CustomInput.release_key(
                CustomInput.key_map[second_key], second_key)

    def move_towards(value, dir):
        if dir == "x":
            if value > 0:
                key = "left"
            else:
                key = "right"
        elif dir == "y":
            if value > 0:
                key = "down"
            else:
                key = "up"
        CustomInput.press_key(CustomInput.key_map[key], key)

    def move_to(gamename, x, y, angle=90, yfirst=True, speed=22.5, loot=False, plyr=False, rel=False):
        if not rel:
            if not BotUtils.detect_bigmap_open(gamename):
                BotUtils.try_toggle_map()
            player_pos = BotUtils.grab_player_pos(gamename)
            start_time = time.time()
            while not player_pos:
                time.sleep(0.05)
                if not BotUtils.detect_bigmap_open(gamename):
                    BotUtils.try_toggle_map()
                time.sleep(0.05)
                player_pos = BotUtils.grab_player_pos(gamename)
                if time.time() - start_time > 5:
                    print("Error with finding player")
                    os._exit(1)
            BotUtils.close_map_and_menu(gamename)
            relx = player_pos[0] - int(x)
            rely = int(y) - player_pos[1]
            while abs(relx) > 100 or abs(rely > 100):
                CustomInput.press_key(CustomInput.key_map["right"], "right")
                CustomInput.release_key(CustomInput.key_map["right"], "right")
                time.sleep(0.02)
                player_pos = BotUtils.grab_player_pos(gamename)
                relx = player_pos[0] - int(x)
                rely = int(y) - player_pos[1]
        else:
            relx = x
            rely = y
        if not yfirst:
            if not loot:
                BotUtils.resolve_dir_v2(relx, "x", speed)
                BotUtils.resolve_dir_v2(rely, "y", speed)
            else:
                lootfound = BotUtils.resolve_dir_with_looting(
                    relx, "x", speed, gamename)
                if lootfound:
                    Looting.grab_all_visible_loot(gamename, plyr)
                    # Continue to destination without further looting (prevent stuck)
                    BotUtils.move_to(gamename, x, y, angle, yfirst, speed)
                    # When at destination check for loot again
                    if Looting.check_for_loot(gamename):
                        Looting.grab_all_visible_loot(gamename, plyr)
                        # If needs be return to destination
                        BotUtils.move_to(gamename, x, y, angle, yfirst, speed)
                else:
                    lootfound = BotUtils.resolve_dir_with_looting(
                        rely, "y", speed, gamename)
                    if lootfound:
                        Looting.grab_all_visible_loot(gamename, plyr)
                        # Continue to destination without further looting (prevent stuck)
                        BotUtils.move_to(gamename, x, y, angle, yfirst, speed)
                        # When at destination check for loot again
                        if Looting.check_for_loot(gamename):
                            Looting.grab_all_visible_loot(gamename, plyr)
                            # If needs be return to destination
                            BotUtils.move_to(
                                gamename, x, y, angle, yfirst, speed)
        else:
            if not loot:
                BotUtils.resolve_dir_v2(rely, "y", speed)
                BotUtils.resolve_dir_v2(relx, "x", speed)
            else:
                lootfound = BotUtils.resolve_dir_with_looting(
                    rely, "y", speed, gamename)
                if lootfound:
                    Looting.grab_all_visible_loot(gamename, plyr)
                    # Continue to destination without further looting (prevent stuck)
                    BotUtils.move_to(gamename, x, y, angle, yfirst, speed)
                    # When at destination check for loot again
                    if Looting.check_for_loot(gamename):
                        Looting.grab_all_visible_loot(gamename, plyr)
                        # If needs be return to destination
                        BotUtils.move_to(gamename, x, y, angle, yfirst, speed)
                else:
                    lootfound = BotUtils.resolve_dir_with_looting(
                        relx, "x", speed, gamename)
                    if lootfound:
                        Looting.grab_all_visible_loot(gamename, plyr)
                        # Continue to destination without further looting (prevent stuck)
                        BotUtils.move_to(gamename, x, y, angle, yfirst, speed)
                        # When at destination check for loot again
                        if Looting.check_for_loot(gamename):
                            Looting.grab_all_visible_loot(gamename, plyr)
                            # If needs be return to destination
                            BotUtils.move_to(
                                gamename, x, y, angle, yfirst, speed)

    def resolve_dir_v2(value, dir, speed):
        if dir == "x":
            if value > 0:
                key = "left"
            else:
                key = "right"
        elif dir == "y":
            if value > 0:
                key = "down"
            else:
                key = "up"
        time_reqd = abs(value/speed)
        if time_reqd > 0.003:
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(time_reqd-0.003)
            CustomInput.release_key(CustomInput.key_map[key], key)

    def resolve_dir_with_looting(value, dir, speed, gamename):
        if dir == "x":
            if value > 0:
                key = "left"
            else:
                key = "right"
        elif dir == "y":
            if value > 0:
                key = "down"
            else:
                key = "up"
        time_reqd = abs(value/speed)
        start_time = time.time()
        if time_reqd > 0.003:
            CustomInput.press_key(CustomInput.key_map[key], key)
            # Maximum lootcheck time is about 0.3secs worst case
            # Nominal is about 0.2s
            if time_reqd < 2:
                time.sleep(time_reqd-0.003)
                CustomInput.release_key(CustomInput.key_map[key], key)
            else:
                BotUtils.close_map(gamename)
                loops = math.floor(time_reqd/2)
                for i in range(loops):
                    time.sleep(1.65)
                    result = Looting.check_for_loot(gamename)
                    if result:
                        CustomInput.release_key(CustomInput.key_map[key], key)
                        return True
                time_left = start_time+time_reqd-time.time()
                time.sleep(time_left)
                CustomInput.release_key(CustomInput.key_map[key], key)
        return Looting.check_for_loot(gamename)

    def resolve_single_direction(speed, value, dir, PAG=False):
        if not PAG:
            sleep_time = 0.003
        else:
            sleep_time = 0.1
        if dir == "x":
            if value > 0:
                key = "left"
            else:
                key = "right"
        elif dir == "y":
            if value > 0:
                key = "down"
            else:
                key = "up"
        time_reqd = abs(value/speed)
        key_map = CustomInput.grab_key_dict()
        if not PAG:
            CustomInput.press_key(key_map[key], key)
        else:
            pydirectinput.keyDown(key)
        try:
            time.sleep(time_reqd-sleep_time)
        except:
            pass
        if not PAG:
            CustomInput.release_key(key_map[key], key)
        else:
            pydirectinput.keyDown(key)

    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    def grab_hpbar_locations(gamename=False):
        if gamename:
            wincap = WindowCapture(gamename, [100, 135, 1223, 688])
            original_image = wincap.get_screenshot()
        else:
            original_image = cv2.imread(os.path.dirname(
                os.path.abspath(__file__)) + "/testimages/healthbars.jpg")
        filter = HsvFilter(20, 174, 245, 26, 193, 255, 0, 0, 0, 0)
        output_image = BotUtils.filter_blackwhite_invert(
            filter, original_image, True)
        output_image = cv2.blur(output_image, (2, 2))
        _, thresh = cv2.threshold(output_image, 127, 255, 0)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        if len(contours) < 2:
            return False
        contours.pop(0)
        rectangles = []
        for contour in contours:
            (x, y), _ = cv2.minEnclosingCircle(contour)
            rectangles.append([x-10, y, 20, 5])
            rectangles.append([x-10, y, 20, 5])
        rectangles, _ = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=0.8)
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def grab_character_location(player_name, gamename=False):
        player_chars = "".join(set(player_name))
        if gamename:
            wincap = WindowCapture(gamename, [200, 235, 1123, 688])
            original_image = wincap.get_screenshot()
        else:
            original_image = cv2.imread(os.path.dirname(
                os.path.abspath(__file__)) + "/testimages/test_sensitive.jpg")
        filter = HsvFilter(0, 0, 119, 179, 49, 255, 0, 0, 0, 0)
        output_image = BotUtils.filter_blackwhite_invert(
            filter, original_image, return_gray=True)
        rgb = cv2.cvtColor(output_image, cv2.COLOR_GRAY2RGB)
        tess_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=' + player_chars
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng', config=tess_config)
        try:
            best_match, _ = process.extractOne(
                player_name, results["text"], score_cutoff=0.8)
            i = results["text"].index(best_match)
            x = int(results["left"][i] + (results["width"][i]/2))
            y = int(results["top"][i] + (results["height"][i]/2))
            # Account for the rect
            x += 200
            y += 235
            return x, y
        except:
            return False, False

    def shift_channel(c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c

    def filter_blackwhite_invert(filter: HsvFilter, existing_image, return_gray=False, threshold=67, max=255):
        hsv = cv2.cvtColor(existing_image, cv2.COLOR_BGR2HSV)
        hsv_filter = filter
        # add/subtract saturation and value
        h, s, v = cv2.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
        hsv = cv2.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR
        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
        # now change it to greyscale
        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # now change it to black and white
        (thresh, blackAndWhiteImage) = cv2.threshold(
            grayImage, threshold, max, cv2.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        if return_gray:
            return inverted
        inverted = cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)
        return inverted

    def convert_pynput_to_pag(button):
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

    def detect_player_name(gamename):
        plyrname_rect = [165, 45, 320, 65]
        plyrname_wincap = WindowCapture(gamename, plyrname_rect)
        plyrname_filt = HsvFilter(0, 0, 103, 89, 104, 255, 0, 0, 0, 0)
        # get an updated image of the game
        image = plyrname_wincap.get_screenshot()
        # pre-process the image
        image = BotUtils.apply_hsv_filter(
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

    def detect_level_name(gamename):
        wincap = WindowCapture(gamename, [1121, 31, 1248, 44])
        existing_image = wincap.get_screenshot()
        filter = HsvFilter(0, 0, 0, 169, 34, 255, 0, 0, 0, 0)
        save_image = BotUtils.apply_hsv_filter(existing_image, filter)
        gray_image = cv2.cvtColor(save_image, cv2.COLOR_BGR2GRAY)
        (thresh, blackAndWhiteImage) = cv2.threshold(
            gray_image, 129, 255, cv2.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        save_image = cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)
        rgb = cv2.cvtColor(save_image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        return result

    def apply_hsv_filter(original_image, hsv_filter: HsvFilter):
        # convert image to HSV
        hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        # add/subtract saturation and value
        h, s, v = cv2.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
        hsv = cv2.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR for imshow() to display it properly
        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)

        return img

    def detect_sect_clear(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        wincap = WindowCapture(gamename, custom_rect=[
            464+156, 640, 464+261, 641])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a+b+c > 700:
            if d+e+f > 700:
                return True
        return False

    def detect_boss_healthbar(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        wincap = WindowCapture(gamename, custom_rect=[
                               415+97, 105+533, 415+98, 105+534])
        image = wincap.get_screenshot()
        # bgr
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if c+f > 440:
            if a+b+d+e < 80:
                return True
        return False

    def detect_xprompt(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        wincap = WindowCapture(gamename, custom_rect=[
            1137, 694, 1163, 695])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a+b+d+e > 960 and c+f == 140:
            return True
        else:
            return False

    def grab_player_pos(gamename=False, map_rect=None, rect_rel=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        if not map_rect:
            wincap = WindowCapture(gamename, [561, 282, 1111, 666])
        else:
            wincap = WindowCapture(gamename, map_rect)
        filter = HsvFilter(34, 160, 122, 50, 255, 255, 0, 0, 0, 0)
        image = wincap.get_screenshot()
        save_image = BotUtils.filter_blackwhite_invert(filter, image)
        vision = Vision('plyr.jpg')
        rectangles = vision.find(
            save_image, threshold=0.31, epsilon=0.5)
        if len(rectangles) < 1:
            return False, False
        points = vision.get_click_points(rectangles)
        x, y = points[0]
        if not map_rect:
            x += 561
            y += 282
            return x, y
        elif rect_rel:
            x += map_rect[0]
            y += map_rect[1]
            return x, y
        else:
            x += wincap.window_rect[0]
            y += wincap.window_rect[1]
            return x, y

    def grab_level_rects():
        rects = {}
        # Load the translation from name to num
        with open("lvl_name_num.txt") as f:
            num_names = f.readlines()
        for i, entry in enumerate(num_names):
            num_names[i] = entry.split("-")
        # Load the num to rect catalogue
        with open("catalogue.txt") as f:
            nums_rects = f.readlines()
        for i, entry in enumerate(nums_rects):
            nums_rects[i] = entry.split("-")
        # Then add each rect to the rects dict against name
        for number, name in num_names:
            for num, area, rect in nums_rects:
                if area == "FM" and num == number:
                    rects[name.rstrip().replace(" ", "")] = rect.rstrip()
                    if "1" in name:
                        rects[name.rstrip().replace(
                            " ", "").replace("1", "L")] = rect.rstrip()
                    if "ri" in name:
                        rects[name.rstrip().replace(
                            " ", "").replace("ri", "n").replace("1", "L")] = rect.rstrip()
                    break
        return rects

    def grab_level_rects_and_speeds():
        rects = {}
        speeds = {}
        # Load the translation from name to num
        with open("lvl_name_num.txt") as f:
            num_names = f.readlines()
        for i, entry in enumerate(num_names):
            num_names[i] = entry.split("-")
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
        for number, name in num_names:
            for num, area, rect in nums_rects:
                if area == "FM" and num == number:
                    rects[name.rstrip().replace(" ", "")] = rect.rstrip()
                    if "1" in name:
                        rects[name.rstrip().replace(
                            " ", "").replace("1", "L")] = rect.rstrip()
                    if "ri" in name:
                        rects[name.rstrip().replace(
                            " ", "").replace("ri", "n").replace("1", "L")] = rect.rstrip()
                    break
            for num, speed in num_speeds:
                if num == number:
                    speeds[name.rstrip().replace(
                        " ", "")] = float(speed.rstrip())
                    if "1" in name:
                        speeds[name.rstrip().replace(
                            " ", "").replace("1", "L")] = float(speed.rstrip())
                    if "ri" in name:
                        speeds[name.rstrip().replace(
                            " ", "").replace("ri", "n").replace("1", "L")] = float(speed.rstrip())
                    break
        return rects, speeds

    def string_to_rect(string: str):
        # This converts the rect from catalogue into int list
        return [int(i) for i in string.split(',')]

    def move_mouse_centre(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        wincap = WindowCapture(gamename)
        centre_x = int(0.5 * wincap.w +
                       wincap.window_rect[0])
        centre_y = int(0.5 * wincap.h +
                       wincap.window_rect[1])
        ctypes.windll.user32.SetCursorPos(centre_x, centre_y)

    def detect_bigmap_open(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        wincap = WindowCapture(gamename, custom_rect=[819, 263, 855, 264])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-2]]
        if a+b+c < 30:
            if d+e+f > 700:
                return True
        return False

    def detect_menu_open(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        wincap = WindowCapture(gamename, custom_rect=[595, 278, 621, 281])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a+b+c > 700:
            if d+e+f > 700:
                return True
        return False

    def convert_list_to_rel(item_list, playerx, playery, yoffset=0):
        return_list = []
        for item in item_list:
            relx = playerx - item[0]
            rely = item[1] - playery - yoffset
            return_list.append((relx, rely))
        return return_list

    def close_map_and_menu(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        game_wincap = WindowCapture(gamename)
        if BotUtils.detect_menu_open(gamename):
            BotUtils.close_esc_menu(game_wincap)
        if BotUtils.detect_bigmap_open(gamename):
            BotUtils.close_map(game_wincap)

    def try_toggle_map():
        pydirectinput.keyDown("m")
        time.sleep(0.05)
        pydirectinput.keyUp("m")
        time.sleep(0.08)

    def try_toggle_map_clicking(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        game_wincap = WindowCapture(gamename)
        pydirectinput.click(
            int(1262+game_wincap.window_rect[0]), int(64+game_wincap.window_rect[1]))

    def close_map(game_wincap=False):
        if not game_wincap:
            with open("gamename.txt") as f:
                gamename = f.readline()
            game_wincap = WindowCapture(gamename)
        pydirectinput.click(
            int(859+game_wincap.window_rect[0]), int(260+game_wincap.window_rect[1]))

    def close_esc_menu(game_wincap=False):
        if not game_wincap:
            with open("gamename.txt") as f:
                gamename = f.readline()
            game_wincap = WindowCapture(gamename)
        pydirectinput.click(
            int(749+game_wincap.window_rect[0]), int(280+game_wincap.window_rect[1]))

    def get_monitor_scaling():
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        return float(scaleFactor)

    def grab_res_scroll_left(gamename):
        wincap = WindowCapture(gamename, [112, 130, 125, 143])
        image = wincap.get_screenshot()
        filter = HsvFilter(0, 0, 0, 179, 18, 255, 0, 0, 0, 0)
        image = BotUtils.apply_hsv_filter(image, filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=1234567890'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        return int(result)

    def read_mission_name(gamename):
        wincap = WindowCapture(gamename, [749, 152, 978, 170])
        image = wincap.get_screenshot()
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        return result

    def convert_click_to_ratio(gamename, truex, truey):
        wincap = WindowCapture(gamename)
        wincap.update_window_position(border=False)
        scaling = BotUtils.get_monitor_scaling()
        # print(scaling)
        relx = (truex - (wincap.window_rect[0] * scaling))
        rely = (truey - (wincap.window_rect[1] * scaling))
        # print("relx, rely, w, h: {},{},{},{}".format(
        #     relx, rely, wincap.w, wincap.h))
        ratx = relx/(wincap.w * scaling)
        raty = rely/(wincap.h * scaling)
        return ratx, raty

    def convert_ratio_to_click(ratx, raty, gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        wincap = WindowCapture(gamename)
        relx = int(ratx * wincap.w)
        rely = int(raty * wincap.h)
        truex = int((relx + wincap.window_rect[0]))
        truey = int((rely + wincap.window_rect[1]))
        return truex, truey

    def convert_true_to_window(gamename, truex, truey):
        scaling = BotUtils.get_monitor_scaling()
        wincap = WindowCapture(gamename)
        relx = (truex/scaling) - wincap.window_rect[0]
        rely = (truey/scaling) - wincap.window_rect[1]
        return relx, rely

    def convert_window_to_true(gamename, relx, rely):
        wincap = WindowCapture(gamename)
        truex = int(relx + wincap.window_rect[0])
        truey = int(rely + wincap.window_rect[1])
        return truex, truey

    def find_other_player(gamename, all=False):
        othr_plyr_vision = Vision("otherplayerinvert.jpg")
        othr_plyr_wincap = WindowCapture(gamename, [1100, 50, 1260, 210])
        image = othr_plyr_wincap.get_screenshot()
        filter = HsvFilter(24, 194, 205, 31, 255, 255, 0, 0, 0, 0)
        image = cv2.blur(image, (4, 4))
        image = BotUtils.filter_blackwhite_invert(filter, image)
        rectangles = othr_plyr_vision.find(
            image, threshold=0.61, epsilon=0.5)
        points = othr_plyr_vision.get_click_points(rectangles)
        if len(points) >= 1:
            if not all:
                relx = points[0][0] - 0
                rely = 0 - points[0][1]
                return relx, rely
            else:
                return points
        return False

    def find_enemy(gamename, all=False):
        othr_plyr_vision = Vision("otherplayerinvert.jpg")
        othr_plyr_wincap = WindowCapture(gamename, [1100, 50, 1260, 210])
        image = othr_plyr_wincap.get_screenshot()
        filter = HsvFilter(0, 198, 141, 8, 255, 255, 0, 0, 0, 0)
        image = cv2.blur(image, (4, 4))
        image = BotUtils.filter_blackwhite_invert(filter, image)
        rectangles = othr_plyr_vision.find(
            image, threshold=0.41, epsilon=0.5)
        points = othr_plyr_vision.get_click_points(rectangles)
        if len(points) >= 1:
            if not all:
                relx = points[0][0] - 0
                rely = 0 - points[0][1]
                return relx, rely
            else:
                return points
        return False

    def find_midlevel_event(gamename=False, playerx=False, playery=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        if not playerx:
            playerx, playery = BotUtils.grab_player_pos(
                gamename, [1100, 50, 1260, 210], True)
        filter = HsvFilter(76, 247, 170, 100, 255, 255, 0, 0, 0, 0)
        vision = Vision("otherplayerinvert.jpg")
        wincap = WindowCapture(gamename, [1100, 50, 1260, 210])
        image = wincap.get_screenshot()
        image = cv2.blur(image, (4, 4))
        image = BotUtils.filter_blackwhite_invert(filter, image)
        rectangles = vision.find(
            image, threshold=0.61, epsilon=0.5)
        points = vision.get_click_points(rectangles)
        if len(points) >= 1:
            relx = points[0][0] - playerx
            rely = playery - points[0][1]
            return relx, rely
        return False, False

    def stop_movement(follower=False):
        if follower:
            follower.pressed_keys = []
        for key in ["up", "down", "left", "right"]:
            CustomInput.release_key(CustomInput.key_map[key], key)


class Looting:
    def loot_current_room(gamename, player_name, search_points=False):
        # Start by picking up loot already in range
        BotUtils.close_map_and_menu(gamename)
        Looting.grab_nearby_loot(gamename)
        # Then try grabbing all visible far loot
        Looting.grab_all_visible_loot(gamename, player_name)
        # Then once that is exhausted cycle through the searchpoints
        if search_points:
            for point in search_points:
                x, y, first_dir = point
                BotUtils.move_to(gamename, x, y, yfirst=first_dir == "y")
                Looting.grab_nearby_loot(gamename)
                BotUtils.close_map_and_menu(gamename)
                Looting.grab_all_visible_loot(gamename, player_name)

    def grab_nearby_loot(gamename):
        count = 0
        while BotUtils.detect_xprompt(gamename):
            if count > 12:
                break
            pydirectinput.press("x")
            count += 1
            time.sleep(0.09)

    def grab_all_visible_loot(gamename, player_name):
        start_time = time.time()
        while True:
            if time.time() - start_time > 20:
                break
            outcome = Looting.try_find_and_grab_loot(
                gamename, player_name)
            if outcome == "noloot":
                break
            elif outcome == "noplayer":
                pydirectinput.press("right")
                outcome = Looting.try_find_and_grab_loot(
                    gamename, player_name)
                if outcome == "noplayer":
                    break
            elif outcome == "falsepos":
                break
            elif outcome == True:
                count = 0
                while BotUtils.detect_xprompt(gamename):
                    if count > 12:
                        break
                    pydirectinput.press("x")
                    count += 1
                    time.sleep(0.09)

    def check_for_loot(gamename):
        # This will be a lightweight check for any positive loot ident
        # Meant to be used when moving and normal looting has ceased
        # i.e. opportunistic looting
        data = Looting.grab_farloot_locations(
            gamename, return_image=True)
        if not data:
            return False
        else:
            loot_list, image, xoff, yoff = data
        confirmed = False
        for _, coords in enumerate(loot_list):
            x, y = coords
            x -= xoff
            y -= yoff
            rgb = image[y-22:y+22, x-75:x+75]
            filter = HsvFilter(0, 0, 131, 151, 255, 255, 0, 0, 0, 0)
            rgb = BotUtils.apply_hsv_filter(rgb, filter)
            tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            result = pytesseract.image_to_string(
                rgb, lang='eng', config=tess_config)[:-2]
            if len(result) > 3:
                return True
        if not confirmed:
            return False

    def try_find_and_grab_loot(gamename, player_name, loot_lowest=True, printout=False):
        # First need to close anything that might be in the way
        BotUtils.close_map_and_menu(gamename)
        # Then grab loot locations
        loot_list = Looting.grab_farloot_locations(gamename)
        if not loot_list:
            return "noloot"

        playerx, playery = BotUtils.grab_character_location(
            player_name, gamename)
        # If didn't find player then try once more
        if not playerx:
            playerx, playery = BotUtils.grab_character_location(
                player_name, gamename)
            if not playerx:
                return "noplayer"

        # if want to always loot the nearest first despite the cpu hit
        if not loot_lowest:
            # Then convert lootlist to rel_pos list
            relatives = BotUtils.convert_list_to_rel(
                loot_list, playerx, playery, 275)
            # Grab the indexes in ascending order of closesness
            order = BotUtils.grab_order_closeness(relatives)
            # Then reorder the lootlist to match
            loot_list = [x for _, x in sorted(zip(order, loot_list))]
        # Otherwise if want to loot from bottom of screen to top
        # Typically better as see all loot then in y direction
        # but potentially miss loot in x direction
        else:
            # Grab the indexes in ascending order of distance from
            # bottom of the screen
            order = BotUtils.grab_order_lowest_y(loot_list)
            # Then reorder the lootlist to match
            loot_list = [x for _, x in sorted(zip(order, loot_list))]

        confirmed = False
        for index, coords in enumerate(loot_list):
            x, y = coords
            wincap = WindowCapture(gamename, [x-75, y-22, x+75, y+22])
            rgb = wincap.get_screenshot()
            filter = HsvFilter(0, 0, 131, 151, 255, 255, 0, 0, 0, 0)
            rgb = BotUtils.apply_hsv_filter(rgb, filter)
            tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            result = pytesseract.image_to_string(
                rgb, lang='eng', config=tess_config)[:-2]
            if len(result) > 3:
                if printout:
                    print(result)
                confirmed = loot_list[index]
                break
        if not confirmed:
            return "noloot"

        relx = playerx - confirmed[0]
        rely = confirmed[1] - playery - 275
        rect = [confirmed[0]-100, confirmed[1] -
                30, confirmed[0]+100, confirmed[1]+30]
        BotUtils.move_towards(relx, "x")
        loop_time = time.time()
        time_remaining = 0.1
        time.sleep(0.01)
        while time_remaining > 0:
            time.sleep(0.003)
            if BotUtils.detect_xprompt(gamename):
                break
            try:
                newx, newy = Looting.grab_farloot_locations(gamename, rect)[
                    0]
                time_taken = time.time() - loop_time
                movementx = confirmed[0] - newx
                speed = movementx/time_taken
                if speed != 0:
                    time_remaining = abs(
                        relx/speed) - time_taken
                rect = [newx-100, newy-30, newx+100, newy+30]
            except:
                try:
                    time.sleep(time_remaining)
                    break
                except:
                    return False
        for key in ["left", "right"]:
            CustomInput.release_key(CustomInput.key_map[key], key)
        BotUtils.move_towards(rely, "y")
        start_time = time.time()
        if rely < 0:
            expected_time = abs(rely/7.5)
        else:
            expected_time = abs(rely/5.5)
        while not BotUtils.detect_xprompt(gamename):
            time.sleep(0.005)
            # After moving in opposite direction
            if time.time() - start_time > 10:
                # If have moved opposite with no result for equal amount
                if time.time() - start_time > 10 + 2*(1 + expected_time):
                    for key in ["up", "down"]:
                        CustomInput.release_key(CustomInput.key_map[key], key)
                    # Return falsepos so that it will ignore this detection
                    return "falsepos"
            # If no result for 3 seconds
            elif time.time() - start_time > 1 + expected_time:
                # Try moving in the opposite direction
                for key in ["up", "down"]:
                    CustomInput.release_key(CustomInput.key_map[key], key)
                BotUtils.move_towards(-1*rely, "y")
                start_time -= 8.5
        for key in ["up", "down"]:
            CustomInput.release_key(CustomInput.key_map[key], key)
        pydirectinput.press("x")
        return True

    def grab_farloot_locations(gamename=False, rect=False, return_image=False):
        if gamename:
            if not rect:
                rect1 = [100, 135, 1223, 688]
                wincap = WindowCapture(gamename, rect1)
            else:
                wincap = WindowCapture(gamename, rect)
            original_image = wincap.get_screenshot()
        else:
            original_image = cv2.imread(os.path.dirname(
                os.path.abspath(__file__)) + "/testimages/lootscene.jpg")
        filter = HsvFilter(15, 180, 0, 20, 255, 63, 0, 0, 0, 0)
        output_image = BotUtils.filter_blackwhite_invert(
            filter, original_image, True, 0, 180)

        output_image = cv2.blur(output_image, (8, 1))
        output_image = cv2.blur(output_image, (8, 1))
        output_image = cv2.blur(output_image, (8, 1))

        _, thresh = cv2.threshold(output_image, 127, 255, 0)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        if len(contours) < 2:
            return False
        contours.pop(0)
        rectangles = []
        for contour in contours:
            (x, y), _ = cv2.minEnclosingCircle(contour)
            rectangles.append([x-50, y, 100, 5])
            rectangles.append([x-50, y, 100, 5])
        rectangles, _ = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=0.9)
        if len(rectangles) < 1:
            return False
        points = []
        for (x, y, w, h) in rectangles:
            # Account for the rect
            if rect:
                # Account for the rect
                x += rect[0]
                y += rect[1]
            else:
                x += 100
                y += 135
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        if return_image:
            if rect:
                return points, original_image, rect[0], rect[1]
            else:
                return points, original_image, rect1[0], rect1[1]
        return points


class Events:
    def choose_random_reward(gamename):
        wincap = WindowCapture(gamename)
        posx = wincap.window_rect[0] + (460+(180*random.randint(0, 2)))
        posy = wincap.window_rect[1] + (200+(132*random.randint(0, 3)))
        pydirectinput.click(int(posx), int(posy))
        # Now accept the reward
        pydirectinput.click(
            wincap.window_rect[0]+750, wincap.window_rect[1]+720)

    def detect_reward_choice_open(gamename):
        wincap = WindowCapture(gamename, [503, 90, 535, 92])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a + d > 400:
            if b + e > 500:
                if c + f < 105:
                    return True
        return False

    def detect_move_reward_screen(gamename):
        wincap = WindowCapture(gamename, [581, 270, 593, 272])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a + d > 360 and a + d < 400:
            if b + e > 360 and b + e < 400:
                if c + f < 10:
                    return True
        return False

    def detect_endlevel_chest(gamename):
        wincap = WindowCapture(gamename, [454, 250, 525, 252])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a + d < 50:
            if b + e > 480:
                if c + f > 290 and c+f < 320:
                    return True
        return False

    def detect_endlevel_bonus_area(gamename):
        wincap = WindowCapture(gamename, [503, 487, 514, 589])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a + d > 400:
            if b + e > 400:
                if c + f > 400:
                    return True
        return False

    def detect_in_dungeon(wincap=False):
        if not wincap:
            with open("gamename.txt") as f:
                gamename = f.readline()
            wincap = WindowCapture(gamename, [1090, 331, 1092, 353])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[-1][0]]
        if d < 20:
            if a + b + e > 400 and a+b+e < 500:
                if c + f > 480:
                    return True
        return False

    def detect_go(gamename):
        wincap = WindowCapture(gamename, [623, 247, 628, 249])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        if a < 30:
            if b > 240:
                if c > 140:
                    return True
        return False

    def detect_one_card(gamename):
        # Cards only show up once one has been picked
        # Therefore need to check against bronze, gold, silver
        wincap = WindowCapture(gamename, [833, 44, 835, 46])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        # Bronze
        if a == 27:
            if b == 48:
                if c == 87:
                    return True
        # Silver
        if a == 139:
            if b == 139:
                if c == 139:
                    return True
        # Gold
        if a == 38:
            if b == 129:
                if c == 160:
                    return True
        return False

    def detect_yes_no(gamename):
        wincap = WindowCapture(gamename, [516, 426, 541, 441])
        image = wincap.get_screenshot()
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=Yes'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        if result == "Yes":
            return True
        return False

    def detect_resurrect_prompt(gamename):
        wincap = WindowCapture(gamename, [763, 490, 818, 492])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[-1][0]]
        if a + d > 500:
            if b + e > 500:
                if c + f > 500:
                    return True
        return False

    def detect_store(gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        wincap = WindowCapture(gamename, [763, 490, 818, 492])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[-1][0]]
        if a + d > 500:
            if b + e > 500:
                if c + f > 500:
                    return True
        return False


class RHClick:
    def click_yes(gamename):
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+528, wincap.window_rect[1]+433)

    def click_no(gamename):
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+763, wincap.window_rect[1]+433)

    def click_choose_map(gamename):
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+1150, wincap.window_rect[1]+210)

    def click_explore_again(gamename):
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+1150, wincap.window_rect[1]+152)

    def click_back_to_town(gamename):
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+1150, wincap.window_rect[1]+328)

    def click_map_number(gamename, mapnum):
        wincap = WindowCapture(gamename)
        map_to_clickpoints = {
            5: (728, 521),
            6: (640, 631),
            7: (605, 455),
            8: (542, 350),
            9: (293, 297),
            10: (777, 406),
            11: (140, 370),
            12: (500, 246),
            13: (500, 672),
            14: (419, 478),
            15: (423, 263),
            16: (563, 562),
            17: (642, 432),
            18: (249, 325)
        }
        x, y = map_to_clickpoints[mapnum]
        pydirectinput.click(wincap.window_rect[0]+x, wincap.window_rect[1]+y)

    def choose_difficulty_and_enter(gamename, diff):
        wincap = WindowCapture(gamename)
        num_clicks = 0
        if diff == "N":
            num_clicks = 0
        elif diff == "H":
            num_clicks = 1
        elif diff == "VH":
            num_clicks == 2
        elif diff == "BM":
            num_clicks == 3
        for i in range(num_clicks):
            pydirectinput.click(
                wincap.window_rect[0]+618, wincap.window_rect[1]+333)
            time.sleep(0.3)
        # Then click on enter dungeon
        pydirectinput.click(
            wincap.window_rect[0]+1033, wincap.window_rect[1]+736)

    def go_to_change_character(gamename):
        if not BotUtils.detect_menu_open(gamename):
            pydirectinput.press('esc')
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+640, wincap.window_rect[1]+363)

    def exit_game(gamename):
        if not BotUtils.detect_menu_open(gamename):
            pydirectinput.press('esc')
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+640, wincap.window_rect[1]+480)
        time.sleep(0.2)
        pydirectinput.click(
            wincap.window_rect[0]+640, wincap.window_rect[1]+428)

    def choose_character(gamename, charnum):
        wincap = WindowCapture(gamename)
        char_clickpoints = {
            1: (1100, 140),
            2: (1100, 210),
            3: (1100, 280),
            4: (1100, 350),
            5: (1100, 420),
            6: (1100, 490),
            7: (1100, 560),
            8: (1100, 630)
        }
        if charnum > 8:
            pydirectinput.click(
                wincap.window_rect[0]+1165, wincap.window_rect[1]+680)
            x, y = char_clickpoints[charnum-8]
        else:
            pydirectinput.click(
                wincap.window_rect[0]+1035, wincap.window_rect[1]+680)
            x, y = char_clickpoints[charnum]
        time.sleep(0.2)
        pydirectinput.click(wincap.window_rect[0]+x, wincap.window_rect[1]+y)
        time.sleep(0.2)
        pydirectinput.click(
            wincap.window_rect[0]+640, wincap.window_rect[1]+765)


class Vision:
    def __init__(self, needle_img_path, method=cv2.TM_CCOEFF_NORMED):
        self.needle_img = cv2.imread(needle_img_path, cv2.IMREAD_UNCHANGED)
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, haystack_img, threshold=0.7, max_results=15, epsilon=0.5):
        result = cv2.matchTemplate(haystack_img, self.needle_img, self.method)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            rectangles.append(rect)
            rectangles.append(rect)
        rectangles, weights = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=epsilon)
        return rectangles

    def get_click_points(self, rectangles):
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def draw_rectangles(self, haystack_img, rectangles):
        # BGR
        line_color = (0, 255, 0)
        line_type = cv2.LINE_4
        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv2.rectangle(haystack_img, top_left, bottom_right,
                          line_color, lineType=line_type)
        return haystack_img

    def draw_crosshairs(self, haystack_img, points):
        # BGR
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS

        for (center_x, center_y) in points:
            cv2.drawMarker(haystack_img, (center_x, center_y),
                           marker_color, marker_type)

        return haystack_img


class DynamicFilter:
    TRACKBAR_WINDOW = "Trackbars"
    # create gui window with controls for adjusting arguments in real-time

    def __init__(self, needle_img_path, method=cv2.TM_CCOEFF_NORMED):
        self.needle_img = cv2.imread(needle_img_path, cv2.IMREAD_UNCHANGED)
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, haystack_img, threshold=0.7, epsilon=0.5):
        result = cv2.matchTemplate(haystack_img, self.needle_img, self.method)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            rectangles.append(rect)
            rectangles.append(rect)
        rectangles, weights = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=epsilon)
        return rectangles

    def get_click_points(self, rectangles):
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def draw_rectangles(self, haystack_img, rectangles):
        # BGR
        line_color = (0, 255, 0)
        line_type = cv2.LINE_4
        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv2.rectangle(haystack_img, top_left, bottom_right,
                          line_color, lineType=line_type)
        return haystack_img

    def draw_crosshairs(self, haystack_img, points):
        # BGR
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS

        for (center_x, center_y) in points:
            cv2.drawMarker(haystack_img, (center_x, center_y),
                           marker_color, marker_type)

        return haystack_img

    def init_control_gui(self):
        cv2.namedWindow(self.TRACKBAR_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        # required callback. we'll be using getTrackbarPos() to do lookups
        # instead of using the callback.
        def nothing(position):
            pass

        # create trackbars for bracketing.
        # OpenCV scale for HSV is H: 0-179, S: 0-255, V: 0-255
        cv2.createTrackbar('HMin', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv2.createTrackbar('SMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('HMax', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv2.createTrackbar('SMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        # Set default value for Max HSV trackbars
        cv2.setTrackbarPos('HMax', self.TRACKBAR_WINDOW, 179)
        cv2.setTrackbarPos('SMax', self.TRACKBAR_WINDOW, 255)
        cv2.setTrackbarPos('VMax', self.TRACKBAR_WINDOW, 255)

        # trackbars for increasing/decreasing saturation and value
        cv2.createTrackbar('SAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('SSub', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VSub', self.TRACKBAR_WINDOW, 0, 255, nothing)

    # returns an HSV filter object based on the control GUI values
    def get_hsv_filter_from_controls(self):
        # Get current positions of all trackbars
        hsv_filter = HsvFilter()
        hsv_filter.hMin = cv2.getTrackbarPos('HMin', self.TRACKBAR_WINDOW)
        hsv_filter.sMin = cv2.getTrackbarPos('SMin', self.TRACKBAR_WINDOW)
        hsv_filter.vMin = cv2.getTrackbarPos('VMin', self.TRACKBAR_WINDOW)
        hsv_filter.hMax = cv2.getTrackbarPos('HMax', self.TRACKBAR_WINDOW)
        hsv_filter.sMax = cv2.getTrackbarPos('SMax', self.TRACKBAR_WINDOW)
        hsv_filter.vMax = cv2.getTrackbarPos('VMax', self.TRACKBAR_WINDOW)
        hsv_filter.sAdd = cv2.getTrackbarPos('SAdd', self.TRACKBAR_WINDOW)
        hsv_filter.sSub = cv2.getTrackbarPos('SSub', self.TRACKBAR_WINDOW)
        hsv_filter.vAdd = cv2.getTrackbarPos('VAdd', self.TRACKBAR_WINDOW)
        hsv_filter.vSub = cv2.getTrackbarPos('VSub', self.TRACKBAR_WINDOW)
        return hsv_filter

    def apply_hsv_filter(self, original_image, hsv_filter=None):
        hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        if not hsv_filter:
            hsv_filter = self.get_hsv_filter_from_controls()

        h, s, v = cv2.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
        hsv = cv2.merge([h, s, v])

        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)
        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
        return img


class SellRepair():
    def __init__(self, rarity_cutoff=1, last_row_protect=True) -> None:
        # rarities are as follows:
        # nocolour=0, green=1, blue=2
        self.cutoff = rarity_cutoff
        # this is for whether lastrow in equip is protected
        # useful for characters levelling with next upgrades ready
        self.last_row_protect = last_row_protect
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.inventory_wincap = WindowCapture(
            self.gamename, [512, 277, 775, 430])

        # This is for correct mouse positioning
        self.game_wincap = WindowCapture(self.gamename)

        self.shop_check_wincap = WindowCapture(
            self.gamename, [274, 207, 444, 208])

        # These are for holding reference rgb values
        # Using sets as can then compare easily to other sets
        self.empty = {41, 45, 50}
        self.rar_green = {2, 204, 43}
        self.rar_blue = {232, 144, 5}
        self.rar_none = {24, 33, 48}
        self.junk_list = self.grab_junk_list()

    def grab_junk_list(self):
        jl = []
        with open("itemrgb.txt") as f:
            lines = f.readlines()
            for line in lines:
                _, rgb = line.split("|")
                r, g, b = rgb.split(",")
                jl.append({int(r), int(g), int(b)})
        return jl

    def ident_sell_repair(self):
        self.game_wincap.update_window_position(border=False)
        self.shop_check_wincap.update_window_position(border=False)
        self.open_store_if_necessary()
        # First go through all the equipment
        self.change_tab("Equipment")
        # time.sleep(0.2)
        # self.hover_mouse_all()
        time.sleep(0.3)
        screenshot = self.inventory_wincap.get_screenshot()
        non_empty = self.remove_empty(screenshot)
        junk_list = self.identify_rarities_equip(non_empty, screenshot)
        self.sell(junk_list, "Equipment")
        # Then go through all the other loot
        self.change_tab("Other")
        # time.sleep(0.2)
        # self.hover_mouse_all()
        time.sleep(0.3)
        screenshot = self.inventory_wincap.get_screenshot()
        non_empty = self.remove_empty(screenshot)
        junk_list = self.identify_items_other(non_empty, screenshot)
        self.sell(junk_list)
        # and finally repair gear
        self.repair()
        # and now go through all the steps again minus repair to make sure
        self.change_tab("Equipment")
        time.sleep(0.3)
        screenshot = self.inventory_wincap.get_screenshot()
        non_empty = self.remove_empty(screenshot)
        junk_list = self.identify_rarities_equip(non_empty, screenshot)
        self.sell(junk_list, "Equipment")
        self.change_tab("Other")
        time.sleep(0.3)
        screenshot = self.inventory_wincap.get_screenshot()
        non_empty = self.remove_empty(screenshot)
        junk_list = self.identify_items_other(non_empty, screenshot)
        self.sell(junk_list)

    def open_store_if_necessary(self):
        # This will search to see if the inventory is open
        # in the correct spot and then click shop if not
        screenshot = self.shop_check_wincap.get_screenshot()
        pix1 = screenshot[0, 0]
        pix1 = int(pix1[0]) + int(pix1[1]) + int(pix1[2])
        pix2 = screenshot[0, 169]
        pix2 = int(pix2[0]) + int(pix2[1]) + int(pix2[2])
        if pix1 == 103 and pix2 == 223:
            pass
        else:
            # need to open the store
            self.game_wincap.update_window_position(border=False)
            offsetx = self.game_wincap.window_rect[0] + 534
            offsety = self.game_wincap.window_rect[1] + 277
            ctypes.windll.user32.SetCursorPos(offsetx+610, offsety-10)
            ctypes.windll.user32.mouse_event(
                0x0002, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(
                0x0004, 0, 0, 0, 0)

    def change_tab(self, name):
        self.game_wincap.update_window_position(border=False)
        x = self.game_wincap.window_rect[0] + 534-60
        if name == "Equipment":
            y = self.game_wincap.window_rect[1] + 277 - 15
        elif name == "Other":
            y = self.game_wincap.window_rect[1] + 277 + 44
        ctypes.windll.user32.SetCursorPos(x, y)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)

    def hover_mouse_all(self):
        self.game_wincap.update_window_position(border=False)
        offsetx = self.game_wincap.window_rect[0] + 534
        offsety = self.game_wincap.window_rect[1] + 277
        for i in range(4):
            for j in range(6):
                x = offsetx+j*44
                y = offsety+i*44
                ctypes.windll.user32.SetCursorPos(x-10, y)
                time.sleep(0.03)
                ctypes.windll.user32.SetCursorPos(x, y)
                time.sleep(0.03)
                ctypes.windll.user32.SetCursorPos(x+10, y)
        ctypes.windll.user32.SetCursorPos(offsetx, offsety-70)

        # ctypes.windll.user32.SetCursorPos(offsetx+610, offsety-10)

    def remove_empty(self, screenshot):
        non_empty = []
        for i in range(4):
            for j in range(6):
                colour = set(screenshot[i*44, 22+j*44])
                if colour != self.empty:
                    non_empty.append([i, j])
        # format will be as follows of return list
        # x,y,r,g,b
        return non_empty

    def identify_rarities_equip(self, rowcol_list, screenshot):
        junk = []
        for rowcol in rowcol_list:
            colour = set(screenshot[rowcol[0]*44, rowcol[1]*44])
            if colour == self.rar_none:
                junk.append([rowcol[0], rowcol[1]])
            elif colour == self.rar_green:
                if self.cutoff >= 1:
                    junk.append([rowcol[0], rowcol[1]])
            elif colour == self.rar_green:
                if self.cutoff >= 2:
                    junk.append([rowcol[0], rowcol[1]])
        # format will be as follows of return list
        # x,y corresponding to row,col
        return junk

    def identify_items_other(self, rowcol_list, screenshot):
        junk = []
        for rowcol in rowcol_list:
            colour = set(screenshot[rowcol[0]*44, 22+rowcol[1]*44])
            if colour in self.junk_list:
                junk.append([rowcol[0], rowcol[1]])
        # format will be as follows of return list
        # x,y corresponding to row,col
        return junk

    def sell(self, rowcol_list, tab="Other"):
        offsetx = self.game_wincap.window_rect[0] + 534
        offsety = self.game_wincap.window_rect[1] + 277
        for item in rowcol_list:
            if tab == "Equipment":
                if self.last_row_protect:
                    if item[0] == 3:
                        continue
            x = offsetx+item[1]*44
            y = offsety+item[0]*44
            ctypes.windll.user32.SetCursorPos(x, y)
            time.sleep(0.1)
            ctypes.windll.user32.mouse_event(
                0x0008, 0, 0, 0, 0)
            time.sleep(0.01)
            ctypes.windll.user32.mouse_event(
                0x0010, 0, 0, 0, 0)
            # Then click a second time to be sure
            time.sleep(0.01)
            ctypes.windll.user32.mouse_event(
                0x0008, 0, 0, 0, 0)
            time.sleep(0.01)
            ctypes.windll.user32.mouse_event(
                0x0010, 0, 0, 0, 0)

    def repair(self):
        self.game_wincap.update_window_position(border=False)
        offsetx = self.game_wincap.window_rect[0] + 534
        offsety = self.game_wincap.window_rect[1] + 277
        ctypes.windll.user32.SetCursorPos(offsetx-310, offsety+325)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)
        ctypes.windll.user32.SetCursorPos(offsetx+0, offsety+180)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)
        # this is if everything is already repaired
        ctypes.windll.user32.SetCursorPos(offsetx+100, offsety+180)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)


class QuestHandle():
    def __init__(self) -> None:
        with open("gamename.txt") as f:
            gamename = f.readline()
        self.game_wincap = WindowCapture(gamename)
        self.white_text_filter = HsvFilter(
            0, 0, 102, 45, 65, 255, 0, 0, 0, 0)
        self.yellow_text_filter = HsvFilter(
            16, 71, 234, 33, 202, 255, 0, 0, 0, 0)
        self.blue_text_filter = HsvFilter(
            83, 126, 85, 102, 255, 255, 0, 0, 0, 0)
        self.all_text_filter = HsvFilter(
            0, 0, 61, 78, 255, 255, 0, 255, 0, 0)
        self.vision = Vision('xprompt67filtv2.jpg')
        self.accept_rect = [725, 525, 925, 595]
        self.accept_wincap = WindowCapture(gamename, self.accept_rect)
        self.skip_rect = [730, 740, 890, 780]
        self.skip_wincap = WindowCapture(gamename, self.skip_rect)
        self.next_rect = [880, 740, 1040, 780]
        self.next_wincap = WindowCapture(gamename, self.next_rect)
        self.quest_rect = [310, 160, 1055, 650]
        self.quest_wincap = WindowCapture(gamename, self.quest_rect)
        self.questlist_rect = [740, 240, 1050, 580]
        self.questlist_wincap = WindowCapture(gamename, self.questlist_rect)
        self.complete_wincap = WindowCapture(gamename, self.next_rect)
        self.xprompt_rect = [1130, 670, 1250, 720]
        self.xprompt_wincap = WindowCapture(gamename, self.xprompt_rect)

    def start_quest_handle(self):
        start_time = time.time()
        while time.time() < start_time + 2:
            if self.check_for_accept():
                break

    def convert_and_click(self, x, y, rect):
        self.game_wincap.update_window_position(border=False)
        truex = int(x + self.game_wincap.window_rect[0] + rect[0])
        truey = int(y + self.game_wincap.window_rect[1] + rect[1])
        ctypes.windll.user32.SetCursorPos(truex, truey)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)

    def check_for_accept(self):
        image = self.accept_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Accept" in results["text"][i]:
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                self.convert_and_click(x, y, self.accept_rect)
                detection = True
                break
        if not detection:
            return self.check_for_skip()
        else:
            return True

    def check_for_skip(self):
        image = self.skip_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Skip" in results["text"][i]:
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                self.convert_and_click(x, y, self.skip_rect)
                detection = True
                break
        if not detection:
            return self.check_for_next()
        else:
            return True

    def check_for_next(self):
        image = self.next_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Next" in results["text"][i]:
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                self.convert_and_click(x, y, self.next_rect)
                detection = True
                break
        if not detection:
            return self.check_for_quest()
        else:
            return True

    def check_for_quest(self):
        image = self.quest_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=Quest'
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng', config=tess_config)
        detection = False
        for i in range(0, len(results["text"])):
            if "Quest" in results["text"][i]:
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                self.convert_and_click(x, y, self.quest_rect)
                detection = True
                break
        if not detection:
            return self.check_for_questlist()
        else:
            return True

    def check_for_questlist(self):
        image = self.questlist_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.all_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "LV" in results["text"][i]:
                # at this point need to grab the centre of the rect
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                # and then click at this position
                self.convert_and_click(x, y, self.questlist_rect)
                detection = True
                break
        if not detection:
            return self.check_for_complete()
        else:
            return True

    def check_for_complete(self):
        image = self.complete_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Com" in results["text"][i]:
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                self.convert_and_click(x, y, self.next_rect)
                detection = True
                break
        if not detection:
            return self.check_for_xprompt()
        else:
            return True

    def check_for_xprompt(self):
        image = self.xprompt_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.blue_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Press" in results["text"][i]:
                pydirectinput.keyDown("x")
                time.sleep(0.1)
                pydirectinput.keyUp("x")
                detection = True
                break
        if not detection:
            return False
        else:
            return True


class Follower():
    def __init__(self) -> None:
        self.pressed_keys = []
        self.relx = 0
        self.rely = 0

    def navigate_towards(self, x, y):
        self.relx = x
        self.rely = y
        if self.relx > 1:
            # Check if opposite key held down
            if "left" in self.pressed_keys:
                self.pressed_keys.remove("left")
                CustomInput.release_key(CustomInput.key_map["left"], "left")
            # Check that not already being held down
            if "right" not in self.pressed_keys:
                self.pressed_keys.append("right")
                # Hold the key down
                CustomInput.press_key(CustomInput.key_map["right"], "right")

        elif self.relx < -1:
            # Check if opposite key held down
            if "right" in self.pressed_keys:
                self.pressed_keys.remove("right")
                CustomInput.release_key(CustomInput.key_map["right"], "right")
            # Check that not already being held down
            if "left" not in self.pressed_keys:
                self.pressed_keys.append("left")
                # Hold the key down
                CustomInput.press_key(CustomInput.key_map["left"], "left")

        else:
            # Handling for case where = 0, need to remove both keys
            if "right" in self.pressed_keys:
                self.pressed_keys.remove("right")
                CustomInput.release_key(CustomInput.key_map["right"], "right")
            if "left" in self.pressed_keys:
                self.pressed_keys.remove("left")
                CustomInput.release_key(CustomInput.key_map["left"], "left")

        # Handling for y-dir next
        if self.rely > 1:
            # Check if opposite key held down
            if "down" in self.pressed_keys:
                self.pressed_keys.remove("down")
                CustomInput.release_key(CustomInput.key_map["down"], "down")
            # Check that not already being held down
            if "up" not in self.pressed_keys:
                self.pressed_keys.append("up")
                # Hold the key down
                CustomInput.press_key(CustomInput.key_map["up"], "up")

        elif self.rely < -1:
            # Check if opposite key held down
            if "up" in self.pressed_keys:
                self.pressed_keys.remove("up")
                CustomInput.release_key(CustomInput.key_map["up"], "up")
            # Check that not already being held down
            if "down" not in self.pressed_keys:
                self.pressed_keys.append("down")
                # Hold the key down
                CustomInput.press_key(CustomInput.key_map["down"], "down")
        else:
            # Handling for case where = 0, need to remove both keys
            if "up" in self.pressed_keys:
                self.pressed_keys.remove("up")
                CustomInput.release_key(CustomInput.key_map["up"], "up")
            if "down" in self.pressed_keys:
                self.pressed_keys.remove("down")
                CustomInput.release_key(CustomInput.key_map["down"], "down")


if __name__ == "__main__":
    time.sleep(2)
    with open("gamename.txt") as f:
        gamename = f.readline()
    # start = time.time()
    # BotUtils.detect_xprompt(gamename)
    # print("Time taken: {}s".format(time.time()-start))
    BotUtils.close_map_and_menu(gamename)
