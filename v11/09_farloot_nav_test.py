from rhba_utils import BotUtils, HsvFilter
import time
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def start(gamename, player_name, speed):
    time.sleep(2)
    loot_list = BotUtils.grab_farloot_locationsv2(gamename)
    item1 = loot_list[0]
    rect = [item1[0]-100, item1[1]-100, item1[0]+100, item1[1]+100]
    start_time = time.time()
    for i in range(100):
        BotUtils.grab_farloot_locationsv2(gamename, rect)
    print("Time taken for each is {}s".format((time.time()-start_time)/100))
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


with open("gamename.txt") as f:
    gamename = f.readline()
with open(os.path.dirname(os.path.abspath(__file__)) + "/testimages/mainplayer.txt") as f:
    player_name = f.readline()
start(gamename, player_name, 22.5)
