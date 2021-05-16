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

# Options for x and y values
# x = 512, 556, 600, 644, 684, 732
# y = 277, 321, 365, 411

# The next block of code is for detecting the object in question
# initialize the WindowCapture class for object detection
object_wincap = WindowCapture(gamename, [512, 277, 775, 430])
# initialize the Vision class
object_vision = Vision('emptyslot67filt.jpg')
screenshot = object_wincap.get_screenshot()
start = time()
data = []
for i in range(4):
    for j in range(6):
        colour = screenshot[i*44, j*44]
        data.append([i+1, j+1, colour[0], colour[1], colour[2]])
for line in data:
    rgb = "{},{},{}".format(line[2], line[3], line[4])
    if rgb == "24,33,48":
        rarity = "common"
    elif rgb == "2,204,43":
        rarity = "green"
    elif rgb == "232,144,5":
        rarity = "blue"
    else:
        rarity = rgb
    print("row: {}, col: {}, Rarity={}".format(
        line[0], line[1], rarity))
end = time()
print(end-start)
while(True):
    cv.imshow('Matches', screenshot)
    sleep(0.1)
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
print('Done.')
