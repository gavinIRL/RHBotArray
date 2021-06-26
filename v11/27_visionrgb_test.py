import cv2
import numpy as np
import time
import os
import math
import ctypes
import logging
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter, Follower
import pydirectinput
import pytesseract
from custom_input import CustomInput
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class RgbFilter:
    def __init__(self, rMin=None, gMin=None, bMin=None, rMax=None, gMax=None, bMax=None):
        self.rMin = rMin
        self.gMin = gMin
        self.bMin = bMin
        self.rMax = rMax
        self.gMax = gMax
        self.bMax = bMax


class VisionRGB:
    TRACKBAR_WINDOW = "Trackbars"

    # create gui window with controls for adjusting arguments in real-time
    def init_control_gui(self):
        cv2.namedWindow(self.TRACKBAR_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.TRACKBAR_WINDOW, 350, 400)

        # required callback. we'll be using getTrackbarPos() to do lookups
        # instead of using the callback.
        def nothing(position):
            pass

        # create trackbars for bracketing.
        # OpenCV scale for HSV is H: 0-179, S: 0-255, V: 0-255
        cv2.createTrackbar('rMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('gMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('bMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('rMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('gMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('bMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        # Set default value for Max HSV trackbars
        cv2.setTrackbarPos('rMax', self.TRACKBAR_WINDOW, 255)
        cv2.setTrackbarPos('gMax', self.TRACKBAR_WINDOW, 255)
        cv2.setTrackbarPos('bMax', self.TRACKBAR_WINDOW, 255)

    # returns an HSV filter object based on the control GUI values
    def get_rgb_filter_from_controls(self):
        # Get current positions of all trackbars
        rgb_filter = RgbFilter()
        rgb_filter.rMin = cv2.getTrackbarPos('rMin', self.TRACKBAR_WINDOW)
        rgb_filter.gMin = cv2.getTrackbarPos('gMin', self.TRACKBAR_WINDOW)
        rgb_filter.bMin = cv2.getTrackbarPos('bMin', self.TRACKBAR_WINDOW)
        rgb_filter.rMax = cv2.getTrackbarPos('rMax', self.TRACKBAR_WINDOW)
        rgb_filter.gMax = cv2.getTrackbarPos('gMax', self.TRACKBAR_WINDOW)
        rgb_filter.bMax = cv2.getTrackbarPos('bMax', self.TRACKBAR_WINDOW)
        return rgb_filter

    def apply_rgb_filter(self, original_image, rgb_filter=None):
        # if we haven't been given a defined filter, use the filter values from the GUI
        if not rgb_filter:
            rgb_filter = self.get_rgb_filter_from_controls()
        # Then apply the filter
        thresh = cv2.inRange(original_image, np.array(
            [rgb_filter.bMin, rgb_filter.gMin, rgb_filter.rMin]), np.array([rgb_filter.bMax, rgb_filter.gMax, rgb_filter.rMax]))
        # return thresh
        combined_mask_inv = 255 - thresh
        # combined_mask_inv = thresh
        combined_mask_rgb = cv2.cvtColor(combined_mask_inv, cv2.COLOR_GRAY2BGR)
        return cv2.max(original_image, combined_mask_rgb)


# Now the live filter stuff
wincap = WindowCapture(custom_rect=[200, 150, 1400, 1200])

# initialize the Vision class
vision_limestone = VisionRGB()
vision_limestone.init_control_gui()

while(True):

    # get an updated image of the game
    screenshot = wincap.get_screenshot()
    # pre-process the image
    output_image = vision_limestone.apply_rgb_filter(screenshot)
    # display the processed image
    cv2.imshow('Matches', output_image)

    # debug the loop rate
    # print('FPS {}'.format(1 / (time() - loop_time)))
    # loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break

print('Done.')
