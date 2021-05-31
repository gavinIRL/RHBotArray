# This file will automatically run through map 10
import time
import os
import numpy as np
import cv2
from hsvfilter import HsvFilter
from windowcapture import WindowCapture
from vision import Vision
import pydirectinput
from custom_input import CustomInput
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Map10_MS30():
    def __init__(self, maxloops=1) -> None:
        self.rooms = self.load_map_rooms()
        self.maxloops = maxloops
        self.speed = 22.5
        self.map_rect = [561, 282, 1111, 666]
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.key_dict = CustomInput.grab_key_dict()

    def start(self):
        while self.maxloops > 0:
            self.mainloop()
            self.maxloops -= 1

    def test(self):
        time.sleep(2)
        room = self.rooms[0]
        self.move_to(int(room[1]), int(room[2]))
        self.roomclear_skill()
        time.sleep(0.3)
        start_time = time.time()
        while not self.sect_clear_detected():
            self.continue_clear()
            if time.time() > start_time + 4:
                break

    def mainloop(self):
        # First assume that have entered the map
        # Therefore will wait for 3 seconds
        time.sleep(3)
        for room in self.rooms:
            # Need to decide if boss room or not
            if room[0] == "b":
                # Now move to the correct point in room
                self.move_to(int(room[1]), int(room[2]), 45)
                # Perform the first bossfight skill combo
                self.boss_combo_1()
                # Then move to the second point in the room
                self.move_to(int(room[3]), int(room[4]), 45)
                # Perform the second bossfight combo
                self.boss_combo_2()
                # Until boss is defeated continue to attack
                while not self.boss_defeat_detected():
                    self.boss_combo_1()
                    self.roomclear_skill()
                # After boss is defeated need to move to the main loot drop point
                self.move_to(int(room[5]), int(room[6]), 45)
            # Else if need to break a box straight away
            elif "x" in room:
                # Now move to the boxes
                self.move_to(int(room[1]), int(room[2]))
                # And then perform x attack twice
                self.x_attack_twice()
                # Now move to the correct point in room
                self.move_to(int(room[3]), int(room[4]))
                # And perform the roomclear skill
                self.roomclear_skill()
                # Until sectclear detected continue to perform homing skills
                while not self.sect_clear_detected():
                    self.continue_clear()
            # Handling for all other rooms
            else:
                # Now move to the correct point in room
                self.move_to(int(room[1]), int(room[2]))
                # And perform the roomclear skill
                self.roomclear_skill()
                # Until sectclear detected continue to perform homing skills
                while not self.sect_clear_detected():
                    self.continue_clear()
            # And then check for loot afterwards
            self.ident_farloot()
        # Once boss is defeated need to go through the event check
        # And clear the event if necessary
        if not self.detect_endlevel_event():
            # Try to move towards and detect loot
            self.move_to(int(self.rooms[-1][5]), int(self.rooms[-1][6]), 45)
            self.ident_farloot()
        # Then go through the reward select
        self.select_reward()
        # Check once more for loot
        self.move_to(int(self.rooms[-1][5]), int(self.rooms[-1][6]), 45)
        self.ident_farloot()
        # Then perform the sell and repair
        self.sell_and_repair()
        # And if there are more loops to do then go again
        if self.maxloops > 0:
            self.repeat_level()

    def move_to(self, x, y, angle=90):
        if not self.detect_bigmap_open():
            self.try_toggle_map()
        player_pos = self.grab_player_pos()
        self.clear_all()
        print(player_pos)
        relx = player_pos[0] - int(x)
        rely = int(y) - player_pos[1]
        if abs(rely) > 150 or rely == 0:
            self.resolve_dir_v2(rely, "y")
        if abs(relx) > 150 or relx == 0:
            self.resolve_dir_v2(relx, "x")

    def resolve_dir_v2(self, value, dir):
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
        print("val={}".format(value))
        time_reqd = abs(value/self.speed)
        print(self.key_dict[key])
        CustomInput.press_key(self.key_dict[key], key)
        time.sleep(time_reqd-0.003)
        CustomInput.release_key(self.key_dict[key], key)

    def try_toggle_map(self):
        pydirectinput.keyDown("m")
        time.sleep(0.05)
        pydirectinput.keyUp("m")
        time.sleep(0.08)

    def detect_bigmap_open(self):
        wincap = WindowCapture(self.gamename, custom_rect=[819, 263, 855, 264])
        image = wincap.get_screenshot()
        # cv2.imwrite("testy.jpg", image)
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-2]]
        if a+b+c < 30:
            if d+e+f > 700:
                # print("Working")
                return True
        return False

    def grab_player_pos(self):
        if not self.map_rect:
            wincap = WindowCapture(self.gamename)
        else:
            wincap = WindowCapture(self.gamename, self.map_rect)
        filter = HsvFilter(34, 160, 122, 50, 255, 255, 0, 0, 0, 0)
        image = wincap.get_screenshot()
        save_image = self.filter_blackwhite_invert(filter, image)
        # cv2.imwrite("testy3.jpg", save_image)
        vision_limestone = Vision('plyr.jpg')
        rectangles = vision_limestone.find(
            save_image, threshold=0.31, epsilon=0.5)
        points = vision_limestone.get_click_points(rectangles)
        x, y = points[0]
        if not self.map_rect:
            return x, y
        else:
            x += self.map_rect[0]
            y += self.map_rect[1]
            return x, y

    def roomclear_skill(self):
        hex = self.key_dict["h"]
        CustomInput.press_key(hex)
        time.sleep(0.01)
        CustomInput.release_key(hex)

    def continue_clear(self):
        hex = self.key_dict["a"]
        CustomInput.press_key(hex)
        time.sleep(0.01)
        CustomInput.release_key(hex)
        time.sleep(0.1)
        hex = self.key_dict["f"]
        CustomInput.press_key(hex)
        time.sleep(0.01)
        CustomInput.release_key(hex)
        time.sleep(0.1)
        hex = self.key_dict["g"]
        CustomInput.press_key(hex)
        time.sleep(0.01)
        CustomInput.release_key(hex)

    def ident_farloot(self):
        pass

    def ident_nearloot(self):
        pass

    def boss_combo_1(self):
        pass

    def boss_combo_2(self):
        pass

    def x_attack_twice(self):
        pass

    def sect_clear_detected(self):
        wincap = WindowCapture(self.gamename, custom_rect=[
            464+156, 640, 464+261, 641])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a+b+c > 700 and d+e+f > 700:
            return True
        else:
            return False

    def boss_defeat_detected(self):
        return True

    def load_map_rooms(self):
        # Format to be as follows:
        # roomnum, moveposx, moveposy,
        # exitposx,exitposy
        # exception is bossfight which has move2 vs exit
        # and additional lootx, looty for bossloot
        return_list = []
        filepath = os.path.dirname(
            os.path.abspath(__file__)) + "/levels/map10.txt"
        with open(filepath) as file:
            lines = file.readlines()
        for line in lines:
            return_list.append(line.split(","))
        return return_list

    def detect_endlevel_event(self):
        pass

    def select_reward(self):
        pass

    def sell_and_repair(self):
        pass

    def repeat_level(self):
        pass

    def filter_blackwhite_invert(self, filter, existing_image):
        hsv = cv2.cvtColor(existing_image, cv2.COLOR_BGR2HSV)
        hsv_filter = filter
        # add/subtract saturation and value
        h, s, v = cv2.split(hsv)
        s = self.shift_channel(s, hsv_filter.sAdd)
        s = self.shift_channel(s, -hsv_filter.sSub)
        v = self.shift_channel(v, hsv_filter.vAdd)
        v = self.shift_channel(v, -hsv_filter.vSub)
        hsv = cv2.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR
        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
        # now change it to greyscale
        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # now change it to black and white
        (thresh, blackAndWhiteImage) = cv2.threshold(
            grayImage, 67, 255, cv2.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        inverted = cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)
        return inverted

    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c

    def clear_all(self):
        if self.detect_menu_open():
            self.close_esc_menu()
        elif self.detect_bigmap_open():
            self.close_map()

    def detect_menu_open(self):
        wincap = WindowCapture(self.gamename, custom_rect=[595, 278, 621, 479])
        image = wincap.get_screenshot()
        # cv2.imwrite("testy.jpg", image)
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        # print("Sum abc:{}, def:{}".format(a+b+c, d+e+f))
        if a+b+c > 700:
            if d+e+f > 700:
                return True
        return False

    def close_map(self):
        pydirectinput.click(
            int(self.scaling*859+self.game_wincap.window_rect[0]), int(self.scaling*260+self.game_wincap.window_rect[1]))

    def close_esc_menu(self):
        pydirectinput.click(
            int(self.scaling*749+self.game_wincap.window_rect[0]), int(self.scaling*280+self.game_wincap.window_rect[1]))


if __name__ == "__main__":
    map10 = Map10_MS30(maxloops=1)
    map10.test()
