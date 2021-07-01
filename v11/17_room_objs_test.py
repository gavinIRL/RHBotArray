# This file will test how to best store data on each room
# Will preferably load information from a single file
from threading import Thread
import time
import os
import numpy as np
import cv2
import math
import ctypes
import logging
from fuzzywuzzy import fuzz
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter, Follower
import pydirectinput
from custom_input import CustomInput
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logging.getLogger().setLevel(logging.ERROR)


class Map10_MS30():
    def __init__(self, roomdata):
        self.rooms = roomdata
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

    def start(self, repeat=False):
        time.sleep(1.5)
        while not Events.detect_in_dungeon():
            time.sleep(0.25)
        self.summon_momo(self.gamename)
        # Now using full universal room handler instead
        for room in self.rooms:
            rh = RoomHandler(room)
            rh.start_room()
        # And then perform the endmap routine
        self.perform_endmap(repeat)


class Weapon:
    def __init__(self, weapon="MS") -> None:
        if weapon == "MS":
            self.primary_clear = "h"
            self.continue_clear = ["h", "a", "g", "f", "s", "d"]
            self.continue_boss = ["a", "g", "f", "s", "d"]


class Room():
    def __init__(self, line: str) -> None:
        # Format of each line in the file should be as follows
        # rect # coords_n | coords_n+1 # action_n | action_n+1 # tags
        # ------------------------------------
        # format rect is leftx, topy, rightx, bottomy
        # format coords is x,y
        # ------------------------------------
        # list actions is as follows:
        # clear,dir - position to perform clear from, point left
        # boss,dir - position to perform boss attacks from
        # exit - position to exit room from
        # chest,dir - position to attack chest, point left
        # repos,dir,5 - position to reposition to, point left, after seconds
        # loot - position to attempt to loot from
        # wypt - this is a travel waypoint only
        # ------------------------------------
        # list of tags is as follows
        # pet,on - this makes sure the pet is summoned (pre) or hidden (post)
        # nxtbss,dir - next room is the boss room, hold l to enter
        # curbss - this room is the boss room
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
    def __init__(self, room: Room, weapon: Weapon) -> None:
        # Add a timestamp to catch if have gotten stuck
        self.last_event_time = time.time()
        self.weapon = weapon
        self.room = room
        with open("gamename.txt") as f:
            self.gamename = f.readline()

    def start_room(self):
        room = self.room
        # Check through the tags first
        tags = "".join(room.tags)
        acts = "".join(room.action_list)
        curbss = False if not "curbss" in tags else True
        nxtbss = False if not "nxtbss" in tags else True
        peton = False if not "pet,on" in tags else True
        petoff = False if not "pet,off" in tags else True
        repos = False if not "repos" in acts else True
        sect_cleared = False
        nxtbss_dir = False
        # Check which direction for nxtboss if reqd
        if nxtbss:
            nxtbss_dir = tags.split("curbss", 1)[1].split("|", 1)[
                0].replace(",", "")

        # Then go through the actions and carry them out
        for i, action in enumerate(room.action_list):
            self.last_event_time = time.time()
            # Need to check if reposition is the next item
            repos_time = False
            if repos:
                next = room.action_list[i+1]
                if "repos" in next:
                    _, _, repos_time = next.split(",")
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
                outcome = self.perform_exit(coords, nxtbss_dir, petoff)
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
                if not curbss:
                    self.perform_loot(coords)
                else:
                    self.perform_endlevel(coords)
            elif "wypt" in action:
                outcome = self.perform_wypt(coords)
                if not outcome:
                    print("Problem with nav during exit, need to add handling")
                    os._exit(1)

    def perform_clear(self, coords, dir, repos=False):
        self.perform_navigation(coords, True)
        self.face_direction(dir)
        if not repos:
            while not BotUtils.detect_sect_clear(self.gamename):
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
            if not need_to_repos:
                return True
            return False

    def perform_boss(self, coords, dir, repos=False, curbss=False):
        self.perform_navigation(coords, True)
        self.face_direction(dir)
        if not repos:
            pass
            # Then need to start the primary bosskill combo
            # And continue attacking until bosskill is detected
            if curbss:
                pass
            # or else until sectclear detected
            else:
                pass
        # Alternative handling if reposition is required mid-clear
        else:
            pass
            # Then need to start the primary bosskill combo
            # And continue attacking until bosskill is detected
            # or reposition time has been reached
            if curbss:
                pass
            # or else until sectclear detected
            # or reposition time has been reached
            else:
                pass

    def perform_exit(self, coords, nxtbss_dir=False, petoff=False):
        self.perform_navigation(coords)
        # Then turn pet off if required
        if petoff:
            self.cancel_momo_summon()
        if nxtbss_dir:
            # Need to press down the required key
            CustomInput.press_key(CustomInput.key_map[nxtbss_dir], nxtbss_dir)
        else:
            time.sleep(0.3)
        return True

    def perform_chest(self, coords, dir):
        self.perform_navigation(coords)
        self.face_direction(dir)
        self.hit_chest()

    def perform_repos(self, coords, dir):
        self.perform_navigation(coords, True)
        self.face_direction(dir)

    def perform_endlevel(self, coords):
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

    def perform_endlevel_event_handling(self):
        pass

    def perform_endlevel_loot(self):
        while Events.detect_in_dungeon():
            if not self.loot_everything(self.gamename):
                self.move_slightly_left()
                # Try once more to loot
                Looting.grab_nearby_loot(self.gamename)
                self.loot_everything(self.gamename)
                # Click centre of screen to skip
                self.skip_to_reward(self.gamename)
                break

    def perform_loot(self, coords):
        self.perform_navigation(coords)
        # Then perform looting as required
        time.sleep(0.3)
        return True

    def perform_wypt(self, coords):
        self.perform_navigation(coords)
        time.sleep(0.3)
        return True

    def perform_midlevel_event(self):
        pass

    def cancel_momo_summon(self):
        wincap = WindowCapture(self.gamename)
        x = wincap.window_rect[0]
        y = wincap.window_rect[1]
        pydirectinput.rightClick(x+82, y+197)
        time.sleep(0.1)
        pydirectinput.click(x+148, y+213)
        time.sleep(0.1)

    def face_direction(self, dir):
        CustomInput.press_key(CustomInput.key_map[dir], dir)
        CustomInput.release_key(CustomInput.key_map[dir], dir)

    def hit_chest(self):
        Looting.grab_nearby_loot(self.gamename)
        key = "x"
        CustomInput.press_key(CustomInput.key_map[key], key)
        CustomInput.release_key(CustomInput.key_map[key], key)
        time.sleep(0.3)
        CustomInput.press_key(CustomInput.key_map[key], key)
        CustomInput.release_key(CustomInput.key_map[key], key)

    def perform_navigation(self, coords, sectclr_chk=False):
        if not sectclr_chk:
            outcome = AntiStickUtils.move_bigmap_dynamic(
                int(coords[0]), int(coords[1]))
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
                    int(coords[0]), int(coords[1]))
        else:
            outcome = AntiStickUtils.move_bigmap_dynamic_sectclrchk(
                int(coords[0]), int(coords[1]))
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
                    int(coords[0]), int(coords[1]))

    def perform_primary_clear(self):
        key = self.weapon.primary_clear
        CustomInput.press_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map[key], key)

    def perform_continue_clear(self):
        for key in self.weapon.continue_clear:
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(0.02)
            CustomInput.release_key(CustomInput.key_map[key], key)

    def perform_boss_combo(self):
        for key in self.weapon.continue_boss:
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(0.02)
            CustomInput.release_key(CustomInput.key_map[key], key)

    def calculate_travel_time(self, x, y, currx=False, curry=False):
        if not currx:
            if not BotUtils.BotUtils.detect_bigmap_open(self.gamename):
                BotUtils.try_toggle_map_clicking(self.gamename)
            currx, curry = BotUtils.grab_player_posv2(
                self.gamename, [x-75, y-75, x+75, y+75])
            BotUtils.close_map_and_menu(self.gamename)
        xdist = abs(currx - int(x))
        ydist = abs(int(y) - curry)
        smaller = min(xdist, ydist)
        diag = math.hypot(smaller, smaller)
        travel_time = (diag + max(xdist, ydist) - smaller)/self.speed
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

    def check_bigmap_open(gamename=False):
        pass

    def open_bigmap(gamename=False):
        pass

    def move_bigmap_dynamic(x, y, gamename=False, rect=False, checkmap=True):
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
        BotUtils.try_toggle_map()
        if noplyr_count > 10:
            return False
        else:
            return True

    def move_bigmap_dynamic_sectclrchk(x, y, gamename=False, rect=False, checkmap=True):
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
        BotUtils.try_toggle_map()
        if noplyr_count > 10:
            return False
        else:
            return True


def load_level_data(filename):
    with open(filename) as f:
        lines = f.readlines()
    list_rooms = []
    for line in lines:
        list_rooms.append(Room(line))
    return list_rooms


filename = os.path.dirname(
    os.path.abspath(__file__)) + "/levels/map10updated.txt"
rooms = load_level_data(filename)
room1 = rooms[0]
print(room1.action_list)
