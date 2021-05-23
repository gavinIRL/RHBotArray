# This file will detect (or at least wait until does detect)
# specific click events on screen
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


class QuestHandleTest():
    def __init__(self) -> None:
        self.listener = None

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

        self.quest_rect = [310, 160, 1055, 650]
        self.quest_wincap = WindowCapture(gamename, self.quest_rect)

    def start(self):
        time.sleep(2)
        self.start_keypress_listener()
        while True:
            time.sleep(0.5)

    def start_keypress_listener(self):
        if self.listener == None:
            self.listener = Listener(on_press=self.on_press,
                                     on_release=self.on_release)
            self.listener.start()

    def on_press(self, key):
        if key == keyboard.Key.f12:
            if self.check_for_quest():
                print("Found and clicked")
            else:
                print("Didn't find anything")
            # while not self.check_for_accept():
            #     time.sleep(0.01)

    def on_release(self, key):
        if key == keyboard.Key.f11:
            os._exit(1)

    def convert_and_click(self, x, y, rect):
        # this will convert a click at a specific subrectangle point
        # into a proper click point and then click it
        self.game_wincap.update_window_position(border=False)
        truex = int(x + self.game_wincap.window_rect[0] + rect[0])
        truey = int(y + self.game_wincap.window_rect[1] + rect[1])
        ctypes.windll.user32.SetCursorPos(truex, truey)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)

    def check_for_quest(self):
        # Copy-paste checklist:
        # wincap, filter, phrase, rect, return
        image = self.quest_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        # cv2.imwrite("testy4.jpg", image)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=Quest'
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng', config=tess_config)
        # print(results)
        detection = False
        for i in range(0, len(results["text"])):
            if "Quest" in results["text"][i]:
                # at this point need to grab the centre of the rect
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                # and then click at this position
                self.convert_and_click(x, y, self.quest_rect)
                detection = True
                break
        # If didn't find an accept then go to the next one
        if not detection:
            # This will branch downwards until eventually detects something
            # at which point it will return true and satisfy the listener condition
            # However if it goes through all the checks and doesn't find anything
            # it will return false which will cause the listener condition to loop again
            return False
        else:
            return True


if __name__ == "__main__":
    qht = QuestHandleTest()
    qht.start()
