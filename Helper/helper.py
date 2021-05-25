# This file needs to include the following:
# 1 - ClearAll
# 2 - Questhandle
# 3 - Sell & Repair
from pynput.keyboard import Key, Listener, KeyCode
import time
import os


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
            self.listener = Listener(on_press=self.on_press,
                                     on_release=self.on_release)
            self.listener.start()

    def on_press(self, key):
        if key == KeyCode(char='0'):
            print("Exiting bot")
            os._exit(1)
        elif key == KeyCode(char='7'):
            os.popen('python sell_repair.py')
        elif key == KeyCode(char='8'):
            self.quest_handle.start_quest_handle()
        elif key == KeyCode(char='-'):
            self.clear_all()

    def on_release(self, key):
        pass


if __name__ == "__main__":
    h = Helper()
    h.start()
