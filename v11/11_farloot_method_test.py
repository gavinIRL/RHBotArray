from rhba_utils import BotUtils
from custom_input import CustomInput
import time
import os
import math
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def loot_nearest_item(gamename, player_name):
    # First need to close anything that might be in the way
    BotUtils.close_map_and_menu()
    # Then grab loot locations
    loot_list = BotUtils.grab_farloot_locationsv2(gamename)
    # If none then return False
    if not loot_list:
        return False
    # Then grab the player location
    playerx, playery = BotUtils.grab_character_location(
        player_name, gamename)
    # If didn't find player then try once more
    if not playerx:
        playerx, playery = BotUtils.grab_character_location(
            player_name, gamename)
        if not playerx:
            return False
    # Then convert lootlist to rel_pos list and find closest
