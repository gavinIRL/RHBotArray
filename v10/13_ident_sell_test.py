import socket
import select
import threading
import pydirectinput
import time
import subprocess
import os
from win32api import GetSystemMetrics
from windowcapture import WindowCapture
import ctypes
from cryptography.fernet import Fernet
from vision import Vision
from hsvfilter import grab_object_preset, HsvFilter
import cv2
import pytesseract
from quest_handle import QuestHandle


class IdentSellTest():
    def __init__(self) -> None:
        pass

    def start(self):
        pass

    def change_tab(self, name):
        pass

    def hover_mouse_all(self):
        pass

    def remove_empty(self, screenshot):
        pass

    def identify_rarities(self, pixel_list):
        pass

    def sell_junk(self, pixel_list):
        pass

    def identify_items(self, pixel_list):
        pass


if __name__ == "__main__":
    ist = IdentSellTest()
    ist.start()
