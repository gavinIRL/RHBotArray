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


class LootIdentTest():
    def __init__(self) -> None:
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.game_wincap = WindowCapture(self.gamename)

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

    def start(self):
        xratlist = [0.12856, 0.15189, 0.17522, 0.19855, 0.21928, 0.24520]
        yratlist = [0.12458, 0.16221, 0.19983, 0.23328]
        loot_vision = Vision("xprompt67filtv2.jpg")
        filt = HsvFilter(0, 0, 0, 25, 82, 71, 0, 0, 0, 0)
        start_time = time.time()
        for i, x in enumerate(xratlist):
            for j, y in enumerate(yratlist):
                truex, truey = self.convert_ratio_to_click(x, y)
                wincap = WindowCapture(
                    self.gamename, [truex-25, truey-25, truex+25, truey+25])
                image = wincap.get_screenshot()
                # cv2.imshow('Filtered', image)
                image = loot_vision.apply_hsv_filter(
                    image, filt)
                image = cv2.bitwise_not(image)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pytesseract.image_to_data(
                    rgb, output_type=pytesseract.Output.DICT, lang='eng')
                # if not "empty" in results["text"]:
                #     print("Found non-empty cell at {},{}".format(i, j))
                res = list(filter(None, results["text"]))
                print(res)

        end_time = time.time()
        print("Time taken: {}s".format(end_time-start_time))


if __name__ == "__main__":
    lit = LootIdentTest()
    lit.start()
