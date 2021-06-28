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


class Map10_MS30():
    def __init__(self, roomdata):
        self.rooms = roomdata
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
        # For aiming at enemies
        self.enemy_minimap_filter = HsvFilter(
            0, 128, 82, 8, 255, 255, 0, 66, 30, 34)
        enemy_custom_rect = [1094, 50, 1284, 210]
        self.enemy_minimap_wincap = WindowCapture(
            self.gamename, enemy_custom_rect)
        self.enemy_minimap_vision = Vision('enemy67.jpg')
        # Var for tracking gold progress
        self.gold = 860000

    def start(self, repeat=False):
        time.sleep(1.5)
        while not Events.detect_in_dungeon():
            time.sleep(0.25)
        self.summon_momo(self.gamename)
        # Now using full universal room handler instead
        for room in self.rooms:
            rh = RoomHandler(room)
            rh.start_room()
        # And then perform the endmap routine
        self.perform_endmap(repeat)


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
        # pet,on - this makes sure the pet is summoned (pre) or hidden (post)
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


class RoomHandler():
    def __init__(self, room: Room) -> None:
        # Add a timestamp to catch if have gotten stuck
        self.last_event_time = time.time()
        self.room = room
        with open("gamename.txt") as f:
            self.gamename = f.readline()

    def start_room(self):
        room = self.room
        # Check through the tags first
        tags = "".join(room.tags)
        acts = "".join(room.action_list)
        curbss = False if not "curbss" in tags else True
        nxtbss = False if not "nxtbss" in tags else True
        peton = False if not "pet,on" in tags else True
        petoff = False if not "pet,off" in tags else True
        repos = False if not "repos" in acts else True
        sect_cleared = False
        nxtbss_dir = False
        # Check which direction for nxtboss if reqd
        if nxtbss:
            nxtbss_dir = tags.split("curbss", 1)[1].split("|", 1)[
                0].replace(",", "")

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
                outcome = self.perform_exit(coords, nxtbss_dir, petoff)
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

    def perform_exit(self, coords, nxtbss_dir=False, petoff=False):
        outcome = BotUtils.move_bigmap_dynamic(int(coords[1]), int(coords[2]))
        nodetcnt = 0
        while not outcome:
            nodetcnt += 1
            if nodetcnt > 10:
                print("QUIT DUE TO CATASTROPHIC ERROR WITH NAVIGATION")
                os._exit(1)
            if nodetcnt % 3 == 0:
                key = "right"
                CustomInput.press_key(CustomInput.key_map[key], key)
                CustomInput.release_key(CustomInput.key_map[key], key)
            outcome = BotUtils.move_bigmap_dynamic(
                int(coords[1]), int(coords[2]))
        # Then turn pet off if required
        if petoff:
            self.cancel_momo_summon()
        if nxtbss_dir:
            # Need to press down the required key
            CustomInput.press_key(CustomInput.key_map[nxtbss_dir], nxtbss_dir)
        else:
            time.sleep(0.3)

    def perform_chest(self, coords, dir):
        pass

    def perform_repos(self, coords, dir):
        pass

    def perform_loot(self, coords, currbss=False):
        pass

    def perform_wypt(self, coords):
        pass

    def cancel_momo_summon(self):
        wincap = WindowCapture(self.gamename)
        x = wincap.window_rect[0]
        y = wincap.window_rect[1]
        pydirectinput.rightClick(x+82, y+197)
        time.sleep(0.1)
        pydirectinput.click(x+148, y+213)
        time.sleep(0.1)


def load_level_data(filename):
    with open(filename) as f:
        lines = f.readlines()
    list_rooms = []
    for line in lines:
        list_rooms.append(Room(line))
    return list_rooms


filename = os.path.dirname(
    os.path.abspath(__file__)) + "/levels/map10updated.txt"
rooms = load_level_data(filename)
room1 = rooms[0]
print(room1.action_list)
