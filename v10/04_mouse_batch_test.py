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

# This will record keypresses and actions in the following format:
# button|type|time|posx,posy\n


class BatchRecordTest():
    def __init__(self) -> None:
        self.listener = None
        self.recording_ongoing = False
        self.start_time = 0
        self.batch = ""
        self.pressed_keys = []
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.game_wincap = WindowCapture(self.gamename)
        self.scaling = ClientUtils.get_monitor_scaling()

    def start(self):
        self.start_keypress_listener()
        while True:
            time.sleep(0.5)
            if self.recording_ongoing:
                if time.time() > self.start_time + 10:
                    # need to first check if there are still keys pressed down
                    if len(self.pressed_keys) == 0:
                        print("Sending batch now due to time")
                        self.start_time = time.time()
                        # print(self.batch)
                        self.batch = ""

    def start_mouse_listener(self):
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click)
        self.mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        # Need to then check if the click was in the right window
        # Do this by checking if window focused
        if GetWindowText(GetForegroundWindow()) == self.gamename:
            # when pressed is False, that means it's a release event.
            # let's listen only to mouse click releases
            if not pressed:
                # Need to get the ratio compared to window top left
                # This will allow common usage on other size monitors
                # print("x={}, y={}".format(x, y))
                xratio, yratio = self.convert_click_to_ratio(x, y)
                # print("xrat={}, yrat={}".format(xratio, yratio))
                self.batch += str(button) + "|click|" + \
                    "{:.3f}".format((time.time() - self.start_time)) + \
                    "|"+"{},{}\n".format(xratio, yratio)

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
            if key not in self.pressed_keys:
                self.batch += str(key) + "|keyDown|" + \
                    "{:.3f}".format((time.time() - self.start_time)) + "|0,0\n"
                self.pressed_keys.append(key)

    def on_release(self, key):
        if key == keyboard.Key.f12:
            pass
        elif key == keyboard.Key.f11:
            os._exit(1)
        elif self.recording_ongoing:
            # log the key release also
            self.batch += str(key) + "|keyUp|" + \
                "{:.3f}".format((time.time() - self.start_time)) + "|0,0\n"
            try:
                self.pressed_keys.remove(key)
            except:
                print("Error in key release of "+str(key))
            # if batch gets too big then send
            if len(self.batch) > 2500:
                # need to first check if there are still keys pressed down
                if len(self.pressed_keys) == 0:
                    print("Sending batch now due to size")
                    self.start_time = time.time()
                    # print(self.batch)
                    self.batch = ""

    def convert_click_to_ratio(self, truex, truey):
        # This will grab the current rectangle coords of game window
        # and then turn the click values into a ratio of positions
        # versus the game window
        self.game_wincap.update_window_position(border=False)
        # Turn the screen pos into window pos
        relx = (truex - self.game_wincap.window_rect[0]) * self.scaling
        rely = (truey - self.game_wincap.window_rect[1]) * self.scaling
        # Then convert to a ratio
        ratx = relx/(self.game_wincap.w*self.scaling)
        raty = rely/(self.game_wincap.h*self.scaling)
        return ratx, raty


if __name__ == "__main__":
    brt = BatchRecordTest()
    brt.start()
