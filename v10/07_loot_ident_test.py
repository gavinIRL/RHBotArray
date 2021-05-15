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
        xratlist = [0.41929, 0.45472, 0.49016, 0.52165, 0.55709, 0.59252]
        yratlist = [0.36332, 0.42161, 0.47431, 0.53360]
        loot_vision = Vision("xprompt67filtv2.jpg")
        filt = HsvFilter(0, 0, 102, 45, 65, 255, 0, 0, 0, 0)
        start_time = time.time()
        for i, x in enumerate(xratlist):
            for j, y in enumerate(yratlist):
                relx = int(self.game_wincap.w * x)
                rely = int(self.game_wincap.h * y)
                truex = relx + self.game_wincap.window_rect[0]
                truey = rely + self.game_wincap.window_rect[1]
                ctypes.windll.user32.SetCursorPos(truex, truey)
                time.sleep(0.05)
                y2 = rely+180
                if y2 > 465:
                    y2 = 465
                wincap = WindowCapture(
                    self.gamename, [relx+35, rely+10, relx+310, y2])
                image = wincap.get_screenshot()
                # cv2.imshow('Filtered', image)
                image = loot_vision.apply_hsv_filter(
                    image, filt)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pytesseract.image_to_data(
                    rgb, output_type=pytesseract.Output.DICT, lang='eng')
                # if not "empty" in results["text"]:
                #     print("Found non-empty cell at {},{}".format(i, j))
                res = list(filter(None, results["text"]))
                if res:
                    print("Found non-empty cell at {},{}".format(i, j))
                    print(res)
                # time.sleep(0.1)

        end_time = time.time()
        print("Time taken: {}s".format(end_time-start_time))


if __name__ == "__main__":
    lit = LootIdentTest()
    lit.start()
