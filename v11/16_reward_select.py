from rhba_utils import BotUtils, WindowCapture
import pydirectinput
import time
import os
import cv2
import random
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def choose_reward(gamename):
    wincap = WindowCapture(gamename)
    posx = wincap.window_rect[0] + (460+(180*random.randint(0, 2)))
    posy = wincap.window_rect[1] + (200+(132*random.randint(0, 3)))
    pydirectinput.click(int(posx), int(posy))
    # Now accept the reward
    pydirectinput.click(wincap.window_rect[0]+750, wincap.window_rect[0]+720)


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
    cv2.imwrite("testytest.jpg", image)
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    if a + d > 360 and a + d < 400:
        if b + e > 360 and b + e < 400:
            if c + f < 10:
                return True
    return False

# To do, read the green writing


def detect_endlevel_chest(gamename):
    wincap = WindowCapture(gamename, [454, 250, 526, 252])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    cv2.imwrite("testytest2.jpg", image)
    if a + d < 50:
        if b + e > 480:
            if c + f > 290 and c+f < 320:
                return True
    return False


def detect_endlevel_bonus_area(gamename):
    wincap = WindowCapture(gamename, [502, 487, 512, 489])
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    cv2.imwrite("testycont.jpg", image)
    if a + d > 400 and a + d < 440:
        if b + e > 400 and b + e < 440:
            if c + f > 400 and c+f < 440:
                return True
    return False


# time.sleep(1)
with open("gamename.txt") as f:
    gamename = f.readline()
# detect_reward_choice(gamename)
print(detect_move_reward_screen(gamename))
print(detect_endlevel_chest(gamename))
print(detect_endlevel_bonus_area(gamename))
