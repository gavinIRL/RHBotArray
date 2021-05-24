# This file needs to include the following:
# 1 - ClearAll
# 2 - Questhandle
# 3 - Sell & Repair
from pynput.keyboard import Key, Listener, KeyCode
import time


class Helper():
    def __init__(self) -> None:
        self.listener = None
        self.unreleased_keys = []

    def start(self):
        self.start_keypress_listener()
        while True:
            time.sleep(0.5)

    def start_keypress_listener(self):
        if self.listener == None:
            if not self.test:
                self.listener = Listener(on_press=self.on_press,
                                         on_release=self.on_release)
            else:
                self.listener = Listener(on_press=self.on_press_test,
                                         on_release=self.on_release_test)
            self.listener.start()


if __name__ == "__main__":
    h = Helper()
    h.start()
