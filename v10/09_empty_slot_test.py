import cv2 as cv
import numpy as np
import os
from time import time, sleep
from windowcapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter, grab_object_preset

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open("gamename.txt") as f:
    gamename = f.readline()
game_wincap = WindowCapture(gamename)

# The next block of code is for detecting the object in question
object_filter = HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0)
# WindowCapture.list_window_names()
# initialize the WindowCapture class for object detection
object_wincap = WindowCapture(gamename, [505, 250, 750, 430])
# initialize the Vision class
object_vision = Vision('emptyslot.jpg')
# initialize the trackbar window
# object_vision.init_control_gui()


loop_time = time()
while(True):

    # get an updated image of the game at map loc
    screenshot = object_wincap.get_screenshot()
    # then try to detect the other player
    output_image = object_vision.apply_hsv_filter(
        screenshot, object_filter)
    # filter_image = output_image.copy()
    # do object detection, this time grab the points
    rectangles = object_vision.find(
        output_image, threshold=0.41, epsilon=0.5)
    # draw the detection results onto the original image
    points = object_vision.get_click_points(rectangles)
    if len(points) >= 1:
        output_image = object_vision.draw_crosshairs(screenshot, points)
        # If there is only one value found
        # i.e. no false positives and players are not on top of each other
        # Then figure out keypresses required to move towards other player
        # And then implement
        print("Other player is located relatively x={} y={}".format(
            points[0][0]-131, 107-points[0][1]))
        sleep(1)
    else:
        # Clear all keypresses
        print("Can't detect other player, stopping movement")
    # display the processed image
    cv.imshow('Matches', output_image)
    # cv.imshow('Filtered', filter_image)

    # debug the loop rate
    # print('FPS {}'.format(1 / (time() - loop_time)))
    # loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')
