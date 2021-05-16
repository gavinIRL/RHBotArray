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

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class IdentSellTest():
    def __init__(self, rarity_cutoff=1, last_row=True) -> None:
        # rarities are as follows:
        # nocolour=0, green=1, blue=2
        self.cutoff = rarity_cutoff
        # this is for whether lastrow in equip is protected
        # useful for characters levelling with next upgrades ready
        self.last_row = last_row
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.inventory_wincap = WindowCapture(
            self.gamename, [512, 277, 775, 430])

    def ident_sell_repair(self):
        self.open_store_if_necessary()
        # First go through all the equipment
        self.change_tab("Equipment")
        screenshot = self.inventory_wincap.get_screenshot()
        self.hover_mouse_all()
        non_empty = self.remove_empty(screenshot)
        rarities = self.identify_rarities_equip(non_empty)
        self.sell_equip(rarities)
        # Then go through all the other loot
        self.change_tab("Other")
        screenshot = self.inventory_wincap.get_screenshot()
        self.hover_mouse_all()
        non_empty = self.remove_empty(screenshot)
        junk_list = self.identify_items_other(non_empty)
        self.sell_other(junk_list)

    def open_store_if_necessary(self):
        # This will search to see if the inventory is open
        # in the correct spot and then click shop if not
        pass

    def change_tab(self, name):
        if name == "Equipment":
            x = 100
            y = 100
        elif name == "Other":
            x = 100
            y = 100
        ctypes.windll.user32.SetCursorPos(x, y)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)

    def hover_mouse_all(self):
        # make sure to move mouse out of way at end
        pass

    def remove_empty(self, screenshot):
        non_empty = []
        # format will be as follows of return list
        # x,y,r,g,b
        return non_empty

    def identify_rarities_equip(self, pixel_list):
        rarities = []
        # format will be as follows of return list
        # x,y,rarity
        return rarities

    def sell_equip(self, pixel_list):
        pass

    def identify_items_other(self, pixel_list):
        pass

    def sell_other(self, pixel_list):
        pass


if __name__ == "__main__":
    ist = IdentSellTest()
    ist.ident_sell_repair()
