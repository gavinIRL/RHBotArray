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

        # This is for correct mouse positioning
        self.game_wincap = WindowCapture(self.gamename)

        self.shop_check_wincap = WindowCapture(
            self.gamename, [274, 207, 444, 208])

        # These are for holding reference rgb values
        # Using sets as can then compare easily to other sets
        self.empty = {41, 45, 50}
        self.rar_green = {2, 204, 43}
        self.rar_blue = {232, 144, 5}
        self.rar_none = {24, 33, 48}
        self.junk_list = self.grab_junk_list()

    def grab_junk_list(self):
        jl = []
        with open("itemrgb.txt") as f:
            lines = f.readlines()
            for line in lines:
                _, rgb = line.split("|")
                r, g, b = rgb.split(",")
                jl.append({int(r), int(g), int(b)})
        return jl

    def ident_sell_repair(self):
        self.open_store_if_necessary()
        # First go through all the equipment
        self.change_tab("Equipment")
        time.sleep(0.1)
        screenshot = self.inventory_wincap.get_screenshot()
        # self.hover_mouse_all()
        non_empty = self.remove_empty(screenshot)
        junk_list = self.identify_rarities_equip(non_empty, screenshot)
        self.sell(junk_list)
        # Then go through all the other loot
        self.change_tab("Other")
        time.sleep(0.1)
        screenshot = self.inventory_wincap.get_screenshot()
        # self.hover_mouse_all()
        non_empty = self.remove_empty(screenshot)
        junk_list = self.identify_items_other(non_empty, screenshot)
        self.sell(junk_list)
        # and finally repair gear
        self.repair()

    def open_store_if_necessary(self):
        # This will search to see if the inventory is open
        # in the correct spot and then click shop if not
        screenshot = self.shop_check_wincap.get_screenshot()
        pix1 = screenshot[0, 0]
        pix1 = int(pix1[0]) + int(pix1[1]) + int(pix1[2])
        pix2 = screenshot[0, 169]
        pix2 = int(pix2[0]) + int(pix2[1]) + int(pix2[2])
        if pix1 == 103 and pix2 == 223:
            pass
            # print("It matches")
        else:
            # need to open the store
            self.game_wincap.update_window_position(border=False)
            offsetx = self.game_wincap.window_rect[0] + 534
            offsety = self.game_wincap.window_rect[1] + 277
            ctypes.windll.user32.SetCursorPos(offsetx+610, offsety-10)
            ctypes.windll.user32.mouse_event(
                0x0002, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(
                0x0004, 0, 0, 0, 0)

    def change_tab(self, name):
        self.game_wincap.update_window_position(border=False)
        x = self.game_wincap.window_rect[0] + 534-60
        if name == "Equipment":
            y = self.game_wincap.window_rect[1] + 277 - 15
        elif name == "Other":
            y = self.game_wincap.window_rect[1] + 277 + 44
        ctypes.windll.user32.SetCursorPos(x, y)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)

    def hover_mouse_all(self):
        self.game_wincap.update_window_position(border=False)
        offsetx = self.game_wincap.window_rect[0] + 534
        offsety = self.game_wincap.window_rect[1] + 277
        for i in range(4):
            for j in range(6):
                x = offsetx+j*44
                y = offsety+i*44
                ctypes.windll.user32.SetCursorPos(x, y)
                time.sleep(0.001)
        ctypes.windll.user32.SetCursorPos(offsetx, offsety-70)

        ctypes.windll.user32.SetCursorPos(offsetx+610, offsety-10)

    def remove_empty(self, screenshot):
        non_empty = []
        for i in range(4):
            for j in range(6):
                colour = set(screenshot[i*44, 22+j*44])
                if colour != self.empty:
                    non_empty.append([i, j])
        # format will be as follows of return list
        # x,y,r,g,b
        return non_empty

    def identify_rarities_equip(self, rowcol_list, screenshot):
        junk = []
        for rowcol in rowcol_list:
            colour = set(screenshot[rowcol[0]*44, rowcol[1]*44])
            # print(colour)
            if colour == self.rar_none:
                junk.append([rowcol[0], rowcol[1]])
            elif colour == self.rar_green:
                if self.cutoff >= 1:
                    junk.append([rowcol[0], rowcol[1]])
            elif colour == self.rar_green:
                if self.cutoff >= 2:
                    junk.append([rowcol[0], rowcol[1]])
        # format will be as follows of return list
        # x,y corresponding to row,col
        return junk

    def identify_items_other(self, rowcol_list, screenshot):
        junk = []
        for rowcol in rowcol_list:
            colour = set(screenshot[rowcol[0]*44, 22+rowcol[1]*44])
            if colour in self.junk_list:
                junk.append([rowcol[0], rowcol[1]])
        # format will be as follows of return list
        # x,y corresponding to row,col
        return junk

    def sell(self, rowcol_list):
        offsetx = self.game_wincap.window_rect[0] + 534
        offsety = self.game_wincap.window_rect[1] + 277
        for item in rowcol_list:
            x = offsetx+item[1]*44
            y = offsety+item[0]*44
            ctypes.windll.user32.SetCursorPos(x, y)
            time.sleep(0.25)
            ctypes.windll.user32.mouse_event(
                0x0008, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(
                0x0010, 0, 0, 0, 0)

    def repair(self):
        self.game_wincap.update_window_position(border=False)
        offsetx = self.game_wincap.window_rect[0] + 534
        offsety = self.game_wincap.window_rect[1] + 277
        ctypes.windll.user32.SetCursorPos(offsetx-310, offsety+325)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)
        ctypes.windll.user32.SetCursorPos(offsetx+0, offsety+180)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)
        # this is if everything is already repaired
        ctypes.windll.user32.SetCursorPos(offsetx+100, offsety+180)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)


if __name__ == "__main__":
    ist = IdentSellTest()
    ist.ident_sell_repair()
    # ist.hover_mouse_all()
    # ist.open_store_if_necessary()
