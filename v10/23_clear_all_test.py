from hsvfilter import HsvFilter, grab_object_preset
import numpy as np
import os
from vision import Vision
import time
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
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


class ClearAllTest():
    def __init__(self) -> None:
        self.scaling = ClientUtils.get_monitor_scaling()
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.game_wincap = WindowCapture(self.gamename)

    def start(self):
        time.sleep(2.5)
        if self.detect_menu_open():
            self.close_esc_menu()
        elif self.detect_bigmap_open():
            self.close_map()

    def detect_bigmap_open(self):
        wincap = WindowCapture(self.gamename, custom_rect=[819, 263, 855, 264])
        image = wincap.get_screenshot()
        # cv2.imwrite("testy.jpg", image)
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-2]]
        if a+b+c < 30:
            if d+e+f > 700:
                return True
        return False

    def detect_menu_open(self):
        wincap = WindowCapture(self.gamename, custom_rect=[595, 278, 621, 479])
        image = wincap.get_screenshot()
        cv2.imwrite("testy.jpg", image)
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        # print("Sum abc:{}, def:{}".format(a+b+c, d+e+f))
        if a+b+c > 700:
            if d+e+f > 700:
                return True
        return False

    def close_map(self):
        pydirectinput.click(
            int(self.scaling*859+self.game_wincap.window_rect[0]), int(self.scaling*260+self.game_wincap.window_rect[1]))

    def close_esc_menu(self):
        pydirectinput.click(
            int(self.scaling*749+self.game_wincap.window_rect[0]), int(self.scaling*280+self.game_wincap.window_rect[1]))


if __name__ == "__main__":
    cat = ClearAllTest()
    cat.start()
