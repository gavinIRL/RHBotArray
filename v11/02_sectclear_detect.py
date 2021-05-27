import time
import os
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
from windowcapture import WindowCapture
import cv2
from threading import Thread
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class ScreenshotGrabber5Sec():
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
        if key == keyboard.Key.f11:
            os._exit(1)

    def on_release(self, key):
        if key == keyboard.Key.f10:
            print("Starting sectclear check")
            t = Thread(target=self.sectclear_checker)
            t.start()

    def sectclear_checker(self):
        with open("gamename.txt") as f:
            gamename = f.readline()
        wincap = WindowCapture(gamename, custom_rect=[
            464+156, 640, 464+261, 641])
        while True:
            image = wincap.get_screenshot()
            a, b, c = [int(i) for i in image[0][0]]
            d, e, f = [int(i) for i in image[0][-1]]
            if a+b+c > 700 and d+e+f > 700:
                print("Detected sect clear")
                break
            else:
                time.sleep(0.1)


if __name__ == "__main__":
    ssg = ScreenshotGrabber5Sec()
    ssg.start()
