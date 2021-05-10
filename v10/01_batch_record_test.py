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

# This will record keypresses and actions in the following format:
# button|type|time|posx,posy\n


class BatchRecordTest():
    def __init__(self) -> None:
        self.listener = None
        self.recording_ongoing = False
        self.start_time = 0
        self.batch = ""

    def start(self):
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
            self.recording_ongoing = not self.recording_ongoing
            if self.recording_ongoing:
                print("Starting recording...")
                self.start_time = time.time()
            if not self.recording_ongoing:
                # would send the batch at this point
                # with the delay if required
                print(self.batch)
                # and then clear the batch
                self.batch = ""
                print("Batch finished")
        elif self.recording_ongoing:
            # Need to log the action and add to batch for sending later
            self.batch += str(key) + "|keyDown|" + \
                "{:.3f}".format((time.time() - self.start_time)) + "|0,0\n"

    def on_release(self, key):
        if key == keyboard.Key.f12:
            pass
        elif key == keyboard.Key.f11:
            os._exit(1)
        elif self.recording_ongoing:
            # log the key release also
            self.batch += str(key) + "|keyUp|" + \
                "{:.3f}".format((time.time() - self.start_time)) + "|0,0\n"


if __name__ == "__main__":
    brt = BatchRecordTest()
    brt.start()
