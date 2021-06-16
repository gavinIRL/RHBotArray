import time
import os
import cv2
import pydirectinput
from custom_input import CustomInput
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def start_endlevel_script(gamename):
    # Need to first wait until dungeon check returns false
    while Events.detect_in_dungeon():
        time.sleep(0.006)
    print("Got to pre-sectclear detect")
    # Then until sect cleared shows up
    while not BotUtils.detect_sect_clear():
        pydirectinput.press('esc')
        time.sleep(0.05)
    print("Got to pre-endlevel event check")
    # Then wait for end-level event to show up
    start_time = time.time()
    event = False
    while True:
        time.sleep(0.006)
        if time.time() > start_time + 3.5:
            break
        if not Events.detect_in_dungeon():
            # Press escape
            pydirectinput.press('esc')
            # Wait 2 seconds
            time.sleep(1)
            # Then if ok is detected turn flag on
            if Events.detect_endlevel_bonus_area():
                event = True
            break
    # Then do the appropriate handling if event is detected
    print("Got to pre-event handling")
    if event:
        do_otherworld_handling(gamename)
    # Once event is complete move to correct place in room
    move_to_loot_point(gamename)
    # And then commence looting
    print("Got to post-move to loot point")
    while Events.detect_in_dungeon():
        if not loot_everything(gamename):
            # Click centre of screen to skip
            skip_to_reward(gamename)
            break
    print("Got to pre-card check")
    # Then wait until card select appears
    while not Events.detect_reward_choice_open(gamename):
        time.sleep(0.2)
    print("Got to pre-choose reward")
    # Then wait until the cards become selectable
    time.sleep(4)
    # Then choose a random card
    Events.choose_random_reward(gamename)
    # Then wait until store is detected
    print("Got to pre-shop check")
    while not Events.detect_store(gamename):
        time.sleep(0.2)
    print("Got to pre-sellrepair")
    # And then perform the sell and repair actions
    sr = SellRepair()
    sr.ident_sell_repair()
    # And then go to next level if needs be
    print("Got to pre-restart")
    repeat_level()


def do_otherworld_handling(gamename):
    wincap = WindowCapture(gamename)
    # For now just press no to it
    pydirectinput.click(wincap.window_rect[0]+775, wincap.window_rect[1]+488)
    time.sleep(1)


def move_to_loot_point(gamename):
    # Placeholder for now
    CustomInput.press_key(CustomInput.key_map["right"], "right")
    # CustomInput.press_key(CustomInput.key_map["up"], "up")
    time.sleep(0.5)
    CustomInput.release_key(CustomInput.key_map["right"], "right")
    # CustomInput.release_key(CustomInput.key_map["up"], "up")


def loot_everything(gamename):
    player_name = BotUtils.detect_player_name(gamename)
    return Looting.grab_all_visible_loot(gamename, player_name)


def skip_to_reward(gamename):
    wincap = WindowCapture(gamename)
    pydirectinput.click(wincap.window_rect[0]+656, wincap.window_rect[1]+276)


def repeat_level():
    # Don't do anything for now
    # RHClick.click_explore_again()
    pass


if __name__ == "__main__":
    time.sleep(2)
    print("Starting")
    with open("gamename.txt") as f:
        gamename = f.readline()
    # while Events.detect_in_dungeon():
    #     time.sleep(0.2)
    # print("Didn't detect in dungeon")
    # print("Detected in dungeon: {}".format(Events.detect_in_dungeon()))
    start_endlevel_script(gamename)
