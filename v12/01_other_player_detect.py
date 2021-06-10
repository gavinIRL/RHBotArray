from rhba_utils import BotUtils, WindowCapture, Vision, HsvFilter
import os
import cv2
import time
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class OtherPlayerDetect():
    def __init__(self) -> None:
        with open("gamename.txt") as f:
            gamename = f.readline()

        # The next block of code is setup for detecting the other player
        self.othr_plyr_filter = HsvFilter(
            16, 172, 194, 32, 255, 255, 0, 0, 70, 37)
        self.othr_plyr_wincap = WindowCapture(gamename, [1100, 50, 1260, 210])
        self.othr_plyr_vision = Vision("otherplayerinvert.jpg")

    def find_other_player_old(self):
        image = self.othr_plyr_wincap.get_screenshot()
        filter = HsvFilter(24, 194, 205, 31, 255, 255, 0, 0, 0, 0)
        image = cv2.blur(image, (4, 4))
        image = BotUtils.filter_blackwhite_invert(filter, image)
        # do object detection, this time grab the points
        rectangles = self.othr_plyr_vision.find(
            image, threshold=0.61, epsilon=0.5)
        points = self.othr_plyr_vision.get_click_points(rectangles)
        if len(points) >= 1:
            relx = points[0][0] - 0
            rely = 0 - points[0][1]
            return relx, rely
        return False

    def find_other_player_new(self):
        image = self.othr_plyr_wincap.get_screenshot()
        filter = HsvFilter(24, 194, 205, 31, 255, 255, 0, 0, 0, 0)
        image = cv2.blur(image, (4, 4))
        image = BotUtils.filter_blackwhite_invert(filter, image)
        print(np.where(np.all(image == [0, 0, 0], axis=2)))
        # print(image[0][0])
        # cv2.imwrite("testy.jpg", image)

    def filter_invert_save(self):
        image = cv2.imread("otherplayer.jpg")
        filter = HsvFilter(24, 194, 205, 31, 255, 255, 0, 0, 0, 0)
        image = cv2.blur(image, (4, 4))
        image = BotUtils.filter_blackwhite_invert(filter, image)
        cv2.imwrite("otherplayerinvert.jpg", image)


if __name__ == "__main__":
    opd = OtherPlayerDetect()
    start = time.time()
    count = 0
    nodetect = 0
    while count < 1000:
        count += 1
        coords = opd.find_other_player_old()
        if not coords:
            nodetect += 1
    # opd.find_other_player_new()
    # opd.filter_invert_save()
    average = (time.time()-start)/count
    print("Time taken: {}s".format(average))
    print(nodetect)
