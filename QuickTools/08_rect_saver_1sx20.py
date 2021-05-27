import time
import os
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
from windowcapture import WindowCapture
import cv2
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
        if key == keyboard.Key.f10:
            print("Got here")
            with open("gamename.txt") as f:
                gamename = f.readline()
            wincap = WindowCapture(gamename, custom_rect=[464, 600, 855, 680])
            counter = 0
            while counter < 20:
                counter += 1
                image = wincap.get_screenshot()
                cv2.imwrite("C:\\Games\\"+str(counter)+".jpg", image)
                time.sleep(0.05)

        if key == keyboard.Key.f11:
            os._exit(1)

    def on_release(self, key):
        pass


if __name__ == "__main__":
    ssg = ScreenshotGrabber5Sec()
    ssg.start()
