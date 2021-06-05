import time
import os
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard


class KeyCodeChecker():
    def __init__(self) -> None:
        self.listener = None
        self.start_time = 0
        self.unreleased_keys = []

    def start(self):
        self.start_keypress_listener()
        self.start_time = time.time()
        while True:
            time.sleep(0.5)

    def start_keypress_listener(self):
        if self.listener == None:
            self.listener = Listener(on_press=self.on_press,
                                     on_release=self.on_release)
            self.listener.start()

    def on_press(self, key):
        if key not in self.unreleased_keys:
            print("key:{}, time:{}".format(key, time.time()-self.start_time))
        if key == keyboard.Key.f11:
            os._exit(1)
        self.unreleased_keys.append(key)

    def on_release(self, key):
        self.unreleased_keys.remove(key)
        print("key:{}, time:{}".format(key, time.time()-self.start_time))


if __name__ == "__main__":
    kcc = KeyCodeChecker()
    kcc.start()
