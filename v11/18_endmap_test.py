import time
import os
from v12.rhba_utils import WindowCapture
import pydirectinput
from rhba_utils import BotUtils, Events, SellRepair
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def start_endlevel_script():
    # Need to first wait until dungeon check returns false
    while not Events.detect_in_dungeon():
        time.sleep(0.006)
    # Then until sect cleared shows up
    while not BotUtils.detect_sect_clear():
        pydirectinput.press('esc')
        time.sleep(0.01)
    # Then wait for end-level event to show up
    start_time = time.time()
    event = False
    while True:
        time.sleep(0.006)
        if time.time() > start_time + 5:
            break
        if not Events.detect_in_dungeon():
            # Press escape
            pydirectinput.press('esc')
            # Wait 2 seconds
            time.sleep(2)
            # Then if ok is detected turn flag on
            if Events.detect_endlevel_bonus_area():
                event = True
            break
    # Then do the appropriate handling if event is detected
    if event:
        do_otherworld_handling()
    # Once event is complete move to correct place in room
    move_to_loot_point()
    # And then commence looting
    while Events.detect_in_dungeon():
        if not loot_everything():
            # Click centre of screen to skip
            skip_to_reward()
            break
    # Then wait until card select appears
    while not Events.detect_reward_choice_open():
        time.sleep(0.2)
    # Then wait until the cards become selectable
    time.sleep(2)
    # Then choose a random card
    Events.choose_random_reward()
    # Then wait until store is detected
    while not Events.detect_store():
        time.sleep(0.2)
    # And then perform the sell and repair actions
    sr = SellRepair()
    sr.ident_sell_repair()
    # And then go to next level if needs be
    repeat_level()


def do_otherworld_handling(gamename):
    wincap = WindowCapture(gamename)
    # For now just press no to it
    pydirectinput.click(wincap.window_rect[0]+775, wincap.window_rect[1]+488)
    time.sleep(1)


def move_to_loot_point():
    pass


def loot_everything():
    pass


def skip_to_reward():
    pass


def repeat_level():
    pass
