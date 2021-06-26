import time
import os
import numpy as np
import cv2
import math
import ctypes
import logging
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter
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


time.sleep(1.5)
with open("gamename.txt") as f:
    gamename = f.readline()
# check_petmenu_open(gamename)
# detect_gold_amount(gamename)
# print(Events.detect_move_reward_screen(gamename))
grab_obscured_loot(gamename)
