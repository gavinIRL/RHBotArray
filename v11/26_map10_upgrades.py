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


def click_on_game(gamename):
    wincap = WindowCapture(gamename)
    centre_x = int(0.5 * wincap.w +
                   wincap.window_rect[0])
    centre_y = int(3 +
                   wincap.window_rect[1])
    ctypes.windll.user32.SetCursorPos(centre_x, centre_y)
    ctypes.windll.user32.mouse_event(
        0x0002, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(
        0x0004, 0, 0, 0, 0)


def detect_store(gamename=False):
    if not gamename:
        with open("gamename.txt") as f:
            gamename = f.readline()
    wincap = WindowCapture(gamename, [1084, 265, 1099, 267])
    image = wincap.get_screenshot()
    # cv2.imwrite("testytest.jpg", image)
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    g, h, i = [int(i) for i in image[0][4]]
    # print("GHI:{},{},{}".format(g, h, i))
    if a + b+c+d+e+f > 1500:
        # Value of 7 is disabled shop
        if g == 8:
            return True
    return False


def detect_yes_no_robust(gamename):
    wincap = WindowCapture(gamename, [516, 426, 541, 441])
    image = wincap.get_screenshot()
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=Yes'
    result = pytesseract.image_to_string(
        rgb, lang='eng', config=tess_config)[:-2]
    if result == "Yes":
        return True
    wincap = WindowCapture(gamename, [748, 426, 775, 441])
    image = wincap.get_screenshot()
    cv2.imwrite("testytest.jpg", image)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=No'
    result = pytesseract.image_to_string(
        rgb, lang='eng', config=tess_config)[:-2]
    if result == "No":
        return True
    return False


def detect_sect_clear_robust(gamename=False):
    if not gamename:
        with open("gamename.txt") as f:
            gamename = f.readline()
    # wincap = WindowCapture(gamename, custom_rect=[
    #     464+156, 640, 464+261, 741])
    wincap = WindowCapture(gamename, custom_rect=[
        464+29, 640, 464+261, 641])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][127]]
    g, h, i = [int(i) for i in image[0][-1]]
    j, k, l = [int(i) for i in image[0][163]]
    m, n, o = [int(i) for i in image[0][6]]
    p, q, r = [int(i) for i in image[0][122]]
    if a+b+c > 760:
        if d+e+f > 760:
            if j+k+l > 760:
                # This is a false positive
                return False
            if m+n+o > 760:
                # This is a false positive
                return False
            if p+q+r > 760:
                # This is a false positive
                return False
            if g+h+i > 760:
                # cv2.imwrite("testytest.jpg", image)
                return True
    return False


def detect_town_quick(gamename=False):
    wincap = WindowCapture(gamename, [1115, 41, 1145, 43])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][2]]
    d, e, f = [int(i) for i in image[0][10]]
    g, h, i = [int(i) for i in image[0][15]]
    j, k, l = [int(i) for i in image[0][20]]
    m, n, o = [int(i) for i in image[0][23]]
    p, q, r = [int(i) for i in image[0][28]]
    t, u, v = [int(i) for i in image[0][29]]
    cv2.imwrite("testytest.jpg", image)
    if a+b+c > 760 and d+e+f > 760:
        # print("Yes to #1")
        if j+k+l > 760 and m+n+o > 760:
            # print("Yes to #2")
            if p+q+r > 760 and g+h+i > 760:
                if not t+u+v > 760:
                    return True
    return False


time.sleep(1.5)
with open("gamename.txt") as f:
    gamename = f.readline()
start = time.time()
# check_petmenu_open(gamename)
# detect_gold_amount(gamename)
# print(Events.detect_move_reward_screen(gamename))
# grab_obscured_loot(gamename)
# detect_enemies_overworld(gamename)
# move_bigmap_dynamic(663, 635)
# prevent_dodge_check(0.05)
# in_town_check_thread(gamename, [True])
# click_on_game(gamename)
# print(detect_yes_no_robust(gamename))
# print(detect_sect_clear_robust(gamename))
print(detect_town_quick(gamename))
print("Time taken: {}s".format(time.time() - start))
