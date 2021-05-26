import os
import cv2 as cv
import numpy as np
from hsvfilter import HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class BotUtils():
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

    def filter_blackwhite_invert(filter, existing_image):
        hsv = cv.cvtColor(existing_image, cv.COLOR_BGR2HSV)
        hsv_filter = filter
        # add/subtract saturation and value
        h, s, v = cv.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
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
