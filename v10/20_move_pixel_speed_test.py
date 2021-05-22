import cv2 as cv
from hsvfilter import HsvFilter, grab_object_preset
import numpy as np
import os
from vision import Vision
import time
import time
import os
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
from hsvfilter import HsvFilter
from windowcapture import WindowCapture
from vision import Vision
import cv2
import pytesseract
import ctypes
import pydirectinput
from win32gui import GetWindowText, GetForegroundWindow
from client import ClientUtils
from fuzzywuzzy import process
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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


class PlayerPositionTest():

    def __init__(self) -> None:
        self.map_rect = None
        self.level_name = None
        self.rects = {}
        self.num_names = []
        self.load_level_rects()
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.key_map = self.load_key_dict()

    def start(self):
        time.sleep(3)
        # print("Starting")
        self.level_name = self.detect_level_name()
        # Then grab the right rect for the level
        try:
            self.map_rect = self.string_to_rect(self.rects[self.level_name])
        except:
            try:
                best_match = process.extractOne(
                    self.level_name, self.rects, score_cutoff=0.8)
                self.map_rect = self.string_to_rect(
                    self.rects[best_match])
            except:
                self.map_rect = [362, 243, 1105, 748]
        # Then open the map
        if not self.detect_bigmap_open():
            self.try_toggle_map()
        player_pos = self.grab_player_pos()
        print(player_pos)
        key = "right"
        hexKeyCode = self.key_map[key]
        self.press_key(hexKeyCode)
        start_time = time.time()
        time.sleep(1.5)
        self.release_key(hexKeyCode)
        time_taken = time.time() - start_time
        player_pos_end = self.grab_player_pos()
        print(player_pos_end)
        x_travel = player_pos_end[0]-player_pos[0]
        print("Travelled {} pixels in {}s => {} pixels/sec".format(x_travel,
                                                                   time_taken, x_travel/time_taken))

    def try_toggle_map(self):
        pydirectinput.keyDown("m")
        time.sleep(0.05)
        pydirectinput.keyUp("m")
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
        # Then add each rect to the rects dict against name
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
        # print(self.rects)

    def detect_level_name(self):
        wincap = WindowCapture(self.gamename, [1121, 31, 1248, 44])
        existing_image = wincap.get_screenshot()
        filter = HsvFilter(0, 0, 0, 169, 34, 255, 0, 0, 0, 0)
        vision_limestone = Vision('plyr.jpg')
        # cv2.imwrite("testy2.jpg", existing_image)
        save_image = vision_limestone.apply_hsv_filter(existing_image, filter)
        # cv2.imwrite("testy3.jpg", save_image)
        gray_image = cv.cvtColor(save_image, cv.COLOR_BGR2GRAY)
        (thresh, blackAndWhiteImage) = cv.threshold(
            gray_image, 129, 255, cv.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        save_image = cv.cvtColor(inverted, cv.COLOR_GRAY2BGR)
        rgb = cv2.cvtColor(save_image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        return result

    def detect_bigmap_open(self):
        wincap = WindowCapture(self.gamename, custom_rect=[819, 263, 855, 264])
        image = wincap.get_screenshot()
        cv2.imwrite("testy.jpg", image)
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-2]]
        if a+b+c < 30:
            if d+e+f > 700:
                # print("Working")
                return True
        return False

    def grab_player_pos(self):
        if not self.map_rect:
            wincap = WindowCapture(self.gamename)
        else:
            wincap = WindowCapture(self.gamename, self.map_rect)
        filter = HsvFilter(34, 160, 122, 50, 255, 255, 0, 0, 0, 0)
        image = wincap.get_screenshot()
        save_image = self.filter_blackwhite_invert(filter, image)
        # cv2.imwrite("testy3.jpg", save_image)
        vision_limestone = Vision('plyr.jpg')
        rectangles = vision_limestone.find(
            save_image, threshold=0.31, epsilon=0.5)
        points = vision_limestone.get_click_points(rectangles)
        x, y = points[0]
        if not self.map_rect:
            return x, y
        else:
            x += wincap.window_rect[0]
            y += wincap.window_rect[1]
            return x, y

    def shift_channel(self, c, amount):
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

    def filter_blackwhite_invert(self, filter, existing_image):
        hsv = cv.cvtColor(existing_image, cv.COLOR_BGR2HSV)
        hsv_filter = filter
        # add/subtract saturation and value
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, hsv_filter.sAdd)
        s = self.shift_channel(s, -hsv_filter.sSub)
        v = self.shift_channel(v, hsv_filter.vAdd)
        v = self.shift_channel(v, -hsv_filter.vSub)
        hsv = cv.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR
        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)
        # now change it to greyscale
        grayImage = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # now change it to black and white
        (thresh, blackAndWhiteImage) = cv.threshold(
            grayImage, 67, 255, cv.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        inverted = cv.cvtColor(inverted, cv.COLOR_GRAY2BGR)
        return inverted
        # cv.imwrite(save_image, inverted)

    def load_key_dict(self):
        KEYBOARD_MAPPING = {
            '1': 0x02,
            '2': 0x03,
            '3': 0x04,
            '4': 0x05,
            '5': 0x06,
            '6': 0x07,
            '7': 0x08,
            '8': 0x09,
            '9': 0x0A,
            '0': 0x0B,
            'q': 0x10,
            'w': 0x11,
            'e': 0x12,
            'r': 0x13,
            't': 0x14,
            'y': 0x15,
            'u': 0x16,
            'i': 0x17,
            'o': 0x18,
            'p': 0x19,
            'a': 0x1E,
            's': 0x1F,
            'd': 0x20,
            'f': 0x21,
            'g': 0x22,
            'h': 0x23,
            'j': 0x24,
            'k': 0x25,
            'l': 0x26,
            'z': 0x2C,
            'x': 0x2D,
            'c': 0x2E,
            'v': 0x2F,
            'b': 0x30,
            'n': 0x31,
            'm': 0x32,
            'up': MapVirtualKey(0x26, MAPVK_VK_TO_VSC),
            'left': MapVirtualKey(0x25, MAPVK_VK_TO_VSC),
            'down': MapVirtualKey(0x28, MAPVK_VK_TO_VSC),
            'right': MapVirtualKey(0x27, MAPVK_VK_TO_VSC),
        }
        return KEYBOARD_MAPPING

    def press_key(self, hexKeyCode):
        if hexKeyCode in [75, 76, 77, 78]:
            # Do the primary key
            hexKeyCode2 = 0xE0
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, hexKeyCode2, 0x0008,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            # then the arrow itself
            ii_.ki = KeyBdInput(0, hexKeyCode, 0x0001,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(
                1, ctypes.pointer(x), ctypes.sizeof(x))
            SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

        else:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(
                1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_key(self, hexKeyCode):
        keybdFlags = 0x0008 | 0x0002
        if hexKeyCode in [75, 76, 77, 78]:
            keybdFlags |= 0x0001
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, hexKeyCode, keybdFlags,
                            0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

        if hexKeyCode in [75, 76, 77, 78] and ctypes.windll.user32.GetKeyState(0x90):
            hexKeyCode = 0xE0
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(
                1, ctypes.pointer(x), ctypes.sizeof(x))


if __name__ == "__main__":
    ppt = PlayerPositionTest()
    ppt.start()
