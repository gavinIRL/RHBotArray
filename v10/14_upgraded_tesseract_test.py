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


class UpgradedDetectTest():
    def __init__(self) -> None:
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        plyrname_rect = [165, 45, 320, 65]
        self.plyrname_wincap = WindowCapture(self.gamename, plyrname_rect)
        self.plyrname_filt = HsvFilter(0, 0, 103, 89, 104, 255, 0, 0, 0, 0)
        self.plyrmname_vision = Vision('xprompt67filtv2.jpg')

    def detect_name(self):
        # get an updated image of the game
        image = self.plyrname_wincap.get_screenshot()
        # pre-process the image
        image = self.plyrmname_vision.apply_hsv_filter(
            image, self.plyrname_filt)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # results = pytesseract.image_to_data(
        #     rgb, output_type=pytesseract.Output.DICT, lang='eng')
        # print(results["text"][4])
        result = pytesseract.image_to_string(
            rgb, lang='eng', config='--psm 7 --oem 3 -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')[:-2]
        print(result)


if __name__ == "__main__":
    udt = UpgradedDetectTest()
    udt.detect_name()
