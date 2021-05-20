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
        self.map_rect = None
        self.level_name = None
        self.rects = {}
        self.num_names = []
        self.load_level_rects()
        with open("gamename.txt") as f:
            self.gamename = f.readline()

    def start(self):
        time.sleep(3)
        print("Starting")
        self.level_name = self.detect_level_name()
        # Then grab the right rect for the level
        self.map_rect = self.string_to_rect(self.rects[self.level_name])
        # Then open the map
        time.sleep(0.07)
        while not self.detect_bigmap_open():
            self.try_toggle_map()
        player_pos = self.grab_player_pos()
        print(player_pos)
        # Then close the map
        while self.detect_bigmap_open():
            self.try_toggle_map()
            break

    def try_toggle_map(self):
        pydirectinput.keyDown("m")
        time.sleep(0.08)
        pydirectinput.keyUp("m")
        time.sleep(0.12)

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
                    self.rects[name.rstrip()] = rect.rstrip()
                    break
        # print(self.rects)

    def detect_level_name(self):
        wincap = WindowCapture(self.gamename, [1121, 31, 1248, 44])
        existing_image = wincap.get_screenshot()
        save_image = existing_image
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
        wincap = WindowCapture(self.gamename, self.map_rect)
        filter = HsvFilter(34, 160, 122, 50, 255, 255, 0, 0, 0, 0)
        image = wincap.get_screenshot()
        save_image = self.filter_blackwhite_invert(filter, image)
        vision_limestone = Vision('plyr.jpg')
        rectangles = vision_limestone.find(
            save_image, threshold=0.31, epsilon=0.5)
        points = vision_limestone.get_click_points(rectangles)
        if len(points) == 1:
            x, y = points[0]
            return x, y
        return False

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


if __name__ == "__main__":
    ppt = PlayerPositionTest()
    start = time.time()
    ppt.start()
    print("Time taken: {}s".format(time.time() - start))
