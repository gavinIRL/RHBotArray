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
# initialize the WindowCapture class for object detection
object_wincap = WindowCapture(gamename, [510, 250, 775, 430])
# initialize the Vision class
object_vision = Vision('emptyslot67filt.jpg')
screenshot = object_wincap.get_screenshot()
print(screenshot[0, 0])
while(True):
    cv.imshow('Matches', screenshot)
    sleep(0.15)
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
print('Done.')
