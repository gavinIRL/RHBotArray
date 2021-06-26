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
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    def __init__(self, needle_img_path, method=cv2.TM_CCOEFF_NORMED) -> None:
        self.needle_img = cv2.imread(needle_img_path, cv2.IMREAD_UNCHANGED)
        # Save the dimensions of the needle image
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, haystack_img, threshold=0.7, max_results=15, epsilon=0.5):
        # run the OpenCV algorithm
        result = cv2.matchTemplate(haystack_img, self.needle_img, self.method)
        # Grab results above threshold
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        # if we found no results
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)
        # First we need to create the list of [x, y, w, h] rectangles
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)
        # Apply group rectangles.
        rectangles, _ = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=epsilon)
        if len(rectangles) > max_results:
            rectangles = rectangles[:max_results]
        return rectangles

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

    def get_click_points(self, rectangles):
        points = []
        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:
            # Determine the center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            # Save the points
            points.append((center_x, center_y))

        return points

    def draw_rectangles(self, haystack_img, rectangles):
        # these colors are actually BGR
        line_color = (0, 255, 0)
        line_type = cv2.LINE_4

        for (x, y, w, h) in rectangles:
            # determine the box positions
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # draw the box
            cv2.rectangle(haystack_img, top_left, bottom_right,
                          line_color, lineType=line_type)

        return haystack_img

    def draw_crosshairs(self, haystack_img, points):
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS

        for (center_x, center_y) in points:
            # draw the center point
            cv2.drawMarker(haystack_img, (center_x, center_y),
                           marker_color, marker_type)

        return haystack_img


def live_filter_chooser():
    # Now the live filter stuff
    # wincap = WindowCapture(custom_rect=[300, 150, 2100, 1100])
    with open("gamename.txt") as f:
        gamename = f.readline()
    wincap = WindowCapture(gamename, [561, 282, 1111, 666])
    # initialize the Vision class
    vision_limestone = VisionRGB("plyr.jpg")
    vision_limestone.init_control_gui()

    while(True):

        # get an updated image of the game
        screenshot = wincap.get_screenshot()
        screenshot = cv2.blur(screenshot, (6, 6))
        # pre-process the image
        output_image = vision_limestone.apply_rgb_filter(screenshot)
        # display the processed image
        cv2.imshow('Matches', output_image)

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break

    print('Done.')


def rgb_find_test():
    with open("gamename.txt") as f:
        gamename = f.readline()
    wincap = WindowCapture(gamename, [561, 282, 1111, 666])
    # initialize the Vision class
    vision_limestone = VisionRGB("plyr.jpg")
    screenshot = wincap.get_screenshot()
    output_image = cv2.blur(screenshot, (6, 6))
    # pre-process the image
    rgb_filter = RgbFilter(79, 129, 0, 140, 206, 65)
    output_image = vision_limestone.apply_rgb_filter(output_image, rgb_filter)
    cv2.imwrite("testytest.jpg", output_image)
    rectangles = vision_limestone.find(
        output_image, threshold=0.61, epsilon=0.5)
    if len(rectangles) < 1:
        print("Didn't find player")
        return False
    points = vision_limestone.get_click_points(rectangles)
    output_image = vision_limestone.draw_crosshairs(screenshot, points)
    cv2.imwrite("testypoints.jpg", output_image)
    while True:
        time.sleep(0.1)
        cv2.imshow('Matches', output_image)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break


def live_rgb_find_test():
    with open("gamename.txt") as f:
        gamename = f.readline()
    wincap = WindowCapture(gamename, [561, 282, 1111, 666])
    # initialize the Vision class
    vision_limestone = VisionRGB("plyrv2.jpg")
    rgb_filter = RgbFilter(79, 129, 0, 140, 206, 65)
    detected = wincap.get_screenshot()
    while True:
        screenshot = wincap.get_screenshot()
        output_image = cv2.blur(screenshot, (6, 6))
        output_image = vision_limestone.apply_rgb_filter(
            output_image, rgb_filter)
        rectangles = vision_limestone.find(
            output_image, threshold=0.51, epsilon=0.5)
        if len(rectangles) > 0:
            points = vision_limestone.get_click_points(rectangles)
            detected = vision_limestone.draw_crosshairs(screenshot, points)
        cv2.imshow('Matches', detected)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break


live_rgb_find_test()
