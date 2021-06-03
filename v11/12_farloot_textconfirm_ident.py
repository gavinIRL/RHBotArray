import pydirectinput
from rhba_utils import BotUtils, WindowCapture, HsvFilter
from custom_input import CustomInput
import time
import os
import cv2
import math
import pytesseract
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def confirm_loot_test(gamename, player_name):
    # First need to close anything that might be in the way
    BotUtils.close_map_and_menu(gamename)
    # Then grab loot locations
    loot_list = BotUtils.grab_farloot_locationsv2(gamename)
    if not loot_list:
        return "noloot"
    confirmed = False
    for index, coords in enumerate(loot_list):
        x, y = coords
        wincap = WindowCapture(gamename, [x-75, y-12, x+75, y+10])
        rgb = wincap.get_screenshot()
        filter = HsvFilter(0, 0, 131, 151, 255, 255, 0, 0, 0, 0)
        rgb = BotUtils.apply_hsv_filter(rgb, filter)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        if len(result) > 3:
            confirmed = loot_list[index]
            print("Detected "+result)
            break
    if not confirmed:
        return False
    playerx, playery = BotUtils.grab_character_location(
        player_name, gamename)
    # If didn't find player then try once more
    if not playerx:
        playerx, playery = BotUtils.grab_character_location(
            player_name, gamename)
        if not playerx:
            return "noplayer"
    relx = playerx - confirmed[0]
    rely = confirmed[1] - playery - 275
    rect = [confirmed[0]-100, confirmed[1] -
            30, confirmed[0]+100, confirmed[1]+30]
    BotUtils.move_towards(relx, "x")
    loop_time = time.time()
    time_remaining = 0.1
    time.sleep(0.01)
    while time_remaining > 0:
        time.sleep(0.003)
        if BotUtils.detect_xprompt(gamename):
            break
        try:
            newx, newy = BotUtils.grab_farloot_locationsv2(gamename, rect)[0]
            time_taken = time.time() - loop_time
            movementx = confirmed[0] - newx
            speed = movementx/time_taken
            time_remaining = abs(
                relx/speed) - time_taken
            rect = [newx-100, newy-30, newx+100, newy+30]
        except:
            print("Exited x due to no detect")
            try:
                time.sleep(time_remaining)
                break
            except:
                return False
    for key in ["left", "right"]:
        CustomInput.release_key(CustomInput.key_map[key], key)
    BotUtils.move_towards(rely, "y")
    start_time = time.time()
    while not BotUtils.detect_xprompt(gamename):
        time.sleep(0.005)
        # After moving in opposite direction
        if time.time() - start_time > 10:
            # If have moved opposite with no result for equal amount
            if time.time() - start_time > 12:
                for key in ["up", "down"]:
                    CustomInput.release_key(CustomInput.key_map[key], key)
                # Return ignore so that it will ignore this detection
                return "ignore"
        # If no result for 3 seconds
        elif time.time() - start_time > 2:
            # Try moving in the opposite direction
            for key in ["up", "down"]:
                CustomInput.release_key(CustomInput.key_map[key], key)
            BotUtils.move_towards(-1*rely, "y")
            start_time -= 8
    for key in ["up", "down"]:
        CustomInput.release_key(CustomInput.key_map[key], key)
    return True


time.sleep(2)
with open("gamename.txt") as f:
    gamename = f.readline()
with open(os.path.dirname(os.path.abspath(__file__)) + "/testimages/mainplayer.txt") as f:
    player_name = f.readline()
while True:
    if confirm_loot_test(gamename, player_name) != True:
        break
    pydirectinput.press("x")
