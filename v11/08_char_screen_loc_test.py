# First part of the file will assume
# that the player name has already been detected
import os
import re
import cv2
import time
import pytesseract
from rhba_utils import BotUtils, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


with open(os.path.dirname(os.path.abspath(__file__)) + "/testimages/mainplayer.txt") as f:
    player_name = f.readline()
player_chars = "".join(set(player_name))

original_image = cv2.imread(os.path.dirname(
    os.path.abspath(__file__)) + "/testimages/test_sensitive.jpg")

filter = HsvFilter(0, 0, 119, 179, 49, 255, 0, 0, 0, 0)
# output_image = BotUtils.apply_hsv_filter(original_image, filter)
output_image = BotUtils.filter_blackwhite_invert(
    filter, original_image, return_gray=True)

rgb = cv2.cvtColor(output_image, cv2.COLOR_GRAY2RGB)
tess_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=' + player_chars
results = pytesseract.image_to_data(
    rgb, output_type=pytesseract.Output.DICT, lang='eng', config=tess_config)  # [:-2]

print(results["text"])
