# This file will test looting of the current room
# It will require room details such as loot search points
# and automatically progress through each position
# and loot everything it can find
import pydirectinput
from rhba_utils import BotUtils, WindowCapture, HsvFilter
from custom_input import CustomInput
import time
import os
import cv2
import math
import pytesseract
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def grab_all_visible_loot(gamename, player_name):
    start_time = time.time()
    while True:
        if time.time() - start_time > 20:
            break
        outcome = BotUtils.try_find_and_grab_loot(
            gamename, player_name, printout=True)
        if outcome == "noloot":
            break
        elif outcome == "noplayer":
            pydirectinput.press("right")
            outcome = BotUtils.try_find_and_grab_loot(
                gamename, player_name, printout=True)
            if outcome == "noplayer":
                break
        elif outcome == "falsepos":
            break
        elif outcome == True:
            count = 0
            while BotUtils.detect_xprompt(gamename):
                if count > 12:
                    break
                pydirectinput.press("x")
                count += 1
                time.sleep(0.09)


def loot_current_room(gamename, player_name, search_points=False):
    # Start by picking up loot already in range
    BotUtils.close_map_and_menu(gamename)
    count = 0
    while BotUtils.detect_xprompt(gamename):
        if count > 12:
            break
        pydirectinput.press("x")
        count += 1
        time.sleep(0.09)
    # Then try grabbing all visible far loot
    grab_all_visible_loot(gamename, player_name)
    # Then once that is exhausted cycle through the searchpoints
    if search_points:
        for point in search_points:
            x, y, first_dir = point
            BotUtils.move_to(gamename, x, y, yfirst=first_dir == "y")
            BotUtils.close_map_and_menu(gamename)
            grab_all_visible_loot(gamename, player_name)
    # Then are completely finished
    print("Done looting!")


# format will be x,y,movefirst
search_points = [(722, 626, "y")]
with open("gamename.txt") as f:
    gamename = f.readline()
with open(os.path.dirname(os.path.abspath(__file__)) + "/testimages/mainplayer.txt") as f:
    player_name = f.readline()
time.sleep(2)
loot_current_room(gamename, player_name, search_points)
