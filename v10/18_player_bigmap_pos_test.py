import cv2 as cv
from hsvfilter import HsvFilter, grab_object_preset
import numpy as np
import os
from vision import Vision
import time
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


class PlayerPositionTest():

    def __init__(self) -> None:
        self.rects = self.load_level_rects()

    def start(self):
        level_name = self.detect_level_name()
        # Then grab the right rect for the level
        rect = self.rects[level_name]
        # Then open the map
        while not self.detect_bigmap_open():
            # Press M
            pass
        print(self.grab_player_pos())
        # Then close the map
        while self.detect_bigmap_open():
            # Press M
            pass

    def load_level_rects(self):
        rects = {}
        return rects

    def detect_level_name(self):
        name = ""
        return name

    def detect_bigmap_open(self):
        return True

    def grab_player_pos(self):
        xrat, yrat = (0.5, 0.5)
        return xrat, yrat
