# This file will automatically run through map 10
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
        enemy_custom_rect = [1100, 50, 1260, 210]
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

    def start(self):
        # Using placeholder individual methods for now
        self.perform_room1()
        for i in range(4):
            self.perform_room_after_first(i+1)

    def perform_room1(self):
        time.sleep(2)
        room = self.rooms[0]
        BotUtils.move_diagonal(int(room[1]), int(room[2]), self.speed)
        time.sleep(0.4)
        self.roomclear_skill()
        time.sleep(0.6)
        start_time = time.time()
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
                result = self.move_diagonal_sectclrdet(
                    points[0], points[1], self.speed*4, self.gamename)
                if result:
                    BotUtils.stop_movement(self.gamename)
                    break
                move_cd = time.time()
            else:
                self.continue_clear()
                BotUtils.stop_movement()
        time.sleep(0.3)

    def perform_room_after_first(self, num):
        room = self.rooms[num-1]
        print("{},{}".format(int(room[1]), int(room[2])))
        print("Just about to move to next roomstart, room {}".format(num))
        BotUtils.move_diagonal(int(room[3]), int(room[4]), self.speed)
        print("Finished moving to next roomstart, room {}".format(num))
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
        print("Preparing to move to clear position, room {}".format(num))
        BotUtils.move_diagonal(int(room[1]), int(room[2]), self.speed)
        time.sleep(0.6)
        self.roomclear_skill()
        time.sleep(0.6)
        start_time = time.time()
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
                result = self.move_diagonal_sectclrdet(
                    points[0], points[1], self.speed*4, self.gamename)
                if result:
                    BotUtils.stop_movement(self.gamename)
                    break
                move_cd = time.time()
            else:
                self.continue_clear()
                BotUtils.stop_movement()
        time.sleep(0.5)
        BotUtils.stop_movement()
        print("Finished combat in room {}".format(num))

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
        for key in available:
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(0.015)
            CustomInput.release_key(CustomInput.key_map[key], key)

    def aim_at_enemies(self):
        points = self.grab_enemy_points()
        if points:
            # print("Enemy detected at {}".format(points[0]))
            if points[0][0] > 80:
                CustomInput.press_key(CustomInput.key_map["left"], "left")
            if points[0][0] < 80:
                CustomInput.press_key(CustomInput.key_map["right"], "right")
            if points[0][1] > 80:
                CustomInput.press_key(CustomInput.key_map["up"], "up")
            if points[0][1] < 80:
                CustomInput.press_key(CustomInput.key_map["down"], "down")
            time.sleep(0.005)
            BotUtils.stop_movement()

    def find_nearest_enemy(self):
        points = self.grab_enemy_points()[0]
        return [points[0] - 80, 80-points[1]]

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
        if a != 56 and "a" in skill_list:
            available.append("a")
        if b != 11 and "s" in skill_list:
            available.append("s")
        if c != 44 and "d" in skill_list:
            available.append("d")
        if d != 245 and "f" in skill_list:
            available.append("f")
        if e != 231 and "g" in skill_list:
            available.append("g")
        if f != 142 and "h" in skill_list:
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
            return self.enemy_minimap_vision.get_click_points(
                enemy_rectangles)
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


if __name__ == "__main__":
    time.sleep(2)
    map = Map10_MS30()
    map.start()
