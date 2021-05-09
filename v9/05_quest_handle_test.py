# This file will detect (or at least wait until does detect)
# specific click events on screen
import time
import os
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard


class QuestHandleTest():
    def __init__(self) -> None:
        self.listener == None

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
            self.check_for_accept()

    def on_release(self, key):
        if key == keyboard.Key.f11:
            os._exit()

    def check_for_accept(self):
        pass

    def check_for_skip(self):
        pass

    def check_for_next(self):
        pass

    def check_for_xprompt(self):
        pass

    def check_for_quest(self):
        pass
