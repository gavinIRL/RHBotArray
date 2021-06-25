# This file will automatically run through map 10
from random import randint
import time
import os
import numpy as np
import cv2
import math
import ctypes
import logging
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter
import pydirectinput
from custom_input import CustomInput
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logging.getLogger().setLevel(logging.ERROR)


class Map10_MS30():
    def __init__(self):
        self.rooms = self.load_map_rooms()
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

    def load_map_rooms(self):
        # Temporary, will be replace by objects later
        # that will load from a database file
        return_list = []
        filepath = os.path.dirname(
            os.path.abspath(__file__)) + "/levels/map10.txt"
        with open(filepath) as file:
            lines = file.readlines()
        for line in lines:
            return_list.append(line.split(","))
        return return_list

    def start(self, repeat=False):
        self.summon_momo(self.gamename)
        # Using placeholder individual methods for now
        self.perform_room1()
        for i in range(4):
            self.perform_room_after_first(i+1)
        # Then move into the boss room
        BotUtils.move_diagonal(882, 615, self.speed)
        # Cancel summon of momo
        self.cancel_momo_summon(self.gamename)
        # And then perform the endmap routine
        self.perform_endmap(repeat)

    def perform_room1(self):
        time.sleep(2)
        room = self.rooms[0]
        BotUtils.move_diagonal(int(room[1]), int(room[2]), self.speed)
        time.sleep(0.4)
        self.roomclear_skill()
        time.sleep(0.6)
        aim_cd = time.time()
        move_cd = time.time()
        while not BotUtils.detect_sect_clear(self.gamename):
            if time.time() - aim_cd > 2:
                print("Aiming at enemies again")
                self.aim_at_enemies()
                aim_cd = time.time()
                self.continue_clear()
            elif time.time() - move_cd > 6:
                print("Moving closer to the enemy")
                # prob need to move closer to enemies at this point
                points = self.find_nearest_enemy()
                if points:
                    result = self.move_diagonal_sectclrdet(
                        points[0], points[1], self.speed*4, self.gamename)
                    if result:
                        BotUtils.stop_movement()
                        break
                    move_cd = time.time()
                else:
                    move_cd = time.time() - 4
            else:
                self.continue_clear()
                # BotUtils.stop_movement()
        time.sleep(1.4)

    def perform_room_after_first(self, num):
        room = self.rooms[num-1]
        print("{},{}".format(int(room[1]), int(room[2])))
        # print("Just about to move to next roomstart, room {}".format(num))
        BotUtils.move_diagonal(int(room[3]), int(room[4]), self.speed)
        # print("Finished moving to next roomstart, room {}".format(num))
        time.sleep(0.4)
        # Now calculate the travel time to figure out
        # How long to sleep before moving to room2 spot
        targetx = self.rooms[num][1]
        targety = self.rooms[num][2]
        travel_time = self.calculate_travel_time(
            targetx, targety, int(room[3]), int(room[4]))
        sleep_time = self.last_clear + self.clearskill_cd - time.time() - travel_time
        if sleep_time > 0:
            time.sleep(sleep_time)
        room = self.rooms[num]
        # print("Preparing to move to clear position, room {}".format(num))
        BotUtils.move_diagonal(int(room[1]), int(room[2]), self.speed)
        time.sleep(0.6)
        self.roomclear_skill()
        time.sleep(0.6)
        aim_cd = time.time()
        move_cd = time.time()
        while not BotUtils.detect_sect_clear(self.gamename):
            if time.time() - aim_cd > 2:
                print("Aiming at enemies again")
                self.aim_at_enemies()
                aim_cd = time.time()
                self.continue_clear()
            elif time.time() - move_cd > 6:
                print("Moving closer to the enemy")
                # prob need to move closer to enemies at this point
                points = self.find_nearest_enemy()
                if points:
                    result = self.move_diagonal_sectclrdet(
                        points[0], points[1], self.speed*4, self.gamename)
                    if result:
                        BotUtils.stop_movement()
                        break
                    move_cd = time.time()
                else:
                    move_cd = time.time() - 4
            else:
                self.continue_clear()
                # BotUtils.stop_movement()
        time.sleep(1.4)
        # BotUtils.stop_movement()
        print("Finished combat in room {}".format(num))

    def perform_endmap(self, repeat=False):
        self.kill_boss(self.gamename)
        self.start_endlevel_script(self.gamename, repeat)

    def cancel_momo_summon(self, gamename):
        wincap = WindowCapture(gamename)
        x = wincap.window_rect[0]
        y = wincap.window_rect[1]
        pydirectinput.rightClick(x+82, y+197)
        time.sleep(0.1)
        pydirectinput.click(x+148, y+213)
        time.sleep(0.1)

    def summon_momo(self, gamename):
        wincap = WindowCapture(gamename)
        x = wincap.window_rect[0]
        y = wincap.window_rect[1]
        pydirectinput.press("j")
        time.sleep(0.1)
        pydirectinput.click(x+471, y+178)
        time.sleep(0.1)
        pydirectinput.click(x+713, y+682)
        time.sleep(0.1)
        pydirectinput.press("esc")
        time.sleep(0.1)

    def calculate_travel_time(self, x, y, currx=False, curry=False):
        if not currx:
            if not BotUtils.BotUtils.detect_bigmap_open(self.gamename):
                BotUtils.try_toggle_map_clicking(self.gamename)
            currx, curry = BotUtils.grab_player_pos(
                self.gamename, [x-75, y-75, x+75, y+75])
            BotUtils.close_map_and_menu(self.gamename)
        xdist = abs(currx - int(x))
        ydist = abs(int(y) - curry)
        travel_time = (math.sqrt(xdist ^ 2+ydist ^ 2))/self.speed
        return travel_time

    def roomclear_skill(self):
        CustomInput.press_key(CustomInput.key_map["h"])
        time.sleep(0.01)
        CustomInput.release_key(CustomInput.key_map["h"])
        self.last_clear = time.time()

    def continue_clear(self):
        available = self.grab_off_cooldown(
            ["a", "g", "f", "s", "d"], self.gamename)
        if not available:
            # Need to dodge right and left?
            return False
        else:
            key = available[0]
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(0.015)
            CustomInput.release_key(CustomInput.key_map[key], key)
            time.sleep(0.2)

    def aim_at_enemies(self):
        points = self.grab_enemy_points()
        if points:
            # print("Enemy detected at {}".format(points[0]))
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
            # output_image = self.enemy_minimap_vision.draw_crosshairs(
            #     minimap_screenshot, [points[0]])
            # name = str(points[0][0])+"-"+str(points[0][1])
            # cv2.imwrite("C:\\Games\\"+name +
            #             ".jpg", output_image)
            return points
        return False

    def move_diagonal_sectclrdet(self, x, y, speed=40, gamename=False):
        # Can only be a relative input
        relx = x
        rely = y
        mult = 0.707
        if relx > 0:
            keyx = "left"
            CustomInput.press_key(CustomInput.key_map["left"], "left")
            timeleftx = float("{:.4f}".format(abs(relx/(speed*mult))))
        elif relx < 0:
            keyx = "right"
            CustomInput.press_key(CustomInput.key_map["right"], "right")
            timeleftx = float("{:.4f}".format(abs(relx/(speed*mult))))
        else:
            keyx = "right"
            timeleftx = 0
            mult = 1
        if rely > 0:
            keyy = "down"
            CustomInput.press_key(CustomInput.key_map["down"], "down")
            timelefty = float("{:.4f}".format(abs(rely/(speed*mult))))
        elif rely < 0:
            keyy = "up"
            CustomInput.press_key(CustomInput.key_map["up"], "up")
            timelefty = float("{:.4f}".format(abs(rely/(speed*mult))))
        else:
            keyy = "up"
            timelefty = 0
            if relx != 0:
                timeleftx = float("{:.4f}".format(abs(relx/speed)))
        first_sleep = min([timeleftx, timelefty])
        second_sleep = max([timeleftx, timelefty])
        first_key = [keyx, keyy][[timeleftx, timelefty].index(first_sleep)]
        second_key = [keyx, keyy][[timeleftx, timelefty].index(second_sleep)]
        if first_sleep < 0.009:
            if second_sleep < 0.009:
                pass
            else:
                start = time.time()
                while time.time() - start < second_sleep - 0.009:
                    if BotUtils.detect_sect_clear(gamename):
                        BotUtils.stop_movement()
                        return True
                    time.sleep(0.005)
                CustomInput.release_key(
                    CustomInput.key_map[second_key], second_key)
        elif timelefty == timeleftx:
            start = time.time()
            while time.time() - start < first_sleep - 0.009:
                if BotUtils.detect_sect_clear(gamename):
                    BotUtils.stop_movement()
                    return True
                time.sleep(0.005)
            CustomInput.release_key(CustomInput.key_map[first_key], first_key)
            CustomInput.release_key(
                CustomInput.key_map[second_key], second_key)
        else:
            start = time.time()
            while time.time() - start < first_sleep - 0.009:
                if BotUtils.detect_sect_clear(gamename):
                    BotUtils.stop_movement()
                    return True
                time.sleep(0.005)
            CustomInput.release_key(CustomInput.key_map[first_key], first_key)
            start = time.time()
            while time.time() - start < (second_sleep-first_sleep-0.009)*mult:
                if BotUtils.detect_sect_clear(gamename):
                    BotUtils.stop_movement()
                    return True
                time.sleep(0.005)
            CustomInput.release_key(
                CustomInput.key_map[second_key], second_key)
        return False

    # Everything below this is for endmap handling from test 18
    def start_endlevel_script(self, gamename, repeat=False):
        # Need to first wait until dungeon check returns false
        while Events.detect_in_dungeon():
            time.sleep(0.006)
        # print("Got to pre-sectclear detect")
        # Then until sect cleared shows up
        while not BotUtils.detect_sect_clear():
            pydirectinput.press('esc')
            time.sleep(0.05)
        # print("Got to pre-endlevel event check")
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
                time.sleep(0.5)
                if Events.detect_move_reward_screen(gamename):
                    break
                # Then if ok is detected turn flag on
                if Events.detect_endlevel_bonus_area(gamename):
                    event = True
                break
        # Then do the appropriate handling if event is detected
        # print("Got to pre-event handling")
        if event:
            self.do_otherworld_handling(gamename)
        # Once event is complete move to correct place in room
        self.move_to_loot_point(gamename)
        # And then commence looting
        # print("Got to post-move to loot point")
        while Events.detect_in_dungeon():
            if not self.loot_everything(gamename):
                # Click centre of screen to skip
                self.skip_to_reward(gamename)
                break
        # print("Got to pre-card check")
        # Then wait until card select appears
        while not Events.detect_reward_choice_open(gamename):
            time.sleep(0.2)
        # print("Got to pre-choose reward")
        # Then wait until the cards become selectable
        time.sleep(4)
        # Then choose a random card
        Events.choose_random_reward(gamename)
        # Then wait until store is detected
        # print("Got to pre-shop check")
        while not Events.detect_store(gamename):
            time.sleep(0.2)
        # print("Got to pre-sellrepair")
        # Then wait to see if chest event appears
        time.sleep(2)
        if Events.detect_endlevel_chest(gamename):
            pydirectinput.press('esc')
            time.sleep(0.05)
        # Then check for loot one last time
        self.check_loot_preshop(gamename)
        # And then perform the sell and repair actions
        sr = SellRepair()
        sr.ident_sell_repair()
        # And then go to next level if needs be
        # print("Got to pre-restart")
        if repeat:
            self.repeat_level(gamename)

    def do_otherworld_handling(self, gamename):
        time.sleep(0.4)
        RHClick.click_otherworld_ok(gamename)
        time.sleep(2)
        while not self.check_if_the_crack(gamename):
            time.sleep(0.006)
        # Then clear the area
        self.perform_otherworld_combat(gamename)
        # Then move to collect the loot
        self.navigate_otherworld_loot(gamename)
        # And then finally leave the otherworld
        self.leave_otherworld(gamename)

    def check_if_the_crack(self, gamename):
        if "ack" in BotUtils.detect_level_name(gamename):
            return True
        return False

    def perform_otherworld_combat(self, gamename):
        CustomInput.press_key(CustomInput.key_map["down"], "down")
        time.sleep(2)
        CustomInput.release_key(CustomInput.key_map["down"], "down")
        time.sleep(0.005)
        CustomInput.press_key(CustomInput.key_map["up"], "up")
        time.sleep(0.005)
        CustomInput.release_key(CustomInput.key_map["up"], "up")
        time.sleep(0.01)
        CustomInput.press_key(CustomInput.key_map["h"])
        time.sleep(0.005)
        CustomInput.release_key(CustomInput.key_map["h"])
        start_time = time.time()
        while self.detect_enemies_overworld(gamename):
            self.continue_otherworld_attacks()
            if time.time()-start_time > 20:
                print("need to move closer to detected enemies")
                os._exit(1)

    def continue_otherworld_attacks(self):
        for key in ["a", "g", "f", "h"]:
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(0.02)
            CustomInput.release_key(CustomInput.key_map[key], key)

    def navigate_otherworld_loot(self, gamename):
        if not BotUtils.detect_bigmap_open(gamename):
            BotUtils.try_toggle_map()
        player_pos = BotUtils.grab_player_pos()
        BotUtils.try_toggle_map()
        relx = player_pos[0] - 590
        rely = 468 - player_pos[1]
        BotUtils.move_diagonal(relx, rely, 50, True)
        relx = 590 - 667
        rely = 407 - 468
        BotUtils.move_diagonal(relx, rely, 50, True)
        while BotUtils.detect_bigmap_open(gamename):
            BotUtils.try_toggle_map()
            time.sleep(0.01)
        self.loot_everything(gamename)

    def leave_otherworld(self, gamename):
        if not BotUtils.detect_bigmap_open(gamename):
            BotUtils.try_toggle_map()
        player_pos = BotUtils.grab_player_pos()
        BotUtils.try_toggle_map()
        relx = player_pos[0] - 667
        rely = 455 - player_pos[1]
        BotUtils.move_diagonal(relx, rely, 50, True)
        os._exit(1)

    def detect_enemies_overworld(self, gamename):
        if not BotUtils.detect_bigmap_open(gamename):
            BotUtils.try_toggle_map()
        wincap = WindowCapture(gamename, [530, 331, 781, 580])
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

    def move_to_loot_point(self, gamename):
        # Placeholder for now
        CustomInput.press_key(CustomInput.key_map["right"], "right")
        # CustomInput.press_key(CustomInput.key_map["up"], "up")
        time.sleep(0.3)
        CustomInput.release_key(CustomInput.key_map["right"], "right")
        # CustomInput.release_key(CustomInput.key_map["up"], "up")

    def check_loot_preshop(self, gamename):
        # Simple placeholder for now
        CustomInput.press_key(CustomInput.key_map["right"], "right")
        start_time = time.time()
        while time.time() - start_time < 1.5:
            if Looting.check_for_lootv2(gamename):
                CustomInput.release_key(CustomInput.key_map["right"], "right")
                self.loot_everything(gamename)
        CustomInput.release_key(CustomInput.key_map["right"], "right")
        # Then perform one final check
        time.sleep(0.1)
        if Looting.check_for_lootv2(gamename):
            self.loot_everything(gamename)

    def loot_everything(self, gamename):
        player_name = False
        player_name = BotUtils.detect_player_name(gamename)
        if not player_name:
            # print("Didn't detect name")
            return Looting.grab_all_visible_lootv2(gamename)
        else:
            return Looting.grab_all_visible_lootv2(gamename, player_name)

    def skip_to_reward(self, gamename):
        wincap = WindowCapture(gamename)
        pydirectinput.click(
            wincap.window_rect[0]+656, wincap.window_rect[1]+276)

    def repeat_level(self, gamename):
        # Close the shop
        pydirectinput.press('esc')
        time.sleep(0.1)
        pydirectinput.press('esc')
        time.sleep(0.1)
        BotUtils.close_map_and_menu(gamename)
        time.sleep(0.1)
        RHClick.click_explore_again(gamename)
        time.sleep(3)
        # self.summon_momo(gamename)

    def move_to_boss(self):
        time.sleep(0.5)
        CustomInput.press_key(CustomInput.key_map["right"], "right")
        time.sleep(0.3)
        CustomInput.release_key(CustomInput.key_map["right"], "right")
        time.sleep(0.1)
        CustomInput.press_key(CustomInput.key_map["right"], "right")
        CustomInput.press_key(CustomInput.key_map["up"], "up")
        time.sleep(3.4)
        CustomInput.release_key(CustomInput.key_map["right"], "right")
        CustomInput.release_key(CustomInput.key_map["up"], "up")
        # dodge_attacks("right")

    def dodge_attacks(self, key):
        CustomInput.press_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map[key], key)
        time.sleep(0.07)
        CustomInput.press_key(CustomInput.key_map[key], key)
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map[key], key)
        time.sleep(0.8)

    def release_dir_keys(self):
        KEYS = {
            'left': 37,
            'up': 38,
            'right': 39,
            'down': 40
        }
        for key in ["up", "down", "left", "right"]:
            if ctypes.windll.user32.GetKeyState(KEYS[key]) > 2:
                CustomInput.release_key(CustomInput.key_map[key], key)

    def point_angle(self, angle):
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

    def continue_boss_attacks(self):
        for key in ["a", "g", "f", "s", "d"]:
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(0.02)
            CustomInput.release_key(CustomInput.key_map[key], key)
            # time.sleep(0.04)

    def perform_boss_moves(self):
        # print("Got to the perform boss move func")
        # Perform first two skill moves
        CustomInput.press_key(CustomInput.key_map["s"])
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map["s"])
        time.sleep(0.4)
        CustomInput.press_key(CustomInput.key_map["f"])
        time.sleep(0.02)
        CustomInput.release_key(CustomInput.key_map["f"])
        time.sleep(0.4)
        self.continue_boss_attacks()
        # print("Got past the first dodge point continue")
        # Then continue attack and dodge until boss defeated
        while Events.detect_in_dungeon():
            self.continue_boss_attacks()

    def kill_boss(self, gamename):
        # First need to start moving straight to the right
        CustomInput.press_key(CustomInput.key_map["right"], "right")
        # Need to first wait until the dung check returns false
        while Events.detect_in_dungeon():
            time.sleep(0.006)
        # And then release the right key
        CustomInput.release_key(CustomInput.key_map["right"], "right")
        time.sleep(0.1)
        # Then press escape
        pydirectinput.press('esc')
        # Then move to the correct distance from the boss
        self.move_to_boss()
        # And then perform the preset initial moves
        self.perform_boss_moves()


if __name__ == "__main__":
    time.sleep(2)
    map = Map10_MS30()
    # print(map.grab_off_cooldown())
    map.start(True)
