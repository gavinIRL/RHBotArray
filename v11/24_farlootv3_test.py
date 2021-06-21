import cv2
import time
import os
import numpy as np
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def grab_lootposv3_right():
    with open("gamename.txt") as f:
        gamename = f.readline()
    vision = Vision("lootside2.jpg")
    rect = [5, 80, 1273, 776]
    wincap = WindowCapture(gamename, rect)
    screenshot = wincap.get_screenshot()
    original_image = screenshot
    rectangles = vision.find(
        original_image, threshold=0.81, epsilon=0.5)
    if len(rectangles) < 1:
        return False
    points = []
    for (x, y, w, h) in rectangles:
        x += rect[0]
        y += rect[1]
        center_x = x + int(w/2)
        center_y = y + int(h/2)
        points.append((center_x, center_y))
    return points


def grab_lootposv3_right():
    with open("gamename.txt") as f:
        gamename = f.readline()
    vision = Vision("lootside.jpg")
    rect = [5, 80, 1273, 776]
    wincap = WindowCapture(gamename, rect)
    screenshot = wincap.get_screenshot()
    original_image = screenshot
    rectangles = vision.find(
        original_image, threshold=0.81, epsilon=0.5)
    if len(rectangles) < 1:
        return False
    points = []
    for (x, y, w, h) in rectangles:
        x += rect[0]
        y += rect[1]
        center_x = x + int(w/2)
        center_y = y + int(h/2)
        points.append((center_x, center_y))
    return points
