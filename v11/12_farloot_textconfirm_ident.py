import pydirectinput
from rhba_utils import BotUtils, WindowCapture, HsvFilter
from custom_input import CustomInput
import time
import os
import cv2
import math
import pytesseract
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def confirm_loot_test(gamename):
    # First need to close anything that might be in the way
    BotUtils.close_map_and_menu(gamename)
    # Then grab loot locations
    loot_list = BotUtils.grab_farloot_locationsv2(gamename)
    confirmed_list = []
    for index, coords in enumerate(loot_list):
        start_time = time.time()
        x, y = coords
        wincap = WindowCapture(gamename, [x-75, y-12, x+75, y+10])
        rgb = wincap.get_screenshot()
        filter = HsvFilter(0, 0, 131, 151, 255, 255, 0, 0, 0, 0)
        rgb = BotUtils.apply_hsv_filter(rgb, filter)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        # print("Index:{}, result={}".format(index, result))
        if len(result) > 3:
            # confirmed_list.append(loot_list[index])
            confirmed_list.append(result)
            cv2.imwrite("testytest.jpg", rgb)
        print("Time taken for confirmation: {}s".format(time.time()-start_time))
    print(confirmed_list)


time.sleep(2)
with open("gamename.txt") as f:
    gamename = f.readline()
confirm_loot_test(gamename)
