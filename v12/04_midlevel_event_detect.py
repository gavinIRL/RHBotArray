from rhba_utils import BotUtils, WindowCapture, Vision, HsvFilter
import os
import cv2
import time
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def find_midlevel_event(gamename=False, playerx=False, playery=False):
    if not gamename:
        with open("gamename.txt") as f:
            gamename = f.readline()
    if not playerx:
        playerx, playery = BotUtils.grab_player_pos(
            gamename, [1100, 50, 1260, 210], True)
    filter = HsvFilter(76, 247, 170, 100, 255, 255, 0, 0, 0, 0)
    vision = Vision("otherplayerinvert.jpg")
    wincap = WindowCapture(gamename, [1100, 50, 1260, 210])
    image = wincap.get_screenshot()
    image = cv2.blur(image, (4, 4))
    image = BotUtils.filter_blackwhite_invert(filter, image)
    rectangles = vision.find(
        image, threshold=0.61, epsilon=0.5)
    points = vision.get_click_points(rectangles)
    if len(points) >= 1:
        relx = points[0][0] - playerx
        rely = playery - points[0][1]
        return relx, rely
    return False, False
