import pydirectinput
from rhba_utils import BotUtils
from custom_input import CustomInput
import time
import os
import math
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def loot_nearest_item(gamename, player_name, ignore_closest=False):
    # First need to close anything that might be in the way
    BotUtils.close_map_and_menu(gamename)
    # Then grab loot locations
    loot_list = BotUtils.grab_farloot_locationsv2(gamename)
    # If none then return False
    if not loot_list:
        return "noloot"
    # Then grab the player location
    playerx, playery = BotUtils.grab_character_location(
        player_name, gamename)
    # If didn't find player then try once more
    if not playerx:
        playerx, playery = BotUtils.grab_character_location(
            player_name, gamename)
        if not playerx:
            return "noplayer"
    # Then convert lootlist to rel_pos list
    relatives = BotUtils.convert_list_to_rel(loot_list, playerx, playery, 275)
    # And find the closest
    closest_index = BotUtils.grab_closest(relatives)
    # If need to ignore closest as known false positive:
    if ignore_closest:
        loot_list.pop(closest_index)
        relatives.pop(closest_index)
    closest = loot_list[closest_index]
    # Create the rectangle for zoomed rapid tracking
    rect = [closest[0]-100, closest[1]-30, closest[0]+100, closest[1]+30]

    # Now need to start moving towards the loot in x direction
    BotUtils.move_towards(relatives[closest_index][0], "x")
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
            movementx = closest[0] - newx
            speed = movementx/time_taken
            time_remaining = abs(
                relatives[closest_index][0]/speed) - time_taken
            rect = [newx-100, newy-30, newx+100, newy+30]
        except:
            try:
                time.sleep(time_remaining)
                break
            except:
                return False
    for key in ["left", "right"]:
        CustomInput.release_key(CustomInput.key_map[key], key)
    BotUtils.move_towards(relatives[closest_index][1], "y")
    start_time = time.time()
    while not BotUtils.detect_xprompt(gamename):
        time.sleep(0.005)
        # After moving in opposite direction
        if time.time() - start_time > 10:
            # If have moved opposite with no result for equal amount
            if time.time() - start_time > 14:
                for key in ["up", "down"]:
                    CustomInput.release_key(CustomInput.key_map[key], key)
                # Return ignore so that it will ignore this detection
                return "ignore"
        # If no result for 3 seconds
        elif time.time() - start_time > 2:
            # Try moving in the opposite direction
            for key in ["up", "down"]:
                CustomInput.release_key(CustomInput.key_map[key], key)
            BotUtils.move_towards(-1*relatives[closest_index][1], "y")
            start_time -= 8
    for key in ["up", "down"]:
        CustomInput.release_key(CustomInput.key_map[key], key)
    return True


with open("gamename.txt") as f:
    gamename = f.readline()
with open(os.path.dirname(os.path.abspath(__file__)) + "/testimages/mainplayer.txt") as f:
    player_name = f.readline()
time.sleep(3)
while True:
    if loot_nearest_item(gamename, player_name) != True:
        break
    pydirectinput.press("x")
