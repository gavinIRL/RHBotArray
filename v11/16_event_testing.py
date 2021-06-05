from rhba_utils import BotUtils, WindowCapture, HsvFilter
import pydirectinput
import time
import os
import cv2
import random
import pytesseract
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def choose_reward(gamename):
    wincap = WindowCapture(gamename)
    posx = wincap.window_rect[0] + (460+(180*random.randint(0, 2)))
    posy = wincap.window_rect[1] + (200+(132*random.randint(0, 3)))
    pydirectinput.click(int(posx), int(posy))
    # Now accept the reward
    pydirectinput.click(wincap.window_rect[0]+750, wincap.window_rect[1]+720)


def detect_reward_choice(gamename):
    wincap = WindowCapture(gamename, [503, 90, 535, 92])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    if a + d > 400:
        if b + e > 500:
            if c + f < 105:
                return True
    return False

# To do, read the blue writing


def detect_move_reward_screen(gamename):
    wincap = WindowCapture(gamename, [581, 270, 593, 272])
    image = wincap.get_screenshot()
    # cv2.imwrite("testytest.jpg", image)
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    if a + d > 360 and a + d < 400:
        if b + e > 360 and b + e < 400:
            if c + f < 10:
                return True
    return False

# To do, read the green writing


def detect_endlevel_chest(gamename):
    wincap = WindowCapture(gamename, [454, 250, 525, 252])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    # cv2.imwrite("testytest2.jpg", image)
    if a + d < 50:
        if b + e > 480:
            if c + f > 290 and c+f < 320:
                return True
    return False


def detect_endlevel_bonus_area(gamename):
    wincap = WindowCapture(gamename, [503, 487, 514, 589])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    # cv2.imwrite("testycont.jpg", image)
    if a + d > 400:
        if b + e > 400:
            if c + f > 400:
                return True
    return False


def detect_in_dungeon(gamename):
    wincap = WindowCapture(gamename, [1090, 331, 1092, 353])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[-1][0]]
    # print("abc:{},{},{}, def:{},{},{}".format(a, b, c, d, e, f))
    # cv2.imwrite("testycont.jpg", image)
    if d < 20:
        if a + b + e > 400 and a+b+e < 500:
            if c + f > 480:
                return True
    return False


def detect_go(gamename):
    wincap = WindowCapture(gamename, [623, 247, 628, 249])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    if a < 30:
        if b > 240:
            if c > 140:
                return True
    return False


def detect_one_card(gamename):
    # Cards only show up once one has been picked
    # Therefore need to check against bronze, gold, silver
    wincap = WindowCapture(gamename, [833, 44, 835, 46])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    print("abc:{},{},{}".format(a, b, c))
    # cv2.imwrite("testycont.jpg", image)
    # Bronze
    if a == 27:
        if b == 48:
            if c == 87:
                return True
    # Silver
    if a == 139:
        if b == 139:
            if c == 139:
                return True
    # Gold
    if a == 38:
        if b == 129:
            if c == 160:
                return True
    return False


def detect_yes_no(gamename):
    wincap = WindowCapture(gamename, [516, 426, 541, 441])
    image = wincap.get_screenshot()
    # cv2.imwrite("testycont.jpg", image)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=Yes'
    result = pytesseract.image_to_string(
        rgb, lang='eng', config=tess_config)[:-2]
    if result == "Yes":
        return True
    return False


def click_yes(gamename):
    wincap = WindowCapture(gamename)
    pydirectinput.click(wincap.window_rect[0]+528, wincap.window_rect[1]+433)


def click_no(gamename):
    wincap = WindowCapture(gamename)
    pydirectinput.click(wincap.window_rect[0]+763, wincap.window_rect[1]+433)


def click_choose_map(gamename):
    wincap = WindowCapture(gamename)
    pydirectinput.click(wincap.window_rect[0]+1150, wincap.window_rect[1]+210)


def click_explore_again(gamename):
    wincap = WindowCapture(gamename)
    pydirectinput.click(wincap.window_rect[0]+1150, wincap.window_rect[1]+152)


def click_back_to_town(gamename):
    wincap = WindowCapture(gamename)
    pydirectinput.click(wincap.window_rect[0]+1150, wincap.window_rect[1]+328)


def click_map_gate1(gamename, mapnum):
    wincap = WindowCapture(gamename)
    map_to_clickpoints = {
        5: (728, 521),
        6: (640, 631),
        7: (605, 455),
        8: (542, 350),
        9: (293, 297),
        10: (777, 406),
        11: (140, 370),
        12: (500, 246)
    }
    x, y = map_to_clickpoints[mapnum]
    pydirectinput.click(wincap.window_rect[0]+x, wincap.window_rect[1]+y)


def choose_difficulty_and_enter(gamename, diff):
    wincap = WindowCapture(gamename)
    num_clicks = 0
    if diff == "N":
        num_clicks = 0
    elif diff == "H":
        num_clicks = 1
    elif diff == "VH":
        num_clicks == 2
    elif diff == "BM":
        num_clicks == 3
    for i in range(num_clicks):
        pydirectinput.click(
            wincap.window_rect[0]+618, wincap.window_rect[1]+333)
        time.sleep(0.3)
    # Then click on enter dungeon
    pydirectinput.click(wincap.window_rect[0]+1033, wincap.window_rect[1]+736)


def grab_res_scroll_left(gamename):
    wincap = WindowCapture(gamename, [112, 130, 125, 143])
    image = wincap.get_screenshot()
    filter = HsvFilter(0, 0, 0, 179, 18, 255, 0, 0, 0, 0)
    image = BotUtils.apply_hsv_filter(image, filter)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=1234567890'
    result = pytesseract.image_to_string(
        rgb, lang='eng', config=tess_config)[:-2]
    return int(result)


def read_mission_name(gamename):
    wincap = WindowCapture(gamename, [749, 152, 978, 170])
    image = wincap.get_screenshot()
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    result = pytesseract.image_to_string(
        rgb, lang='eng', config=tess_config)[:-2]
    return result


def go_to_change_character(gamename):
    if not BotUtils.detect_menu_open(gamename):
        pass
    wincap = WindowCapture(gamename)
    pydirectinput.click(wincap.window_rect[0]+640, wincap.window_rect[1]+363)


def exit_game(gamename):
    if not BotUtils.detect_menu_open(gamename):
        pass
    wincap = WindowCapture(gamename)
    pydirectinput.click(wincap.window_rect[0]+640, wincap.window_rect[1]+480)
    time.sleep(0.2)
    pydirectinput.click(wincap.window_rect[0]+640, wincap.window_rect[1]+428)


def choose_character(gamename, charnum):
    wincap = WindowCapture(gamename)
    char_clickpoints = {
        1: (1100, 140),
        2: (1100, 210),
        3: (1100, 280),
        4: (1100, 350),
        5: (1100, 420),
        6: (1100, 490),
        7: (1100, 560),
        8: (1100, 630)
    }
    if charnum > 8:
        pydirectinput.click(
            wincap.window_rect[0]+1165, wincap.window_rect[1]+680)
        x, y = char_clickpoints[charnum-8]
    else:
        pydirectinput.click(
            wincap.window_rect[0]+1035, wincap.window_rect[1]+680)
        x, y = char_clickpoints[charnum]
    time.sleep(0.2)
    pydirectinput.click(wincap.window_rect[0]+x, wincap.window_rect[1]+y)
    time.sleep(0.2)
    pydirectinput.click(wincap.window_rect[0]+640, wincap.window_rect[1]+765)


# time.sleep(1)
with open("gamename.txt") as f:
    gamename = f.readline()
start_time = time.time()


# detect_reward_choice(gamename)
# print(detect_move_reward_screen(gamename))
# print(detect_endlevel_chest(gamename))
# print(detect_endlevel_bonus_area(gamename))
# print(detect_in_dungeon(gamename))
# print(detect_go(gamename))
# print(detect_one_card(gamename))
# print(detect_yes_no(gamename))
# click_yes(gamename)
# print(grab_res_scroll_left(gamename))
# print(read_mission_name(gamename))

print("Time taken: {}s".format(time.time()-start_time))
