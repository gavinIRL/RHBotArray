import pydirectinput
from rhba_utils import BotUtils, WindowCapture
from custom_input import CustomInput
import time
import os
import math
import pytesseract
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def confirm_loot_test(gamename):
    # First need to close anything that might be in the way
    BotUtils.close_map_and_menu(gamename)
    # Then grab loot locations
    loot_list = BotUtils.grab_farloot_locationsv2(gamename)
    for index, coords in enumerate(loot_list):
        x, y = coords
        wincap = WindowCapture(gamename, [x-70, y+15, x+70, y+15])
        rgb = wincap.get_screenshot()
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        print("Index:{}, result={}".format(index, result))


with open("gamename.txt") as f:
    gamename = f.readline()
confirm_loot_test(gamename)
