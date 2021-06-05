from rhba_utils import BotUtils, WindowCapture
import pydirectinput
import time
import os
import cv2
import random
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def choose_reward(gamename):
    wincap = WindowCapture(gamename)
    posx = wincap.window_rect[0]
    posx += (460+(180*random.randint(0, 2)))
    posy = wincap.window_rect[1]
    posy += (200+(132*random.randint(0, 3)))
    pydirectinput.moveTo(int(posx), int(posy))
    # pydirectinput.click(int(posx), int(posy))


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


time.sleep(1)
with open("gamename.txt") as f:
    gamename = f.readline()
detect_reward_choice(gamename)
