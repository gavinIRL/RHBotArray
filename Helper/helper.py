# This file needs to include the following:
# 1 - ClearAll
# 2 - Questhandle
# 3 - Sell & Repair
from pynput.keyboard import Key, Listener, KeyCode
import time
import os
import cv2
import pydirectinput
from windowcapture import WindowCapture

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Helper():
    def __init__(self) -> None:
        self.listener = None
        self.unreleased_keys = []
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.game_wincap = WindowCapture(self.gamename)
        self.scaling = self.get_monitor_scaling()

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
        if key == KeyCode(char='0'):
            print("Exiting bot")
            os._exit(1)
        elif key == KeyCode(char='7'):
            if key not in self.unreleased_keys:
                self.unreleased_keys.append(key)
                os.popen('python sell_repair.py')
        elif key == KeyCode(char='8'):
            if key not in self.unreleased_keys:
                self.unreleased_keys.append(key)
                self.quest_handle.start_quest_handle()
        elif key == KeyCode(char='-'):
            if key not in self.unreleased_keys:
                self.unreleased_keys.append(key)
                self.clear_all()

    def on_release(self, key):
        if key == KeyCode(char='7'):
            self.unreleased_keys.remove(key)
        elif key == KeyCode(char='8'):
            self.unreleased_keys.remove(key)
        elif key == KeyCode(char='-'):
            self.unreleased_keys.remove(key)

    def clear_all(self):
        if self.detect_menu_open():
            self.close_esc_menu()
        elif self.detect_bigmap_open():
            self.close_map()

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
    h = Helper()
    h.start()
