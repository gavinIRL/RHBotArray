from rhba_utils import BotUtils, HsvFilter
from custom_input import CustomInput
import time
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def start(gamename, player_name):
    time.sleep(2)
    loot_list = BotUtils.grab_farloot_locationsv2(gamename)
    item1 = loot_list[0]
    rect = [item1[0]-100, item1[1]-100, item1[0]+100, item1[1]+100]
    playerx, playery = BotUtils.grab_character_location(
        player_name, gamename)
    relx = playerx - item1[0]
    rely = item1[1] - playery - 275
    # Now need to start moving towards the loot in x direction
    move_towards(relx, "x")
    loop_time = time.time()
    time_remaining = 0.1
    time.sleep(0.01)
    while time_remaining > 0:
        time.sleep(0.005)
        # Grab an updated image
        try:
            newx, newy = BotUtils.grab_farloot_locationsv2(gamename, rect)[0]
            time_taken = time.time() - loop_time
            movementx = item1[0] - newx
            speed = movementx/time_taken
            time_remaining = abs(relx/speed) - time_taken
            # print(time_remaining)
            rect = [newx-100, newy-100, newx+100, newy+100]
        except:
            time.sleep(time_remaining)
            break
    for key in ["left", "right"]:
        CustomInput.release_key(CustomInput.key_map[key], key)

    # And now try to solve the y-dir
    move_towards(rely, "y")
    while not BotUtils.detect_xprompt(gamename):
        time.sleep(0.005)
    for key in ["up", "down"]:
        CustomInput.release_key(CustomInput.key_map[key], key)

    # start_time = time.time()
    # for i in range(100):
    #     BotUtils.grab_farloot_locationsv2(gamename, rect)
    # print("Time taken for each is {}s".format((time.time()-start_time)/100))
    # if loot_list:
    #     playerx, playery = BotUtils.grab_character_location(
    #         player_name, gamename)
    #     for item in loot_list:
    #         relx = playerx - item[0]
    #         rely = item[1] - playery - 275
    #         print("relx:{}, rely:{}".format(relx, rely))
    #         # BotUtils.resolve_single_direction(speed*25, relx, "x")
    #         # BotUtils.resolve_single_direction(speed*12, rely, "y")
    #         # break


def move_towards(value, dir):
    if dir == "x":
        if value > 0:
            key = "left"
        else:
            key = "right"
    elif dir == "y":
        if value > 0:
            key = "down"
        else:
            key = "up"
    CustomInput.press_key(CustomInput.key_map[key], key)


with open("gamename.txt") as f:
    gamename = f.readline()
with open(os.path.dirname(os.path.abspath(__file__)) + "/testimages/mainplayer.txt") as f:
    player_name = f.readline()
start(gamename, player_name)
