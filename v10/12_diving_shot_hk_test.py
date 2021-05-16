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


class DSTest():
    def __init__(self) -> None:
        self.start_keypress_listener()

    def start_keypress_listener(self):
        self.listener = Listener(
            on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        print(key)
        if key == keyboard.Key.f12:
            os._exit(1)

    def on_release(self, key):
        pass
