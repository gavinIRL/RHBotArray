import time
import os
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard


class KeyCodeChecker():
    def __init__(self) -> None:
        self.listener = None

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
        print(key)

    def on_release(self, key):
        pass


if __name__ == "__main__":
    kcc = KeyCodeChecker()
    kcc.start()
