# First part of the file will assume
# that the player name has already been detected
import os
import re
import cv2
import time
import pytesseract
from fuzzywuzzy import process
from rhba_utils import BotUtils, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


with open(os.path.dirname(os.path.abspath(__file__)) + "/testimages/mainplayer.txt") as f:
    player_name = f.readline()
player_chars = "".join(set(player_name))

original_image = cv2.imread(os.path.dirname(
    os.path.abspath(__file__)) + "/testimages/test_sensitive.jpg")

start_time = time.time()

filter = HsvFilter(0, 0, 119, 179, 49, 255, 0, 0, 0, 0)
# output_image = BotUtils.apply_hsv_filter(original_image, filter)
output_image = BotUtils.filter_blackwhite_invert(
    filter, original_image, return_gray=True)

print("Time taken to post-invert: {}s".format(time.time()-start_time))

rgb = cv2.cvtColor(output_image, cv2.COLOR_GRAY2RGB)
tess_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=' + player_chars
results = pytesseract.image_to_data(
    rgb, output_type=pytesseract.Output.DICT, lang='eng', config=tess_config)  # [:-2]

print("Time taken to post-tessresults: {}s".format(time.time()-start_time))

best_match, score = process.extractOne(
    player_name, results["text"], score_cutoff=0.8)

i = results["text"].index(best_match)
x = int(results["left"][i] + (results["width"][i]/2))
y = int(results["top"][i] + (results["height"][i]/2))

print("Time taken to pre-marking: {}s".format(time.time()-start_time))
marker_color = (255, 0, 255)
marker_type = cv2.MARKER_CROSS

cv2.drawMarker(original_image, (x, y),
               marker_color, marker_type)
cv2.imwrite("testypoints.jpg", original_image)

# print(best_match)
print("Time taken to end: {}s".format(time.time()-start_time))
