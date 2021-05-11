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
        pass

    def play_actions(self):
        with open("playback1.txt", 'r') as file:
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
