import os
import cv2
import time
import math
import ctypes
import win32ui
import win32gui
import win32con
import numpy as np
import pytesseract
import pydirectinput
from fuzzywuzzy import process
from custom_input import CustomInput
from win32api import GetSystemMetrics
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class HsvFilter:
    def __init__(self, hMin=None, sMin=None, vMin=None, hMax=None, sMax=None, vMax=None,
                 sAdd=None, sSub=None, vAdd=None, vSub=None):
        self.hMin = hMin
        self.sMin = sMin
        self.vMin = vMin
        self.hMax = hMax
        self.sMax = sMax
        self.vMax = vMax
        self.sAdd = sAdd
        self.sSub = sSub
        self.vAdd = vAdd
        self.vSub = vSub


class WindowCapture:
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    def __init__(self, window_name=None, custom_rect=None):
        self.custom_rect = custom_rect
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        # Declare all the class variables
        self.w, self.h, self.cropped_x, self.cropped_y
        self.offset_x, self.offset_y
        self.update_window_position()

    def get_screenshot(self):
        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj,
                   (self.cropped_x, self.cropped_y), win32con.SRCCOPY)
        # convert the raw data into a format opencv can read
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)
        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        # drop the alpha channel
        img = img[..., :3]
        # make image C_CONTIGUOUS
        img = np.ascontiguousarray(img)

        return img

    def update_window_position(self, border=True):
        self.window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = self.window_rect[2] - self.window_rect[0]
        self.h = self.window_rect[3] - self.window_rect[1]
        border_pixels = 8
        titlebar_pixels = 30
        if self.custom_rect is None:
            if border:
                self.w = self.w - (border_pixels * 2)
                self.h = self.h - titlebar_pixels - border_pixels
                self.cropped_x = border_pixels
                self.cropped_y = titlebar_pixels
            else:
                self.cropped_x = 0
                self.cropped_y = 0
        else:
            self.w = self.custom_rect[2] - self.custom_rect[0]
            self.h = self.custom_rect[3] - self.custom_rect[1]
            self.cropped_x = self.custom_rect[0]
            self.cropped_y = self.custom_rect[1]
        self.offset_x = self.window_rect[0] + self.cropped_x
        self.offset_y = self.window_rect[1] + self.cropped_y

    # WARNING: need to call the update_window_position function to prevent errors
    # That would come from moving the window after starting the bot
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)


class BotUtils:
    def try_toggle_map():
        pydirectinput.keyDown("m")
        time.sleep(0.05)
        pydirectinput.keyUp("m")
        time.sleep(0.08)

    def grab_closest(rel_list: list):
        closest_index = False
        smallest_dist = 100000
        for i, pair in enumerate(rel_list):
            x = abs(pair[0])
            y = abs(pair[1])
            hypot = math.hypot(x, y)
            if hypot < smallest_dist:
                smallest_dist = hypot
                closest_index = i
        return closest_index

    def grab_order_closeness(relatives):
        dists = []
        for x, y in relatives:
            dists.append(math.hypot(x, y))
        return sorted(range(len(dists)), key=dists.__getitem__)

    def grab_order_lowest_y(coords):
        y_only = []
        for _, y in coords:
            y_only.append(y)
        return sorted(range(len(y_only)), key=y_only.__getitem__, reverse=True)

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

    def move_to(x, y, angle=90, yfirst=True, speed=22.5):
        if not BotUtils.detect_bigmap_open():
            BotUtils.try_toggle_map()
        player_pos = BotUtils.grab_player_pos()
        start_time = time.time()
        while not player_pos:
            time.sleep(0.05)
            if not BotUtils.detect_bigmap_open():
                BotUtils.try_toggle_map()
            time.sleep(0.05)
            player_pos = BotUtils.grab_player_pos()
            if time.time() - start_time > 5:
                print("Error with finding player")
                os._exit(1)
        BotUtils.close_map_and_menu()
        relx = player_pos[0] - int(x)
        rely = int(y) - player_pos[1]
        while abs(relx) > 100 or abs(rely > 100):
            CustomInput.press_key(CustomInput.key_map["right"], "right")
            CustomInput.release_key(CustomInput.key_map["right"], "right")
            time.sleep(0.02)
            player_pos = BotUtils.grab_player_pos()
            relx = player_pos[0] - int(x)
            rely = int(y) - player_pos[1]

        if not yfirst:
            BotUtils.resolve_dir_v2(relx, "x", speed)
            BotUtils.resolve_dir_v2(rely, "y", speed)
        else:
            BotUtils.resolve_dir_v2(rely, "y", speed)
            BotUtils.resolve_dir_v2(relx, "x", speed)

    def resolve_dir_v2(value, dir, speed):
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
        time_reqd = abs(value/speed)
        if time_reqd > 0.003:
            CustomInput.press_key(CustomInput.key_map[key], key)
            time.sleep(time_reqd-0.003)
            CustomInput.release_key(CustomInput.key_map[key], key)

    def resolve_single_direction(speed, value, dir, PAG=False):
        if not PAG:
            sleep_time = 0.003
        else:
            sleep_time = 0.1
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
        time_reqd = abs(value/speed)
        key_map = CustomInput.grab_key_dict()
        if not PAG:
            CustomInput.press_key(key_map[key], key)
        else:
            pydirectinput.keyDown(key)
        try:
            time.sleep(time_reqd-sleep_time)
        except:
            pass
        if not PAG:
            CustomInput.release_key(key_map[key], key)
        else:
            pydirectinput.keyDown(key)

    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    def grab_hpbar_locations(gamename=False):
        if gamename:
            wincap = WindowCapture(gamename, [100, 135, 1223, 688])
            original_image = wincap.get_screenshot()
        else:
            original_image = cv2.imread(os.path.dirname(
                os.path.abspath(__file__)) + "/testimages/healthbars.jpg")
        filter = HsvFilter(20, 174, 245, 26, 193, 255, 0, 0, 0, 0)
        output_image = BotUtils.filter_blackwhite_invert(
            filter, original_image, True)
        output_image = cv2.blur(output_image, (2, 2))
        _, thresh = cv2.threshold(output_image, 127, 255, 0)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        if len(contours) < 2:
            return False
        contours.pop(0)
        rectangles = []
        for contour in contours:
            (x, y), _ = cv2.minEnclosingCircle(contour)
            rectangles.append([x-10, y, 20, 5])
            rectangles.append([x-10, y, 20, 5])
        rectangles, _ = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=0.8)
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def grab_farloot_locations(gamename=False):
        if gamename:
            wincap = WindowCapture(gamename, [100, 135, 1223, 688])
            original_image = wincap.get_screenshot()
        else:
            original_image = cv2.imread(os.path.dirname(
                os.path.abspath(__file__)) + "/testimages/lootscene.jpg")
        filter = HsvFilter(16, 140, 0, 26, 255, 49, 0, 0, 0, 0)
        output_image = BotUtils.filter_blackwhite_invert(
            filter, original_image, True, 0, 180)
        output_image = cv2.blur(output_image, (3, 2))
        _, thresh = cv2.threshold(output_image, 127, 255, 0)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        if len(contours) < 2:
            return False
        contours.pop(0)
        rectangles = []
        for contour in contours:
            (x, y), _ = cv2.minEnclosingCircle(contour)
            rectangles.append([x-50, y, 100, 5])
            # rectangles.append([x-50, y, 100, 5])
        rectangles, _ = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=0.9)
        if len(rectangles) < 1:
            return False
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def grab_farloot_locationsv2(gamename=False, rect=False, return_image=False):
        if gamename:
            if rect:
                wincap = WindowCapture(gamename, rect)
            else:
                wincap = WindowCapture(gamename, [100, 135, 1223, 688])
            original_image = wincap.get_screenshot()
        else:
            original_image = cv2.imread(os.path.dirname(
                os.path.abspath(__file__)) + "/testimages/lootscene.jpg")
        filter = HsvFilter(15, 180, 0, 20, 255, 63, 0, 0, 0, 0)
        output_image = BotUtils.filter_blackwhite_invert(
            filter, original_image, True, 0, 180)

        output_image = cv2.blur(output_image, (8, 1))
        output_image = cv2.blur(output_image, (8, 1))
        output_image = cv2.blur(output_image, (8, 1))

        cv2.imwrite("testytest.jpg", output_image)
        _, thresh = cv2.threshold(output_image, 127, 255, 0)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        if len(contours) < 2:
            return False
        contours.pop(0)
        rectangles = []
        for contour in contours:
            (x, y), _ = cv2.minEnclosingCircle(contour)
            rectangles.append([x-50, y, 100, 5])
            rectangles.append([x-50, y, 100, 5])
        rectangles, _ = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=0.9)
        if len(rectangles) < 1:
            return False
        points = []
        for (x, y, w, h) in rectangles:
            # Account for the rect
            if rect:
                # Account for the rect
                x += rect[0]
                y += rect[1]
            else:
                x += 100
                y += 135
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        if return_image:
            return points, original_image, rect[0], rect[1]
        return points

    def grab_character_location(player_name, gamename=False):
        player_chars = "".join(set(player_name))
        if gamename:
            wincap = WindowCapture(gamename, [200, 235, 1123, 688])
            original_image = wincap.get_screenshot()
        else:
            original_image = cv2.imread(os.path.dirname(
                os.path.abspath(__file__)) + "/testimages/test_sensitive.jpg")
        filter = HsvFilter(0, 0, 119, 179, 49, 255, 0, 0, 0, 0)
        output_image = BotUtils.filter_blackwhite_invert(
            filter, original_image, return_gray=True)
        rgb = cv2.cvtColor(output_image, cv2.COLOR_GRAY2RGB)
        tess_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=' + player_chars
        results = pytesseract.image_to_data(
            rgb, output_type=pytesseract.Output.DICT, lang='eng', config=tess_config)
        try:
            best_match, _ = process.extractOne(
                player_name, results["text"], score_cutoff=0.8)
            i = results["text"].index(best_match)
            x = int(results["left"][i] + (results["width"][i]/2))
            y = int(results["top"][i] + (results["height"][i]/2))
            # Account for the rect
            x += 200
            y += 235
            return x, y
        except:
            return False, False

    def shift_channel(c, amount):
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

    def filter_blackwhite_invert(filter: HsvFilter, existing_image, return_gray=False, threshold=67, max=255):
        hsv = cv2.cvtColor(existing_image, cv2.COLOR_BGR2HSV)
        hsv_filter = filter
        # add/subtract saturation and value
        h, s, v = cv2.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
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
            grayImage, threshold, max, cv2.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        if return_gray:
            return inverted
        inverted = cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)
        return inverted

    def detect_level_name(gamename):
        wincap = WindowCapture(gamename, [1121, 31, 1248, 44])
        existing_image = wincap.get_screenshot()
        filter = HsvFilter(0, 0, 0, 169, 34, 255, 0, 0, 0, 0)
        save_image = BotUtils.apply_hsv_filter(existing_image, filter)
        gray_image = cv2.cvtColor(save_image, cv2.COLOR_BGR2GRAY)
        (thresh, blackAndWhiteImage) = cv2.threshold(
            gray_image, 129, 255, cv2.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        save_image = cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)
        rgb = cv2.cvtColor(save_image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        return result

    def apply_hsv_filter(original_image, hsv_filter: HsvFilter):
        # convert image to HSV
        hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        # add/subtract saturation and value
        h, s, v = cv2.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
        hsv = cv2.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR for imshow() to display it properly
        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)

        return img

    def detect_bigmap_open(gamename):
        wincap = WindowCapture(gamename, custom_rect=[819, 263, 855, 264])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-2]]
        if a+b+c < 30:
            if d+e+f > 700:
                return True
        return False

    def detect_sect_clear(gamename):
        wincap = WindowCapture(gamename, custom_rect=[
            464+156, 640, 464+261, 641])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a+b+c > 700:
            if d+e+f > 700:
                return True
        return False

    def detect_boss_healthbar(gamename):
        wincap = WindowCapture(gamename, custom_rect=[
                               415+97, 105+533, 415+98, 105+534])
        image = wincap.get_screenshot()
        # bgr
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        # print("abc={},{},{}".format(a, b, c))
        if c+f > 440:
            if a+b+d+e < 80:
                return True
        return False

    def detect_xprompt(gamename):
        wincap = WindowCapture(gamename, custom_rect=[
            1137, 694, 1163, 695])
        image = wincap.get_screenshot()
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        if a+b+d+e > 960 and c+f == 140:
            return True
        else:
            return False

    def grab_player_pos(gamename, map_rect=None):
        if not map_rect:
            wincap = WindowCapture(gamename)
        else:
            wincap = WindowCapture(gamename, map_rect)
        filter = HsvFilter(34, 160, 122, 50, 255, 255, 0, 0, 0, 0)
        image = wincap.get_screenshot()
        save_image = BotUtils.filter_blackwhite_invert(filter, image)
        vision = Vision('plyr.jpg')
        rectangles = vision.find(
            save_image, threshold=0.31, epsilon=0.5)
        points = vision.get_click_points(rectangles)
        x, y = points[0]
        if not map_rect:
            return x, y
        else:
            x += wincap.window_rect[0]
            y += wincap.window_rect[1]
            return x, y

    def grab_level_rects():
        rects = {}
        # Load the translation from name to num
        with open("lvl_name_num.txt") as f:
            num_names = f.readlines()
        for i, entry in enumerate(num_names):
            num_names[i] = entry.split("-")
        # Load the num to rect catalogue
        with open("catalogue.txt") as f:
            nums_rects = f.readlines()
        for i, entry in enumerate(nums_rects):
            nums_rects[i] = entry.split("-")
        # Then add each rect to the rects dict against name
        for number, name in num_names:
            for num, area, rect in nums_rects:
                if area == "FM" and num == number:
                    rects[name.rstrip().replace(" ", "")] = rect.rstrip()
                    if "1" in name:
                        rects[name.rstrip().replace(
                            " ", "").replace("1", "L")] = rect.rstrip()
                    if "ri" in name:
                        rects[name.rstrip().replace(
                            " ", "").replace("ri", "n").replace("1", "L")] = rect.rstrip()
                    break
        return rects

    def detect_menu_open(gamename):
        wincap = WindowCapture(gamename, custom_rect=[595, 278, 621, 281])
        image = wincap.get_screenshot()
        # cv2.imwrite("testy.jpg", image)
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-1]]
        # print("Sum abc:{}, def:{}".format(a+b+c, d+e+f))
        if a+b+c > 700:
            if d+e+f > 700:
                return True
        return False

    def convert_list_to_rel(item_list, playerx, playery, yoffset=0):
        return_list = []
        for item in item_list:
            relx = playerx - item[0]
            rely = item[1] - playery - yoffset
            return_list.append((relx, rely))
        return return_list

    def close_map_and_menu(gamename):
        scaling = BotUtils.get_monitor_scaling()
        wincap = WindowCapture(gamename)
        if BotUtils.detect_menu_open(gamename):
            BotUtils.close_esc_menu(scaling, wincap)
        elif BotUtils.detect_bigmap_open(gamename):
            BotUtils.close_map(scaling, wincap)

    def close_map(scaling, game_wincap):
        pydirectinput.click(
            int(scaling*859+game_wincap.window_rect[0]), int(scaling*260+game_wincap.window_rect[1]))

    def close_esc_menu(scaling, game_wincap):
        pydirectinput.click(
            int(scaling*749+game_wincap.window_rect[0]), int(scaling*280+game_wincap.window_rect[1]))

    def get_monitor_scaling():
        user32 = ctypes.windll.user32
        w_orig = GetSystemMetrics(0)
        user32.SetProcessDPIAware()
        [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        return float(("{:.3f}".format(w/w_orig)))

    def find_and_verify_loot(gamename):
        # This will be a lightweight check for any positive loot ident
        # Meant to be used when moving and normal looting has ceased
        # i.e. opportunistic looting
        loot_list, image, xoff, yoff = BotUtils.grab_farloot_locationsv2(
            gamename, return_image=True)
        if not loot_list:
            return False

        confirmed = False
        for _, coords in enumerate(loot_list):
            x, y = coords
            x -= xoff
            y -= yoff
            rgb = image[y-22:y+22, x-75:x+75]
            filter = HsvFilter(0, 0, 131, 151, 255, 255, 0, 0, 0, 0)
            rgb = BotUtils.apply_hsv_filter(rgb, filter)
            tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            result = pytesseract.image_to_string(
                rgb, lang='eng', config=tess_config)[:-2]
            if len(result) > 3:
                return True
        if not confirmed:
            return False

    def try_find_and_grab_loot(gamename, player_name, loot_nearest=False, loot_lowest=True):
        # First need to close anything that might be in the way
        BotUtils.close_map_and_menu(gamename)
        # Then grab loot locations
        loot_list = BotUtils.grab_farloot_locationsv2(gamename)
        if not loot_list:
            return "noloot"

        playerx, playery = BotUtils.grab_character_location(
            player_name, gamename)
        # If didn't find player then try once more
        if not playerx:
            playerx, playery = BotUtils.grab_character_location(
                player_name, gamename)
            if not playerx:
                return "noplayer"

        # if want to always loot the nearest first despite the cpu hit
        if loot_nearest:
            # Then convert lootlist to rel_pos list
            relatives = BotUtils.convert_list_to_rel(
                loot_list, playerx, playery, 275)
            # Grab the indexes in ascending order of closesness
            order = BotUtils.grab_order_closeness(relatives)
            # Then reorder the lootlist to match
            loot_list = [x for _, x in sorted(zip(order, loot_list))]
        # Otherwise if want to loot from bottom of screen to top
        # Typically better as see all loot then in y direction
        # but potentially miss loot in x direction
        elif loot_lowest:
            # Grab the indexes in ascending order of distance from
            # bottom of the screen
            order = BotUtils.grab_order_lowest_y(loot_list)
            # Then reorder the lootlist to match
            loot_list = [x for _, x in sorted(zip(order, loot_list))]

        confirmed = False
        for index, coords in enumerate(loot_list):
            x, y = coords
            wincap = WindowCapture(gamename, [x-75, y-22, x+75, y+22])
            rgb = wincap.get_screenshot()
            filter = HsvFilter(0, 0, 131, 151, 255, 255, 0, 0, 0, 0)
            rgb = BotUtils.apply_hsv_filter(rgb, filter)
            tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            result = pytesseract.image_to_string(
                rgb, lang='eng', config=tess_config)[:-2]
            if len(result) > 3:
                confirmed = loot_list[index]
                break
        if not confirmed:
            return False

        relx = playerx - confirmed[0]
        rely = confirmed[1] - playery - 275
        rect = [confirmed[0]-100, confirmed[1] -
                30, confirmed[0]+100, confirmed[1]+30]
        BotUtils.move_towards(relx, "x")
        loop_time = time.time()
        time_remaining = 0.1
        time.sleep(0.01)
        while time_remaining > 0:
            time.sleep(0.003)
            if BotUtils.detect_xprompt(gamename):
                break
            try:
                newx, newy = BotUtils.grab_farloot_locationsv2(gamename, rect)[
                    0]
                time_taken = time.time() - loop_time
                movementx = confirmed[0] - newx
                speed = movementx/time_taken
                if speed != 0:
                    time_remaining = abs(
                        relx/speed) - time_taken
                rect = [newx-100, newy-30, newx+100, newy+30]
            except:
                try:
                    time.sleep(time_remaining)
                    break
                except:
                    return False
        for key in ["left", "right"]:
            CustomInput.release_key(CustomInput.key_map[key], key)
        BotUtils.move_towards(rely, "y")
        start_time = time.time()
        while not BotUtils.detect_xprompt(gamename):
            time.sleep(0.005)
            # After moving in opposite direction
            if time.time() - start_time > 10:
                # If have moved opposite with no result for equal amount
                if time.time() - start_time > 12:
                    for key in ["up", "down"]:
                        CustomInput.release_key(CustomInput.key_map[key], key)
                    # Return falsepos so that it will ignore this detection
                    return "falsepos"
            # If no result for 3 seconds
            elif time.time() - start_time > 2:
                # Try moving in the opposite direction
                for key in ["up", "down"]:
                    CustomInput.release_key(CustomInput.key_map[key], key)
                BotUtils.move_towards(-1*rely, "y")
                start_time -= 8
        for key in ["up", "down"]:
            CustomInput.release_key(CustomInput.key_map[key], key)
        pydirectinput.press("x")
        return True


class Vision:
    def __init__(self, needle_img_path, method=cv2.TM_CCOEFF_NORMED):
        self.needle_img = cv2.imread(needle_img_path, cv2.IMREAD_UNCHANGED)
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, haystack_img, threshold=0.7, max_results=15, epsilon=0.5):
        result = cv2.matchTemplate(haystack_img, self.needle_img, self.method)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            rectangles.append(rect)
            rectangles.append(rect)
        rectangles, weights = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=epsilon)
        return rectangles

    def get_click_points(self, rectangles):
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def draw_rectangles(self, haystack_img, rectangles):
        # BGR
        line_color = (0, 255, 0)
        line_type = cv2.LINE_4
        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv2.rectangle(haystack_img, top_left, bottom_right,
                          line_color, lineType=line_type)
        return haystack_img

    def draw_crosshairs(self, haystack_img, points):
        # BGR
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS

        for (center_x, center_y) in points:
            cv2.drawMarker(haystack_img, (center_x, center_y),
                           marker_color, marker_type)

        return haystack_img


class DynamicFilter:
    TRACKBAR_WINDOW = "Trackbars"
    # create gui window with controls for adjusting arguments in real-time

    def __init__(self, needle_img_path, method=cv2.TM_CCOEFF_NORMED):
        self.needle_img = cv2.imread(needle_img_path, cv2.IMREAD_UNCHANGED)
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, haystack_img, threshold=0.7, epsilon=0.5):
        result = cv2.matchTemplate(haystack_img, self.needle_img, self.method)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            rectangles.append(rect)
            rectangles.append(rect)
        rectangles, weights = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=epsilon)
        return rectangles

    def get_click_points(self, rectangles):
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def draw_rectangles(self, haystack_img, rectangles):
        # BGR
        line_color = (0, 255, 0)
        line_type = cv2.LINE_4
        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv2.rectangle(haystack_img, top_left, bottom_right,
                          line_color, lineType=line_type)
        return haystack_img

    def draw_crosshairs(self, haystack_img, points):
        # BGR
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS

        for (center_x, center_y) in points:
            cv2.drawMarker(haystack_img, (center_x, center_y),
                           marker_color, marker_type)

        return haystack_img

    def init_control_gui(self):
        cv2.namedWindow(self.TRACKBAR_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        # required callback. we'll be using getTrackbarPos() to do lookups
        # instead of using the callback.
        def nothing(position):
            pass

        # create trackbars for bracketing.
        # OpenCV scale for HSV is H: 0-179, S: 0-255, V: 0-255
        cv2.createTrackbar('HMin', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv2.createTrackbar('SMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('HMax', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv2.createTrackbar('SMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        # Set default value for Max HSV trackbars
        cv2.setTrackbarPos('HMax', self.TRACKBAR_WINDOW, 179)
        cv2.setTrackbarPos('SMax', self.TRACKBAR_WINDOW, 255)
        cv2.setTrackbarPos('VMax', self.TRACKBAR_WINDOW, 255)

        # trackbars for increasing/decreasing saturation and value
        cv2.createTrackbar('SAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('SSub', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VSub', self.TRACKBAR_WINDOW, 0, 255, nothing)

    # returns an HSV filter object based on the control GUI values
    def get_hsv_filter_from_controls(self):
        # Get current positions of all trackbars
        hsv_filter = HsvFilter()
        hsv_filter.hMin = cv2.getTrackbarPos('HMin', self.TRACKBAR_WINDOW)
        hsv_filter.sMin = cv2.getTrackbarPos('SMin', self.TRACKBAR_WINDOW)
        hsv_filter.vMin = cv2.getTrackbarPos('VMin', self.TRACKBAR_WINDOW)
        hsv_filter.hMax = cv2.getTrackbarPos('HMax', self.TRACKBAR_WINDOW)
        hsv_filter.sMax = cv2.getTrackbarPos('SMax', self.TRACKBAR_WINDOW)
        hsv_filter.vMax = cv2.getTrackbarPos('VMax', self.TRACKBAR_WINDOW)
        hsv_filter.sAdd = cv2.getTrackbarPos('SAdd', self.TRACKBAR_WINDOW)
        hsv_filter.sSub = cv2.getTrackbarPos('SSub', self.TRACKBAR_WINDOW)
        hsv_filter.vAdd = cv2.getTrackbarPos('VAdd', self.TRACKBAR_WINDOW)
        hsv_filter.vSub = cv2.getTrackbarPos('VSub', self.TRACKBAR_WINDOW)
        return hsv_filter

    def apply_hsv_filter(self, original_image, hsv_filter=None):
        hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        if not hsv_filter:
            hsv_filter = self.get_hsv_filter_from_controls()

        h, s, v = cv2.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
        hsv = cv2.merge([h, s, v])

        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)
        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
        return img


if __name__ == "__main__":
    with open("gamename.txt") as f:
        gamename = f.readline()
    start = time.time()
    BotUtils.detect_xprompt(gamename)
    print("Time taken: {}s".format(time.time()-start))
