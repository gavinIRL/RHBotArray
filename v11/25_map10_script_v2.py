# This file will automatically run through map 10
import time
import os
import numpy as np
import cv2
import ctypes
import logging
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter
import pydirectinput
from custom_input import CustomInput
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logging.getLogger().setLevel(logging.ERROR)


class Map10_MS30():
    def __init__(self):
        self.rooms = self.load_map_rooms()
        self.speed = 22.5
        self.map_rect = [561, 282, 1111, 666]
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.game_wincap = WindowCapture(self.gamename)
        # This is for determining wait time before next clear
        self.last_clear = 0
        self.clearskill_cd = 8.9
        # This is for keeping track of where player is
        self.current_room = 0

    def load_map_rooms(self):
        # Temporary, will be replace by objects later
        # that will load from a database file
        return_list = []
        filepath = os.path.dirname(
            os.path.abspath(__file__)) + "/levels/map10.txt"
        with open(filepath) as file:
            lines = file.readlines()
        for line in lines:
            return_list.append(line.split(","))
        return return_list

    def start(self):
        # Using placeholder individual methods for now
        self.perform_room1()
        self.perform_room2()

    def perform_room1(self):
        time.sleep(2)
        room = self.rooms[0]
        self.move_to(int(room[1]), int(room[2]))
        time.sleep(0.4)
        self.roomclear_skill()
        time.sleep(0.6)
        start_time = time.time()
        while not self.sect_clear_detected():
            if time.time() > start_time + 4:
                self.aim_am_enemies()
                self.continue_clear()
                if time.time() > start_time + 12:
                    os._exit()
            else:
                self.continue_clear()

    def perform_room2(self):
        room = self.rooms[0]
        self.move_to(int(room[3]), int(room[4]))
        time.sleep(0.4)
        # Now calculate the travel time to figure out
        # How long to sleep before moving to room2 spot
        targetx = self.rooms[1][1]
        targety = self.rooms[1][2]
        travel_time = self.calculate_travel_time(targetx, targety)
        sleep_time = self.last_clear + self.clearskill_cd - time.time() - travel_time
        if sleep_time > 0:
            time.sleep(sleep_time)
        room = self.rooms[1]
        self.move_to(int(room[1]), int(room[2]), yfirst=False)
        time.sleep(0.6)
        self.roomclear_skill()
        time.sleep(0.6)
        start_time = time.time()
        while not self.sect_clear_detected():
            if time.time() > start_time + 4:
                calc_time = time.time()
                self.aim_am_enemies()
                print("Total aim time = {}".format(time.time()-calc_time))
                self.continue_clear()
                if time.time() > start_time + 12:
                    os._exit()
            else:
                self.continue_clear()
