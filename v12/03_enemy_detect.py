from rhba_utils import BotUtils, WindowCapture, Vision, HsvFilter
import os
import cv2
import time
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class EnemyDetect():
    def __init__(self) -> None:
        pass

    def find_enemy(self, gamename, all=False):
        othr_plyr_vision = Vision("otherplayerinvert.jpg")
        othr_plyr_wincap = WindowCapture(gamename, [1100, 50, 1260, 210])
        image = othr_plyr_wincap.get_screenshot()
        filter = HsvFilter(0, 198, 141, 8, 255, 255, 0, 0, 0, 0)
        image = cv2.blur(image, (4, 4))
        cv2.imwrite("testy.jpg", image)
        image = BotUtils.filter_blackwhite_invert(filter, image)
        cv2.imwrite("testytest.jpg", image)
        rectangles = othr_plyr_vision.find(
            image, threshold=0.41, epsilon=0.5)
        points = othr_plyr_vision.get_click_points(rectangles)
        if len(points) >= 1:
            if not all:
                relx = points[0][0] - 0
                rely = 0 - points[0][1]
                return relx, rely
            else:
                return points
        return False


with open("gamename.txt") as f:
    gamename = f.readline()
time.sleep(2)
ed = EnemyDetect()
print(ed.find_enemy(gamename))
