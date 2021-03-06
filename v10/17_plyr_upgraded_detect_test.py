import cv2 as cv
from hsvfilter import HsvFilter, grab_object_preset
import numpy as np
import os
from vision import Vision
import time


class BigMapPlayerCheck():

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

    def filter_blackwhite_invert(self, filter, existing_image):
        img = cv.imread(existing_image, cv.IMREAD_UNCHANGED)
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        hsv_filter = filter
        # add/subtract saturation and value
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, hsv_filter.sAdd)
        s = self.shift_channel(s, -hsv_filter.sSub)
        v = self.shift_channel(v, hsv_filter.vAdd)
        v = self.shift_channel(v, -hsv_filter.vSub)
        hsv = cv.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR
        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)
        # now change it to greyscale
        grayImage = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # now change it to black and white
        (thresh, blackAndWhiteImage) = cv.threshold(
            grayImage, 67, 255, cv.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        inverted = cv.cvtColor(inverted, cv.COLOR_GRAY2BGR)
        return inverted
        # cv.imwrite(save_image, inverted)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
start_time = time.time()
filter = HsvFilter(34, 160, 122, 50, 255, 255, 0, 0, 0, 0)
sfi = BigMapPlayerCheck()
existing_image = "CH.jpg"
save_image = sfi.filter_blackwhite_invert(filter, existing_image)
existing_image = cv.imread(existing_image)

vision_limestone = Vision('plyr.jpg')
# save_image = vision_limestone.apply_hsv_filter(save_image)
rectangles = vision_limestone.find(
    save_image, threshold=0.31, epsilon=0.5)
output_image = vision_limestone.draw_rectangles(save_image, rectangles)
cv.imshow('Matches', output_image)
print("Time taken: {}s".format(time.time()-start_time))
cv.waitKey(0)
cv.destroyAllWindows()
