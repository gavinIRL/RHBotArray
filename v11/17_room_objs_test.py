# This file will test how to best store data on each room
# Will preferably load information from a single file
from threading import Thread
import time
import os
import numpy as np
import cv2
import math
import ctypes
import logging
from fuzzywuzzy import fuzz
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter
import pydirectinput
from custom_input import CustomInput
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logging.getLogger().setLevel(logging.ERROR)


class Room():
    def __init__(self, line: str) -> None:
        # Format of each line in the file should be as follows
        # coords_n | coords_n+1 # action_n | action_n+1 # tags
        # format coords is x,y
        # ------------------------------------
        # list actions is as follows:
        # clear,dir - position to perform clear from, point left
        # boss,dir - position to perform boss attacks from
        # exit - position to exit room from
        # chest,dir - position to attack chest, point left
        # repos,dir,5 - position to reposition to, point left, after seconds
        # loot - position to attempt to loot from
        # wypt - this is a travel waypoint only
        # ------------------------------------
        # list of tags is as follows
        # nxtbss,dir - next room is the boss room, hold l to enter
        # curbss - this room is the boss room
        coords, actions, tags = line.split("#")
        self.action_list = []
        self.coord_list = []
        self.tags = []
        for coord in coords.split("|"):
            x, y = coord.split(",")
            self.coord_list.append((int(x), int(y)))
        for action in actions.split("|"):
            self.action_list.append(action)
        for tag in tags.split("|"):
            self.tags.append(tag)


class RoomTest():
    dir_list = ["l", "r", "u", "d"]

    def __init__(self) -> None:
        # Add a timestamp to catch if have gotten stuck
        self.last_event_time = time.time()

    def room_handler(self, room: Room):
        # Check through the tags first
        curbss = False if not "curbss" in "".join(room.tags) else True
        nxtbss = False if not "nxtbss" in "".join(room.tags) else True
        repos = False if not "repos" in "".join(room.action_list) else True
        sect_cleared = False
        # Then go through the actions and carry them out
        for i, action in enumerate(room.action_list):
            self.last_event_time = time.time()
            # Need to check if reposition is the next item
            repos_time = False
            if repos:
                next = room.action_list[i+1]
                if "repos" in next:
                    _, _, repos_time = next.split(",")
            coords = room.coord_list[i]
            if "clear" in action:
                _, dir = action.split(",")
                outcome = self.perform_clear(coords, dir, repos_time)
                if outcome:
                    sect_cleared = True
            elif "boss" in action:
                _, dir = action.split(",")
                outcome = self.perform_boss(coords, dir, repos_time, curbss)
                if outcome:
                    sect_cleared = True
            elif "exit" in action:
                outcome = self.perform_exit(coords, nxtbss)
            elif "chest" in action:
                _, dir = action.split(",")
                outcome = self.perform_chest(coords, dir)
            elif "repos" in action:
                _, dir, sec = action.split(",")
                if not sect_cleared:
                    self.perform_repos(coords, dir)
            elif "loot" in action:
                self.perform_loot(coords, curbss)
            elif "wypt" in action:
                self.perform_wypt(coords)

    def perform_clear(self, coords, dir, repos=False):
        pass

    def perform_boss(self, coords, dir, repos=False, curbss=False):
        pass

    def perform_exit(self, coords, nxtbss=False):
        pass

    def perform_chest(self, coords, dir):
        pass

    def perform_repos(self, coords, dir):
        pass

    def perform_loot(self, coords, currbss=False):
        pass

    def perform_wypt(self, coords):
        pass


def load_rooms(filename):
    with open(filename) as f:
        lines = f.readlines()
    list_rooms = []
    for line in lines:
        list_rooms.append(Room(line))
    return list_rooms


filename = os.path.dirname(
    os.path.abspath(__file__)) + "/levels/map10updated.txt"
rooms = load_rooms(filename)
room1 = rooms[0]
print(room1.action_list)
