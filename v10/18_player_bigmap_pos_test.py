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
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class PlayerPositionTest():

    def __init__(self) -> None:
        self.rects = {}
        self.num_names = []
        self.load_level_rects()
        with open("gamename.txt") as f:
            self.gamename = f.readline()

    def start(self):
        level_name = self.detect_level_name()
        # Then grab the right rect for the level
        rect = self.rects[level_name]
        # Then open the map
        while not self.detect_bigmap_open():
            # Press M
            pass
        print(self.grab_player_pos())
        # Then close the map
        while self.detect_bigmap_open():
            # Press M
            pass

    def load_level_rects(self):
        # Load the translation from name to num
        with open("level_name_num.txt") as f:
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
                    self.rects[name] = rect
                    break
        print(self.rects)

    def detect_level_name(self):
        existing_image = WindowCapture(self.gamename, [1121, 31, 1248, 44])
        filter = HsvFilter(0, 0, 103, 89, 104, 255, 0, 0, 0, 0)
        vision = Vision('xprompt67filtv2.jpg')
        save_image = vision.apply_hsv_filter(existing_image, filter)
        rgb = cv2.cvtColor(save_image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        return result

    def detect_bigmap_open(self):
        return True

    def grab_player_pos(self):
        xrat, yrat = (0.5, 0.5)
        return xrat, yrat

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
        img = cv.imread(existing_image, cv.IMREAD_UNCHANGED)
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
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
