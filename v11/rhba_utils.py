import os
import cv2
import numpy as np
import pytesseract
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
            grayImage, 67, 255, cv2.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        inverted = cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)
        return inverted

    def detect_level_name(self):
        wincap = WindowCapture(self.gamename, [1121, 31, 1248, 44])
        existing_image = wincap.get_screenshot()
        filter = HsvFilter(0, 0, 0, 169, 34, 255, 0, 0, 0, 0)
        # cv2.imwrite("testy2.jpg", existing_image)
        save_image = BotUtils.apply_hsv_filter(existing_image, filter)
        # cv2.imwrite("testy3.jpg", save_image)
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

    def apply_hsv_filter(original_image, hsv_filter=None):
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
