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

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class QuestHandleTest():
    def __init__(self) -> None:
        self.listener == None

        with open("gamename.txt") as f:
            gamename = f.readline()
        self.white_text_filter = HsvFilter(
            0, 0, 102, 45, 65, 255, 0, 0, 0, 0)
        self.yellow_text_filter = HsvFilter(
            16, 71, 234, 33, 202, 255, 0, 0, 0, 0)
        self.blue_text_filter = HsvFilter(
            94, 188, 255, 137, 255, 255, 0, 0, 0, 0)

        self.vision = Vision('xprompt67filtv2.jpg')

        self.accept_rect = [210, 60, 1455, 650]
        self.accept_wincap = WindowCapture(gamename, self.accept_rect)

        self.skip_rect = [210, 60, 1455, 650]
        self.skip_wincap = WindowCapture(gamename, self.skip_rect)

        self.next_rect = [210, 60, 1455, 650]
        self.next_wincap = WindowCapture(gamename, self.next_rect)

        self.quest_rect = [210, 60, 1455, 650]
        self.quest_wincap = WindowCapture(gamename, self.quest_rect)

        self.xprompt_rect = [210, 60, 1455, 650]
        self.xprompt_wincap = WindowCapture(gamename, self.xprompt_rect)

    def start(self):
        while True:
            time.sleep(0.5)

    def start_keypress_listener(self):
        if self.listener == None:
            self.listener = Listener(on_press=self.on_press,
                                     on_release=self.on_release)
            self.listener.start()

    def on_press(self, key):
        if key == keyboard.Key.f12:
            while not self.check_for_accept():
                # this will loop through checking for everything
                # until it finds something, otherwise sleeps
                # the full loops themselves make the sleep time redundant
                time.sleep(0.01)

    def on_release(self, key):
        if key == keyboard.Key.f11:
            os._exit()

    def convert_and_click(self, x, y, rect):
        # this will convert a click at a specific subrectangle point
        # into a proper click point and then click it
        pass

    def check_for_accept(self):
        # Copy-paste checklist:
        # wincap, vision, filter, phrase, rect, return
        image = self.accept_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Accept" in results["text"][i]:
                # at this point need to grab the centre of the rect
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                # and then click at this position
                self.convert_and_click(x, y, self.accept_rect)
                detection = True
                break
        # If didn't find an accept then go to the next one
        if not detection:
            # This will branch downwards until eventually detects something
            # at which point it will return true and satisfy the listener condition
            # However if it goes through all the checks and doesn't find anything
            # it will return false which will cause the listener condition to loop again
            return self.check_for_skip()
        else:
            return True

    def check_for_skip(self):
        # Copy-paste checklist:
        # wincap, filter, phrase, rect, return
        image = self.skip_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Skip" in results["text"][i]:
                # at this point need to grab the centre of the rect
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                # and then click at this position
                self.convert_and_click(x, y, self.skip_rect)
                detection = True
                break
        # If didn't find an accept then go to the next one
        if not detection:
            # This will branch downwards until eventually detects something
            # at which point it will return true and satisfy the listener condition
            # However if it goes through all the checks and doesn't find anything
            # it will return false which will cause the listener condition to loop again
            return self.check_for_next()
        else:
            return True

    def check_for_next(self):
        # Copy-paste checklist:
        # wincap, filter, phrase, rect, return
        image = self.next_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Next" in results["text"][i]:
                # at this point need to grab the centre of the rect
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                # and then click at this position
                self.convert_and_click(x, y, self.next_rect)
                detection = True
                break
        # If didn't find an accept then go to the next one
        if not detection:
            # This will branch downwards until eventually detects something
            # at which point it will return true and satisfy the listener condition
            # However if it goes through all the checks and doesn't find anything
            # it will return false which will cause the listener condition to loop again
            return self.check_for_quest()
        else:
            return True

    def check_for_quest(self):
        # Copy-paste checklist:
        # wincap, filter, phrase, rect, return
        image = self.quest_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.white_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
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
            return self.check_for_xprompt()
        else:
            return True

    def check_for_xprompt(self):
        # Copy-paste checklist:
        # wincap, filter, phrase, rect, return
        image = self.xprompt_wincap.get_screenshot()
        image = self.vision.apply_hsv_filter(
            image, self.blue_text_filter)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng')
        detection = False
        for i in range(0, len(results["text"])):
            if "Press" in results["text"][i]:
                # at this point need to grab the centre of the rect
                x = results["left"][i] + (results["width"][i]/2)
                y = results["top"][i] + (results["height"][i]/2)
                # and then click at this position
                self.convert_and_click(x, y, self.xprompt_rect)
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
