# First part of the file will assume
# that the player name has already been detected
import os
import cv2
import time
from rhba_utils import BotUtils, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


with open(os.path.dirname(os.path.abspath(__file__)) + "/testimages/mainplayer.txt") as f:
    player_name = f.readline()

original_image = cv2.imread(os.path.dirname(
    os.path.abspath(__file__)) + "/testimages/test_sensitive.jpg")

filter = HsvFilter(0, 0, 119, 179, 49, 255, 0, 0, 0, 0)
# output_image = BotUtils.apply_hsv_filter(original_image, filter)
output_image = BotUtils.filter_blackwhite_invert(filter, original_image)
