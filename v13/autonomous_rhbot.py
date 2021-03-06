# This file autonomously performs a level (multiple times if required)
# The level data is drawn from a self-created database
# of actions and locations, see the levels folder
from threading import Thread
import time
import os
import cv2
import math
import ctypes
import logging
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter, Follower
import pydirectinput
from custom_input import CustomInput
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logging.getLogger().setLevel(logging.ERROR)


class Weapon:
    # This class defines what keys to press for a given weapon

    def __init__(self, weapon: str = "MS") -> None:
        if weapon == "MS":
            self.primary_clear = "h"
            self.primary_clear_cd = 8.8
            self.continue_clear = ["h", "a", "g", "f", "s", "d"]
            self.continue_boss = ["s", "d", "f", "a", "g"]
            self.chest_open = "d"


class MapHandler():
    # This class handles the entire map (consisting of multiple rooms)

    def __init__(self, roomdata: list, weapon: Weapon) -> None:
        self.rooms = roomdata
        self.weapon = weapon
        self.speed = 22.5
        self.map_rect = [561, 282, 1111, 666]
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.game_wincap = WindowCapture(self.gamename)
        # This is for determining wait time before next clear
        self.last_clear = 0
        self.clearskill_cd = 8.9
        # This is for keeping track of where player is
        self.current_room = 0
        # For aiming at enemies
        self.enemy_minimap_filter = HsvFilter(
            0, 128, 82, 8, 255, 255, 0, 66, 30, 34)
        enemy_custom_rect = [1094, 50, 1284, 210]
        self.enemy_minimap_wincap = WindowCapture(
            self.gamename, enemy_custom_rect)
        self.enemy_minimap_vision = Vision('enemy67.jpg')
        # Var for tracking gold progress
        self.gold = 860000

    def start(self, repeat: bool = False) -> None:
        """This function performs all functions necessary to complete a map, 
        and start the level repeat logic if required.

                Parameters:
                        repeat (bool, optional): Whether to do end-of-level start new level logic. Defaults to disabled.
        """
        time.sleep(1.5)
        while not Events.detect_in_dungeon():
            time.sleep(0.25)
        # Now using full universal room handler instead
        for i, room in enumerate(self.rooms):
            rh = RoomHandler(self, room, self.weapon)
            # print(f"Starting room {i}")
            rh.start_room()
            # print(f"Finished room {i}")
        # And then perform the endmap routine
        if repeat:
            self.repeat_level(self.gamename)

    def repeat_level(self, gamename: str) -> None:
        """This function performs the actions required to start a new level.

                Parameters:
                        gamename (str): Game window name
        """
        # Close the shop
        pydirectinput.press('esc')
        time.sleep(0.1)
        pydirectinput.press('esc')
        time.sleep(0.1)
        BotUtils.close_map_and_menu(gamename)
        time.sleep(0.1)
        RHClick.click_explore_again(gamename)
        time.sleep(1.5)


class Room():
    # This class holds data for a room
    # Room data is taken from the manual database
    # The room data is given to the roomhandler for execution

    def __init__(self, line: str) -> None:
        # Format of each line in the file should be as follows
        # rect # coords_n | coords_n+1 # action_n | action_n+1 # tags
        # ------------------------------------
        # format rect is leftx, topy, rightx, bottomy
        # format coords is x,y
        # ------------------------------------
        # list actions is as follows:
        # peton / petoff - handle pet
        # clear,dir - position to perform clear from, point left
        # boss,dir - position to perform boss attacks from
        # exit - position to exit room from
        # chest,dir - position to attack chest, point left
        # repos,dir,5 - position to reposition to, point left, after seconds
        # loot - position to attempt to loot from
        # wypt - this is a travel waypoint only
        # nxtbss,dir - next room is the boss room, hold l to enter
        # sllrpr - perform post-boss sell and repair
        # bsslt - bossloot coords i.e. initial boss looting point
        # singclr - do a single main clear skill
        # ------------------------------------
        # please note: bsslt includes endmap handling, only one is required
        # use loot/wypt/chest to continue looting post-boss
        # ------------------------------------
        # list of tags is as follows
        # curbss - this room is the boss room
        # multi - this room will have multiple sectclear notifications
        # midcut - this room will have a mid-clear cutscene
        rect, coords, actions, tags = line.split("#")
        self.action_list = []
        self.coord_list = []
        self.tags = []
        self.rect = []
        for point in rect.split(","):
            self.rect.append(int(point))
        for coord in coords.split("|"):
            x, y = coord.split(",")
            self.coord_list.append((int(x), int(y)))
        for action in actions.split("|"):
            self.action_list.append(action)
        for tag in tags.split("|"):
            self.tags.append(tag)


class RoomHandler():
    # This class executes all required actions in a given room

    def __init__(self, mh: MapHandler, room: Room, weapon: Weapon) -> None:
        # Add a timestamp to catch if have gotten stuck
        self.last_event_time = time.time()
        self.weapon = weapon
        self.room = room
        self.maphandler = mh
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        # For aiming at enemies
        self.enemy_minimap_filter = HsvFilter(
            0, 128, 82, 8, 255, 255, 0, 66, 30, 34)
        enemy_custom_rect = [1094, 50, 1284, 210]
        self.enemy_minimap_wincap = WindowCapture(
            self.gamename, enemy_custom_rect)
        self.enemy_minimap_vision = Vision('enemy67.jpg')

    def start_room(self):
        """This function performs the actions required to complete a room. 
        It can handle any action per the database and terminates once the 
        room is cleared or the move to next room logic has completed.
        All input is handled using the current room object data.
        """
        room = self.room
        # Check through the tags first
        tags = "".join(room.tags).strip()
        acts = "".join(room.action_list)
        curbss = False if not "curbss" in tags else True
        multi = False if not "multi" in tags else True
        repos = False if not "repos" in acts else True
        sect_cleared = False
        # Then go through the actions and carry them out
        for i, action in enumerate(room.action_list):
            self.last_event_time = time.time()
            # Need to check if reposition is the next item
            repos_time = False
            try:
                if repos:
                    next = room.action_list[i+1]
                    if "repos" in next:
                        _, _, repos_time = next.split(",")
            except:
                pass
            coords = room.coord_list[i]
            if "clear" in action:
                _, dir = action.split(",")
                outcome = self.perform_clear(coords, dir, repos_time)
                if outcome:
                    sect_cleared = True
            elif "boss" in action:
                _, dir = action.split(",")
                outcome = self.perform_boss(coords, dir, repos_time, curbss)
                if outcome:
                    sect_cleared = True
            elif "exit" in action:
                outcome = self.perform_exit(coords)
                if not outcome:
                    print("Problem with nav during exit, need to add handling")
                    os._exit(1)
            elif "chest" in action:
                _, dir = action.split(",")
                outcome = self.perform_chest(coords, dir)
            elif "repos" in action:
                _, dir, sec = action.split(",")
                if not sect_cleared:
                    self.perform_repos(coords, dir)
            elif "loot" in action:
                self.perform_loot(coords)
            elif "wypt" in action:
                outcome = self.perform_wypt(coords)
                if not outcome:
                    print("Problem with nav during exit, need to add handling")
                    os._exit(1)
            elif "singclr" in action:
                self.perform_singclr(coords)
            elif "nxtbss" in action:
                # print("Got to pre-nxtbss")
                _, dir = action.split(",")
                self.perform_move_into_bossroom(dir)
            elif "bsslt" in action:
                self.perform_endlevel(coords)
            elif "sllrpr" in action:
                self.perform_sell_and_repair()
            elif "peton" in action:
                self.summon_momo()
            elif "petoff" in action:
                self.cancel_momo_summon()
                # print("Got past pet off")

    def perform_clear(self, coords: tuple, dir: str, repos: bool = False):
        """This function performs the actions required to clear a room.
        It continues until the room clear message is received.

                Parameters:
                        coords (tuple): Big map coordinates to move to to start clearing from.
                        dir (str): Direction character should face to begin clearing.
                        repos (float, optional): The time after which the character should relocate and continue clearing. Defaults to disabled.

                Returns:
                        bool: whether the room clear message was detected during function logic.
        """
        travel_time = self.calculate_travel_time(coords[0], coords[1])
        self.perform_navigation(coords, True)
        self.face_direction(dir)
        if travel_time < 1.8:
            time.sleep(0.8)
        if travel_time < 0.6:
            time.sleep(0.2)
        self.perform_primary_clear()
        aim_cd = time.time()
        if not repos:
            while not BotUtils.detect_sect_clear(self.gamename):
                if time.time() - aim_cd > 2:
                    # print("Aiming at enemies again")
                    self.aim_at_enemies()
                    aim_cd = time.time() + 1
                    self.perform_continue_clear()
                else:
                    self.perform_continue_clear()
            if not Events.detect_in_dungeon():
                self.perform_midlevel_event()
                time.sleep(0.8)
            return True
        # Alternative handling if reposition is required mid-clear
        else:
            start_time = time.time()
            need_to_repos = False
            while not BotUtils.detect_sect_clear(self.gamename):
                if time.time() - aim_cd > 2:
                    # print("Aiming at enemies again")
                    self.aim_at_enemies()
                    aim_cd = time.time() + 1
                    self.perform_continue_clear()
                elif time.time() - start_time > repos:
                    need_to_repos = True
                    break
                else:
                    self.perform_continue_clear()
            if not Events.detect_in_dungeon():
                self.perform_midlevel_event()
                time.sleep(0.8)
            if not need_to_repos:
                return True
            return False

    def perform_singclr(self, coords: tuple):
        """This function performs a single press of clear skill at requested location.
        It does not continue until the room clear message is received.

                Parameters:
                        coords (tuple): Big map coordinates to move to to press clear button from.
        """
        self.perform_navigation(coords, True)
        self.perform_primary_clear()

    def perform_boss(self, coords: tuple, dir: str, repos: bool = False, curbss: bool = True):
        """This function performs the typical actions for a boss kill.
        It continues either until the boss is killed, or a reposition is required, or else until section cleared.

                Parameters:
                        coords (tuple): Big map coordinates to move to to start boss-killer attacks from.
                        dir (str): Direction character should face to begin boss attacks.
                        repos (float, optional): The time after which the character should relocate and continue attacking. Defaults to disabled.
                        curbss (bool, optional): Whether the current room is the boss room or just a standard room. Defaults to boss room.

                Returns:
                        bool: whether the room clear message or boss kill message was detected during function logic.
        """
        # First need to wait until cutscreen or boss appear and react
        if curbss:
            while True:
                time.sleep(0.006)
                if not Events.detect_in_dungeon():
                    # need to stop the movement
                    # BotUtils.stop_movement()
                    while not Events.detect_in_dungeon():
                        # print("Curbss check loop esc press")
                        pydirectinput.press('esc')
                        time.sleep(0.05)
                        BotUtils.close_map_and_menu(self.gamename)
                        time.sleep(0.25)
                    break
                if BotUtils.detect_boss_healthbar(self.gamename):
                    break
        # Then need to navigate to the boss
        self.perform_navigation(coords, True)
        self.face_direction(dir)
        no_dunchk_count = 0
        aim_cd = time.time()
        if not repos:
            while not BotUtils.detect_sect_clear(self.gamename):
                if not Events.detect_in_dungeon():
                    no_dunchk_count += 1
                    if no_dunchk_count > 3:
                        return True
                else:
                    no_dunchk_count = 0
                if Events.detect_move_reward_screen(self.gamename):
                    return True
                if Events.detect_endlevel_bonus_area(self.gamename):
                    return True
                if time.time() - aim_cd > 2:
                    # print("Aiming at enemies again")
                    self.aim_at_enemies()
                    aim_cd = time.time() + 1
                    self.perform_continue_clear()
                else:
                    self.perform_continue_clear()
            return True
        # Alternative handling if reposition is required mid-clear
        else:
            # TBD
            return False

    def perform_exit(self, coords: tuple):
        """This function performs the actions required to navigate to start of next room.
        It will wait to until the previous section clear message has full disappeared before continuing.

                Parameters:
                        coords (tuple): Big map coordinates to move to to wait to enter next room.

                Returns:
                        bool: whether the command was completed successfully.
        """
        self.perform_navigation(coords)
        time_end = time.time() + 0.5
        while time_end > time.time():
            time.sleep(0.005)
            if BotUtils.detect_sect_clear(self.gamename):
                time_end = time.time() + 0.5
        return True

    def perform_chest(self, coords: tuple, dir: str):
        """This function navigates the character to the location of the chest firstly.
        It will then face the correct location to open the chest, and then press the appropriate skill.

                Parameters:
                        coords (tuple): Big map coordinates of where to stand to open chest.
                        dir (str): Direction that character should face to open the chest.
        """
        self.perform_navigation(coords)
        self.face_direction(dir)
        self.hit_chest()

    def perform_repos(self, coords: tuple, dir: str):
        """This functions performs the actions required to navigate to predetermined repositioning point.
        It will then face in a certain direction once the destination is reached.

                Parameters:
                        coords (tuple): Big map coordinates for where to reposition to.
                        dir (str): Direction that character should face to open the chest.
        """
        self.perform_navigation(coords, True)
        self.face_direction(dir)

    def perform_endlevel(self, coords: tuple):
        """This function performs the entire set of actions required once the boss is dead to be ready for next level.
        It will handle any end-level events, manual looting of boss loot, and also automatically sell all junk loot.

        Note: more loot points and chest opening points can be specified after this action.

                Parameters:
                        coords (tuple): Big map coordinates for the primary bossloot point.

                Returns:
                        bool: whether the command was completed successfully.
        """
        # First step is to go past death cutscene if required
        reward_skip_det = False
        endlevel_event_det = False
        while Events.detect_in_dungeon():
            time.sleep(0.006)
            if Events.detect_move_reward_screen(self.gamename):
                reward_skip_det = True
                break
        # Then it is to skip through endlevel event cutscene
        if not reward_skip_det:
            while not Events.detect_in_dungeon():
                pydirectinput.press('esc')
                time.sleep(0.05)
                BotUtils.close_map_and_menu(self.gamename)
                if Events.detect_move_reward_screen(self.gamename):
                    reward_skip_det = True
                    break
                time.sleep(0.15)
        # Then to finally confirm either one of the two events
        if not reward_skip_det:
            while True:
                # Need to check for endlevel event
                if Events.detect_endlevel_bonus_area(self.gamename):
                    endlevel_event_det = True
                    break
                if Events.detect_move_reward_screen(self.gamename):
                    reward_skip_det = True
                    break
                pydirectinput.press('esc')
                time.sleep(0.05)
                BotUtils.close_map_and_menu(self.gamename)
        # And then do the endlevel event handling is required
        if endlevel_event_det:
            self.perform_endlevel_event_handling()
        # Then move to primary loot point
        AntiStickUtils.move_bigmap_dynamic(
            coords[0], coords[1], rect=self.room.rect, checkmap=False)
        Looting.grab_nearby_loot(self.gamename)
        # print("Got to post-move to loot point")
        while Events.detect_in_dungeon():
            if not self.loot_everything(self.gamename):
                self.move_slightly_left()
                # Try once more to loot
                Looting.grab_nearby_loot(self.gamename)
                self.loot_everything(self.gamename)
                # Click centre of screen to skip
                self.skip_to_reward(self.gamename)
                break
        # print("Got to pre-card check")
        # Then wait until card select appears
        while not Events.detect_reward_choice_open(self.gamename):
            time.sleep(0.2)
        # print("Got to pre-choose reward")
        # Then wait until the cards become selectable
        time.sleep(4)
        # Then choose a random card
        Events.choose_random_reward(self.gamename)
        # Then wait until store is detected
        # print("Got to pre-shop check")
        while not Events.detect_store(self.gamename):
            time.sleep(0.2)
        # print("Got to pre-sellrepair")
        # Then wait to see if chest event appears
        time.sleep(2)
        if Events.detect_endlevel_chest(self.gamename):
            pydirectinput.press('esc')
            time.sleep(0.05)
        # Then check for loot one last time
        AntiStickUtils.move_bigmap_dynamic(
            coords[0], coords[1], rect=self.room.rect, checkmap=False)
        while self.loot_everything(self.gamename):
            self.move_slightly_left()
            # Try once more to loot
            Looting.grab_nearby_loot(self.gamename)
            self.loot_everything(self.gamename)
            # Click centre of screen to skip
            self.skip_to_reward(self.gamename)
        # And then go to next level if needs be
        # print("Got to pre-restart")
        # self.calculate_profit(self.gamename)

    def perform_sell_and_repair(self):
        '''This function makes the necessary calls to sell all loot below 
        a particular rarity, and repair all equipped gear.'''
        # And then perform the sell and repair actions
        time.sleep(0.5)
        BotUtils.close_map_and_menu(self.gamename)
        time.sleep(0.5)
        sr = SellRepair()
        sr.ident_sell_repair()

    def loot_everything(self, gamename: str):
        '''This function makes the necessary calls to grab all visible 
        loot on screen

                Parameters:
                        gamename (str): Game window name.

                Returns:
                        bool: whether the command was completed successfully.'''
        player_name = False
        player_name = BotUtils.detect_player_name(gamename)
        if not player_name:
            # print("Didn't detect name")
            return Looting.grab_all_visible_lootv2(gamename)
        else:
            return Looting.grab_all_visible_lootv2(gamename, player_name)

    def skip_to_reward(self, gamename: str):
        '''This function clicks on the correct spot to skip the waiting
        period. Usually only called after skip has been detected.

                Parameters:
                        gamename (str): Game window name.
        '''
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+656, wincap.window_rect[1]+276)

    def perform_endlevel_event_handling(self):
        '''This is the high-level handling function for all
        end-of-map logic in the event map. Typically called
        only after end-level event has been detected. 
        '''
        time.sleep(0.4)
        RHClick.click_otherworld_ok(self.gamename)
        time.sleep(2)
        while not self.check_if_the_crack():
            time.sleep(0.006)
        # Then clear the area
        self.perform_otherworld_combat(self.gamename)
        # Then move to collect the loot
        self.navigate_otherworld_loot(self.gamename)
        # And then finally leave the otherworld
        self.leave_otherworld(self.gamename)

    def perform_otherworld_combat(self, gamename: str):
        '''This function makes the necessary calls to eliminate all 
        enemies in the end-level event map. It will loop until done.
        Also has anti-stick checks so that it doesn't get stuck
        infinitely nor does it cancel prematurely.

                Parameters:
                        gamename (str): Game window name.
        '''
        result = AntiStickUtils.move_bigmap_dynamic(660, 548)
        while not result:
            BotUtils.try_toggle_map_clicking()
            result = AntiStickUtils.move_bigmap_dynamic(660, 548)
        self.point_angle(0)
        time.sleep(0.01)
        CustomInput.press_key(CustomInput.key_map["h"])
        time.sleep(0.005)
        CustomInput.release_key(CustomInput.key_map["h"])
        time.sleep(1)
        result = AntiStickUtils.move_bigmap_dynamic(608, 532)
        self.point_angle(0)
        while not result:
            BotUtils.try_toggle_map_clicking()
            result = AntiStickUtils.move_bigmap_dynamic(608, 532)
        counter = 10
        start_time = time.time()
        while counter > 0:
            if self.detect_enemies_overworld(gamename):
                if counter < 10:
                    counter += 1
            else:
                counter -= 1
            self.perform_continue_clear()
            if time.time()-start_time > 20:
                # print("need to move closer to detected enemies")
                start_time = time.time() - 5
                result = False
                while not result:
                    BotUtils.try_toggle_map_clicking()
                    result = AntiStickUtils.move_bigmap_dynamic(660, 548)
                    self.point_angle(0)

    def move_slightly_left(self):
        '''This will simply move the player so that they're pointing to the 
        left. Will also result in slight movement also. Typically used
        during looting to do the equivalent of bashing something 
        electrical to get it to start. 
        '''
        CustomInput.press_key(CustomInput.key_map["left"], "left")
        time.sleep(0.15)
        CustomInput.release_key(CustomInput.key_map["left"], "left")
        time.sleep(0.1)

    def click_on_game(self, gamename: str):
        '''This function ensures that the game is the window in focus
        by clicking on the header bar at the top.

                Parameters:
                        gamename (str): Game window name.
        '''
        wincap = WindowCapture(gamename)
        centre_x = int(0.5 * wincap.w +
                       wincap.window_rect[0])
        centre_y = int(3 +
                       wincap.window_rect[1])
        ctypes.windll.user32.SetCursorPos(centre_x, centre_y)
        ctypes.windll.user32.mouse_event(
            0x0002, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(
            0x0004, 0, 0, 0, 0)

    def perform_move_into_bossroom(self, dir: str):
        '''This function moves the character in correct direction to start the 
        boss encounter

                Parameters:
                        dir (str): The (singular) direction key to press.
        '''
        time.sleep(0.01)
        # print("Got to here")
        CustomInput.press_key(CustomInput.key_map[dir], dir)
        # while True:
        #     time.sleep(0.005)
        #     if not BotUtils.detect_sect_clear(self.gamename):
        #         break
        #     if BotUtils.detect_boss_healthbar(self.gamename):
        #         break

    def release_dir_keys(self):
        '''This function makes sure that all direction keys are released.
        '''
        KEYS = {
            'left': 37,
            'up': 38,
            'right': 39,
            'down': 40
        }
        for key in ["up", "down", "left", "right"]:
            if ctypes.windll.user32.GetKeyState(KEYS[key]) > 2:
                CustomInput.release_key(CustomInput.key_map[key], key)

    def point_angle(self, angle: int):
        '''This function moves the character in correct direction to start the 
        boss encounter

                Parameters:
                        angle (int): The relative angle of position to point at 
                        e.g. 0 being north/up and 270 being west/left.
        '''
        key = "z"
        CustomInput.press_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        if angle >= 300 or angle < 60:
            CustomInput.press_key(CustomInput.key_map["up"], "up")
        if angle >= 210 and angle < 330:
            CustomInput.press_key(CustomInput.key_map["left"], "left")
        if angle >= 120 and angle < 240:
            CustomInput.press_key(CustomInput.key_map["down"], "down")
        if angle >= 30 and angle < 150:
            CustomInput.press_key(CustomInput.key_map["right"], "right")
        time.sleep(0.01)
        self.release_dir_keys()

    def check_if_the_crack(self):
        '''This function checks if character is in the endlevel event map

                    Returns:
                        bool: whether the endlevel event map was detected.
        '''
        if "ack" in BotUtils.detect_level_name(self.gamename):
            return True
        return False

    def perform_endlevel_loot(self):
        '''This function picks up all of the visible loot at the end of level.
        Differs from normal loot collect as it skips to reward if all loot 
        is picked up.
        '''
        while Events.detect_in_dungeon():
            if not self.loot_everything(self.gamename):
                self.move_slightly_left()
                # Try once more to loot
                Looting.grab_nearby_loot(self.gamename)
                self.loot_everything(self.gamename)
                # Click centre of screen to skip
                self.skip_to_reward(self.gamename)
                break

    def navigate_otherworld_loot(self, gamename: str):
        '''This function moves the character to the fixed loot point for 
        endlevel event and then picks up all loot. Calls movement functions 
        that are specifically resilient to getting stuck.

                Parameters:
                        gamename (str): Game window name.
        '''
        # BotUtils.try_toggle_map_clicking()
        result = AntiStickUtils.move_bigmap_dynamic(593, 419)
        while not result:
            BotUtils.try_toggle_map_clicking()
            result = AntiStickUtils.move_bigmap_dynamic(593, 419)
        AntiStickUtils.move_bigmap_dynamic(667, 392)
        while not result:
            BotUtils.try_toggle_map_clicking()
            result = AntiStickUtils.move_bigmap_dynamic(667, 392)
        BotUtils.close_map_and_menu(gamename)
        self.loot_everything(gamename)
        # Then have a second bite at looting
        AntiStickUtils.move_bigmap_dynamic(667, 407)
        self.loot_everything(gamename)

    def leave_otherworld(self, gamename: str):
        '''This function navigates the player to the endlevel event exit, and
        then selects the exit option and pauses for the required amount of time.

                Parameters:
                        gamename (str): Game window name.
        '''
        AntiStickUtils.move_bigmap_dynamic(667, 455)
        time.sleep(0.5)
        RHClick.click_yes(gamename)
        time.sleep(2.5)

    def detect_enemies_overworld(self, gamename) -> bool:
        '''This function is for detecting enemies specifically on the big
        map in the endlevel event area.

                Parameters:
                        gamename (str): Game window name.
                Returns:
                        bool: whether any enemies were detected.
        '''
        count = 0
        while not BotUtils.detect_bigmap_open(gamename):
            count += 1
            if count % 2 == 0:
                BotUtils.try_toggle_map()
            else:
                BotUtils.try_toggle_map_clicking()
            time.sleep(0.008)
        wincap = WindowCapture(gamename, [519, 304, 830, 610])
        othr_plyr_vision = Vision("otherplayerinvert.jpg")
        image = wincap.get_screenshot()
        filter = HsvFilter(0, 198, 141, 8, 255, 255, 0, 0, 0, 0)
        image = cv2.blur(image, (4, 4))
        image = BotUtils.filter_blackwhite_invert(filter, image)
        rectangles = othr_plyr_vision.find(
            image, threshold=0.41, epsilon=0.5)
        points = othr_plyr_vision.get_click_points(rectangles)
        if len(points) >= 1:
            return True
        return False

    def perform_loot(self, coords: tuple):
        '''This function is for looting a specific position on the big map.
        Grabs both the nearby loot and far away loot.

                Parameters:
                        coords (tuple): bigmap coords to check for loot
                Returns:
                        bool: whether the looting operation was successful.
        '''
        self.perform_navigation(coords)
        # Then perform looting as required
        time.sleep(0.3)
        while not self.loot_everything(self.gamename):
            self.move_slightly_left()
            # Try once more to loot
            Looting.grab_nearby_loot(self.gamename)
            self.loot_everything(self.gamename)
            self.perform_navigation(coords)
        return True

    def perform_wypt(self, coords: tuple):
        '''This function is for moving to a specific waypoint on the bigmap.
        Typically used when no other logic is required.

                Parameters:
                        coords (tuple): bigmap coords to move to
                Returns:
                        bool: whether the moving operation was successful.
        '''
        self.perform_navigation(coords)
        time.sleep(0.3)
        return True

    def perform_midlevel_event(self):
        '''This function will perform all handling for when a mid-level event
        is detected, including checking for a card to trade, and then both
        navigating to the event and accepting the challenge.
        '''
        time.sleep(0.1)
        while not Events.detect_in_dungeon():
            pydirectinput.press('esc')
            time.sleep(0.05)
            BotUtils.close_map_and_menu(self.gamename)
        time.sleep(0.3)
        # Check if user has cards available to trade
        if Events.detect_one_card(self.gamename):
            # Then try grab event pos
            x, y = BotUtils.find_midlevel_event(self.room.rect)
            if x:
                self.perform_navigation([x, y])
                pydirectinput.press("x")
                # Then need to accept card trade
                if Events.detect_yes_no(self.gamename):
                    RHClick.click_yes(self.gamename)
                    time.sleep(0.1)
                    pydirectinput.press('esc')
                    while not Events.detect_in_dungeon():
                        pydirectinput.press('esc')
                        time.sleep(0.05)
                        BotUtils.close_map_and_menu(self.gamename)
        else:
            print("Don't have a card available to trade")

    def summon_momo(self):
        '''This function performs the necessary actions to summon the
        autolooting pet.
        '''
        wincap = WindowCapture(self.gamename)
        x = wincap.window_rect[0]
        y = wincap.window_rect[1]
        pydirectinput.press("j")
        time.sleep(0.1)
        while not BotUtils.detect_petmenu_open(self.gamename):
            pydirectinput.press("j")
            time.sleep(0.25)
        pydirectinput.click(x+471, y+178)
        time.sleep(0.1)
        pydirectinput.click(x+713, y+682)
        time.sleep(0.1)
        # Now empty first 3 inventory slots
        pydirectinput.click(x+471, y+178)
        time.sleep(0.05)
        pydirectinput.rightClick(x+683, y+277)
        time.sleep(0.05)
        pydirectinput.rightClick(x+728, y+277)
        time.sleep(0.05)
        # pydirectinput.rightClick(x+772, y+277)
        # time.sleep(0.1)
        # pydirectinput.rightClick(x+814, y+277)
        # time.sleep(0.1)
        pydirectinput.press("esc")
        time.sleep(0.1)

    def cancel_momo_summon(self):
        '''This function performs the necessary actions to cancel the 
        summon of the autolooting pet.
        '''
        wincap = WindowCapture(self.gamename)
        x = wincap.window_rect[0]
        y = wincap.window_rect[1]
        pydirectinput.rightClick(x+82, y+197)
        time.sleep(0.1)
        pydirectinput.click(x+148, y+213)
        time.sleep(0.1)
        # print("Got to pet off")

    def face_direction(self, dir: str):
        '''This function points the character in a certain direction. Typically
        only used for targeting during combat, and for opening chests.

                Parameters:
                        dir (str): direction to face e.g. up, down, left, right
        '''
        key = "z"
        CustomInput.press_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.press_key(CustomInput.key_map[dir], dir)
        time.sleep(0.003)
        CustomInput.release_key(CustomInput.key_map[dir], dir)

    def hit_chest(self):
        '''This function is used to attack a nearby chest. Requires pointing
        in the correct direction beforehand. Will make sure to pick up existing
        loot in case chest already opened.
        '''
        Looting.grab_nearby_loot(self.gamename)
        key = self.weapon.chest_open
        if key != "x":
            available = self.grab_off_cooldown(
                [key], self.gamename)
            while not available:
                # Need to dodge right and left?
                time.sleep(0.05)
                available = self.grab_off_cooldown(
                    [key], self.gamename)
        CustomInput.press_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map[key], key)
        time.sleep(0.3)
        CustomInput.press_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map[key], key)

    def perform_navigation(self, coords: tuple, sectclr_chk: bool = False):
        '''This function is used to reposition the character to another
        point on the big map. It comes with the option to cancel movement
        if the section is cleared prior to the movement being completed.
                Parameters:
                        coords (tuple): bigmap coords to move character to.
                        sectclr_chk (bool): whether to cancel if section
                        is cleared prior to finishing.
                Returns:
                        bool: whether movement completed successfully, 
                        typically only false is useful.
        '''

        if not sectclr_chk:
            outcome = AntiStickUtils.move_bigmap_dynamic(
                int(coords[0]), int(coords[1]), closemap=False)
            nodetcnt = 0
            while not outcome:
                nodetcnt += 1
                if nodetcnt > 10:
                    print("ERROR WITH NAVIGATION")
                    return False
                    # os._exit(1)
                if nodetcnt % 3 == 0:
                    key = "right"
                    CustomInput.press_key(CustomInput.key_map[key], key)
                    CustomInput.release_key(CustomInput.key_map[key], key)
                outcome = AntiStickUtils.move_bigmap_dynamic(
                    int(coords[0]), int(coords[1]), closemap=False)
        else:
            outcome = AntiStickUtils.move_bigmap_dynamic_sectclrchk(
                int(coords[0]), int(coords[1]), closemap=False)
            nodetcnt = 0
            while not outcome:
                if BotUtils.detect_sect_clear(self.gamename):
                    return True
                nodetcnt += 1
                if nodetcnt > 10:
                    print("ERROR WITH NAVIGATION")
                    return False
                    # os._exit(1)
                if nodetcnt % 3 == 0:
                    key = "right"
                    CustomInput.press_key(CustomInput.key_map[key], key)
                    CustomInput.release_key(CustomInput.key_map[key], key)
                outcome = AntiStickUtils.move_bigmap_dynamic_sectclrchk(
                    int(coords[0]), int(coords[1]), closemap=False)
        return True

    def perform_primary_clear(self):
        key = self.weapon.primary_clear
        CustomInput.press_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map[key], key)
        self.maphandler.last_clear = time.time()

    def perform_continue_clear(self):
        available = self.grab_off_cooldown(
            self.weapon.continue_clear, self.gamename)
        if not available:
            # Need to dodge right and left?
            return False
        else:
            key = available[0]
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(0.015)
            CustomInput.release_key(CustomInput.key_map[key], key)
            if key == self.weapon.primary_clear:
                self.maphandler.last_clear = time.time()
            time.sleep(0.2)

    def perform_boss_combo(self):
        available = self.grab_off_cooldown(
            self.weapon.continue_boss, self.gamename)
        if not available:
            # Need to dodge right and left?
            return False
        else:
            key = available[0]
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(0.015)
            CustomInput.release_key(CustomInput.key_map[key], key)
            time.sleep(0.2)

    def calculate_travel_time(self, x, y, currx=False, curry=False, closemap=False):
        if not currx:
            if not BotUtils.detect_bigmap_open(self.gamename):
                BotUtils.try_toggle_map_clicking(self.gamename)
            currx, curry = BotUtils.grab_player_posv2(
                self.gamename, [x-75, y-75, x+75, y+75])
            if closemap:
                BotUtils.close_map_and_menu(self.gamename)
        xdist = abs(currx - int(x))
        ydist = abs(int(y) - curry)
        smaller = min(xdist, ydist)
        diag = math.hypot(smaller, smaller)
        travel_time = (diag + max(xdist, ydist) - smaller)/30
        return travel_time

    def aim_at_enemies(self):
        points = self.grab_enemy_points()
        if points:
            if points[0][0] < 94:
                CustomInput.press_key(CustomInput.key_map["left"], "left")
            if points[0][0] > 94:
                CustomInput.press_key(CustomInput.key_map["right"], "right")
            if points[0][1] < 69:
                CustomInput.press_key(CustomInput.key_map["up"], "up")
            if points[0][1] > 69:
                CustomInput.press_key(CustomInput.key_map["down"], "down")
            time.sleep(0.005)
            BotUtils.stop_movement()

    def find_nearest_enemy(self):
        try:
            points = self.grab_enemy_points()[0]
        except:
            return False
        return [points[0] - 94, 69-points[1]]

    def grab_off_cooldown(self, skill_list=False, gamename=False):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        if not skill_list:
            skill_list = ["a", "s", "d", "f", "g", "h"]
        available = []
        wincap = WindowCapture(gamename, [395, 745, 591, 748])
        image = wincap.get_screenshot()
        a, _, _ = [int(i) for i in image[0][0]]
        b, _, _ = [int(i) for i in image[0][39]]
        c, _, _ = [int(i) for i in image[0][78]]
        d, _, _ = [int(i) for i in image[0][117]]
        e, _, _ = [int(i) for i in image[0][156]]
        f, _, _ = [int(i) for i in image[0][195]]
        if a == 56 and "a" in skill_list:
            available.append("a")
        if b == 11 and "s" in skill_list:
            available.append("s")
        if c == 44 and "d" in skill_list:
            available.append("d")
        if d == 245 and "f" in skill_list:
            available.append("f")
        if e == 231 and "g" in skill_list:
            available.append("g")
        if f == 142 and "h" in skill_list:
            available.append("h")
        if len(available) > 0:
            return available
        else:
            return False

    def grab_enemy_points(self):
        minimap_screenshot = self.enemy_minimap_wincap.get_screenshot()
        # pre-process the image to help with detection
        enemy_output_image = BotUtils.apply_hsv_filter(
            minimap_screenshot, self.enemy_minimap_filter)
        # do object detection, this time grab points
        enemy_rectangles = self.enemy_minimap_vision.find(
            enemy_output_image, threshold=0.61, epsilon=0.5)
        # then return answer to whether enemies are detected
        if len(enemy_rectangles) >= 1:
            points = self.enemy_minimap_vision.get_click_points(
                enemy_rectangles)
            return points
        return False


class AntiStickUtils:
    # This class is specially-developed utility functions
    # Which are modified to catch times where the bot has gotten stuck
    def move_bigmap_dynamic(x, y, gamename=False, rect=False, checkmap=True, closemap=True):
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        if Events.detect_yes_no(gamename):
            RHClick.click_no(gamename)
        if checkmap:
            count = 0
            while not BotUtils.detect_bigmap_open(gamename):
                count += 1
                if count % 2 == 0:
                    BotUtils.try_toggle_map_clicking()
                else:
                    BotUtils.try_toggle_map()
                time.sleep(0.03)
        else:
            BotUtils.try_toggle_map()
        # Then need to find where the player is
        if not rect:
            rect = [561, 282, 1111, 666]
        playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
        if not playerx:
            if not checkmap:
                time.sleep(0.5)
                BotUtils.try_toggle_map()
                time.sleep(0.005)
                playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
                if not playerx:
                    return False
            else:
                time.sleep(0.5)
                BotUtils.try_toggle_map()
                time.sleep(0.005)
                playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
                if not playerx:
                    print("Unable to find player")
                    return False
        relx = x - playerx
        rely = playery - y
        margin = 1
        follower = Follower(margin)
        noplyr_count = 0
        start_time = time.time()
        while abs(relx) > margin or abs(rely) > margin:
            rect = [playerx - 50, playery - 50, playerx + 50, playery + 50]
            playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
            if playerx:
                if noplyr_count > 0:
                    noplyr_count -= 1
                relx = x - playerx
                rely = playery - y
                follower.navigate_towards(relx, rely)
            else:
                noplyr_count += 1
                if noplyr_count > 10:
                    break
            if time.time() - start_time > 10:
                print("Got stuck during navigation")
                BotUtils.try_toggle_map()
                follower.release_all_keys()
                return False
            time.sleep(0.02)
        follower.release_all_keys()
        if closemap:
            BotUtils.try_toggle_map()
        if noplyr_count > 10:
            return False
        else:
            return True

    def move_bigmap_dynamic_sectclrchk(x, y, gamename=False, rect=False, checkmap=True, closemap=True):
        if BotUtils.detect_sect_clear(gamename):
            return True
        if not gamename:
            with open("gamename.txt") as f:
                gamename = f.readline()
        if Events.detect_yes_no(gamename):
            RHClick.click_no(gamename)
        if checkmap:
            count = 0
            while not BotUtils.detect_bigmap_open(gamename):
                count += 1
                if count % 2 == 0:
                    BotUtils.try_toggle_map_clicking()
                else:
                    BotUtils.try_toggle_map()
                time.sleep(0.03)
        else:
            BotUtils.try_toggle_map()
        if BotUtils.detect_sect_clear(gamename):
            return True
        # Then need to find where the player is
        if not rect:
            rect = [561, 282, 1111, 666]
        playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
        if not playerx:
            if not checkmap:
                if BotUtils.detect_sect_clear(gamename):
                    return True
                time.sleep(0.5)
                BotUtils.try_toggle_map()
                time.sleep(0.005)
                playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
                if not playerx:
                    return False
            else:
                time.sleep(0.5)
                BotUtils.try_toggle_map()
                time.sleep(0.005)
                playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
                if not playerx:
                    print("Unable to find player")
                    return False
        relx = x - playerx
        rely = playery - y
        margin = 1
        follower = Follower(margin)
        noplyr_count = 0
        start_time = time.time()
        while abs(relx) > margin or abs(rely) > margin:
            if BotUtils.detect_sect_clear(gamename):
                follower.release_all_keys()
                return True
            rect = [playerx - 50, playery - 50, playerx + 50, playery + 50]
            playerx, playery = BotUtils.grab_player_posv2(gamename, rect)
            if playerx:
                if noplyr_count > 0:
                    noplyr_count -= 1
                relx = x - playerx
                rely = playery - y
                follower.navigate_towards(relx, rely)
            else:
                noplyr_count += 1
                if noplyr_count > 10:
                    break
            if time.time() - start_time > 10:
                print("Got stuck during navigation")
                BotUtils.try_toggle_map()
                follower.release_all_keys()
                return False
            time.sleep(0.02)
        follower.release_all_keys()
        if closemap:
            BotUtils.try_toggle_map()
        if noplyr_count > 10:
            return False
        else:
            return True


def load_level_data(filename: str):
    """This functions simply loads the given database
    And returns the list of room data
            Parameters:
                    filename (str): Path to database

            Returns:
                    list_rooms (list): 2D list containing data for all rooms
    """
    with open(filename) as f:
        lines = f.readlines()
    list_rooms = []
    for line in lines:
        list_rooms.append(Room(line))
    return list_rooms


filename = os.path.dirname(
    os.path.abspath(__file__)) + "/levels/map10updated.txt"
rooms = load_level_data(filename)
wp = Weapon("MS")
mh = MapHandler(rooms, wp)
time.sleep(2)
mh.start(False)
