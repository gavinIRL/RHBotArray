import time
import os
import numpy as np
import cv2
import math
import ctypes
import logging
from fuzzywuzzy import fuzz
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter, Follower
import pydirectinput
import pytesseract
from custom_input import CustomInput
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# xdist = 61
# ydist = 4
# smaller = min(xdist, ydist)
# diag = math.hypot(smaller, smaller)
# print(diag + max(xdist, ydist) - smaller)


def check_petmenu_open(gamename):
    wincap = WindowCapture(gamename, [604, 120, 657, 122])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][8]]
    g, h, i = [int(i) for i in image[0][-1]]
    # print("ABC:{},{},{}".format(a, b, c))
    # print("DEF:{},{},{}".format(d, e, f))
    # print("GHI:{},{},{}".format(g, h, i))
    # cv2.imwrite("testytest.jpg", image)
    if a + g == 76:
        if d+e+f > 750:
            return True
    return False


def detect_gold_amount(gamename):
    wincap = WindowCapture(gamename, [681, 473, 748, 490])
    image = wincap.get_screenshot()
    # cv2.imwrite("testytest.jpg", image)
    tess_config = '--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789,'
    result = pytesseract.image_to_string(
        image, lang='eng', config=tess_config)[:-2].replace(",", "")
    return result


def grab_obscured_loot(gamename):
    CustomInput.press_key(CustomInput.key_map["up"], "up")
    start = time.time()
    check_again = False
    while not BotUtils.detect_xprompt(gamename):
        time.sleep(0.003)
        if time.time() - start > 0.5:
            check_again = True
            break
    CustomInput.release_key(CustomInput.key_map["up"], "up")
    count = 0
    while BotUtils.detect_xprompt(gamename):
        if count > 12:
            break
        pydirectinput.press("x")
        count += 1
        time.sleep(0.23)
    if check_again:
        Looting.grab_all_visible_lootv2(gamename)


def detect_enemies_overworld(gamename):
    # if not BotUtils.detect_bigmap_open(gamename):
    #     BotUtils.try_toggle_map()
    # wincap = WindowCapture(gamename, [530, 331, 781, 580])
    othr_plyr_vision = Vision("otherplayerinvert.jpg")
    orig_image = cv2.imread("testycont.jpg")
    orig_image = orig_image[331:580, 530:781]
    filter = HsvFilter(0, 198, 141, 8, 255, 255, 0, 0, 0, 0)
    image = cv2.blur(orig_image, (4, 4))
    image = BotUtils.filter_blackwhite_invert(filter, image)
    cv2.imwrite("testytest.jpg", image)
    rectangles = othr_plyr_vision.find(
        image, threshold=0.41, epsilon=0.5)
    points = othr_plyr_vision.get_click_points(rectangles)
    if len(points) >= 1:
        output_image = othr_plyr_vision.draw_crosshairs(orig_image, points)
        cv2.imwrite("testypoints.jpg", output_image)
        return True
    return False


def move_bigmap_dynamic(x, y, gamename=False, rect=False):
    while not BotUtils.detect_bigmap_open(gamename):
        BotUtils.try_toggle_map_clicking()
    if not gamename:
        with open("gamename.txt") as f:
            gamename = f.readline()
    # Then need to find where the player is
    if not rect:
        rect = [561, 282, 1111, 666]
    playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
    if not playerx:
        print("Didn't find player first time")
        return False
    relx = x - playerx
    rely = playery - y
    margin = 2
    follower = Follower(margin)
    noplyr_count = 0
    while abs(relx) > margin or abs(rely) > margin:
        rect = [playerx - 40, playery - 40, playerx + 40, playery + 40]
        playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
        if playerx:
            if noplyr_count > 0:
                noplyr_count -= 1
            relx = x - playerx
            rely = playery - y
            follower.navigate_towards(relx, rely)
        else:
            noplyr_count += 1
            if noplyr_count > 10:
                break
        time.sleep(0.03)
    BotUtils.close_map_and_menu(gamename)
    if noplyr_count > 10:
        return False
    else:
        return True


def dodge_time_check(time_sleep=0.17):
    key = "right"
    CustomInput.press_key(CustomInput.key_map[key], key)
    time.sleep(0.01)
    CustomInput.release_key(CustomInput.key_map[key], key)
    time.sleep(time_sleep)
    CustomInput.press_key(CustomInput.key_map[key], key)
    time.sleep(0.01)
    CustomInput.release_key(CustomInput.key_map[key], key)


def double_dir_dodge_check(time_sleep=0.17):
    key = "right"
    key2 = "up"
    CustomInput.press_key(CustomInput.key_map[key], key)
    # time.sleep(0.005)
    CustomInput.press_key(CustomInput.key_map[key2], key2)
    time.sleep(0.005)
    CustomInput.release_key(CustomInput.key_map[key], key)
    # time.sleep(0.005)
    CustomInput.release_key(CustomInput.key_map[key2], key2)
    time.sleep(time_sleep)
    CustomInput.press_key(CustomInput.key_map[key], key)
    # time.sleep(0.005)
    CustomInput.press_key(CustomInput.key_map[key2], key2)
    time.sleep(0.005)
    CustomInput.release_key(CustomInput.key_map[key], key)
    # time.sleep(0.005)
    CustomInput.release_key(CustomInput.key_map[key2], key2)


def prevent_dodge_check(time_sleep=0.17):
    key = "right"
    CustomInput.press_key(CustomInput.key_map[key], key)
    time.sleep(0.01)
    CustomInput.release_key(CustomInput.key_map[key], key)
    key = "left"
    CustomInput.press_key(CustomInput.key_map[key], key)
    time.sleep(0.001)
    CustomInput.release_key(CustomInput.key_map[key], key)
    key = "right"
    time.sleep(time_sleep)
    CustomInput.press_key(CustomInput.key_map[key], key)
    time.sleep(0.01)
    CustomInput.release_key(CustomInput.key_map[key], key)


def check_in_town(gamename):
    name = BotUtils.detect_level_name(gamename, chars="BramunezMkt")
    if fuzz.ratio(name, "BramunezMarket") > 85:
        return True
    return False


def in_town_check_thread(gamename, flag):
    while flag[0]:
        time.sleep(5)
        if check_in_town(gamename):
            print("Exited as detected in town")
            os._exit(1)


time.sleep(1.5)
with open("gamename.txt") as f:
    gamename = f.readline()
# check_petmenu_open(gamename)
# detect_gold_amount(gamename)
# print(Events.detect_move_reward_screen(gamename))
# grab_obscured_loot(gamename)
# detect_enemies_overworld(gamename)
# move_bigmap_dynamic(663, 635)
# prevent_dodge_check(0.05)
in_town_check_thread(gamename, [True])
