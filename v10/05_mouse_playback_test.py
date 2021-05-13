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

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class BatchPlaybackTest():
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

    def play_actions(self):
        with open("playback2.txt", 'r') as file:
            # parse the file
            data = file.readlines()
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
                    print("Would press {} down now".format(line[0]))
                elif line[1] == "click":
                    x, y = line[3].split(",")
                    print("Would click at {},{} now".format(x, y))
                try:
                    next_action = converted[idx + 1]
                except IndexError:
                    # this was the last action in the list
                    break
                elapsed_time = float(next_action[2]) - float(line[2])
                elapsed_time -= (time.time() - action_start_time)
                if elapsed_time < 0:
                    elapsed_time = 0

                time.sleep(elapsed_time)


if __name__ == "__main__":
    bpt = BatchPlaybackTest()
    bpt.play_actions()
