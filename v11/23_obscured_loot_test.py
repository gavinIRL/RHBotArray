import cv2
import time
import os
import numpy as np
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture, Vision, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open("gamename.txt") as f:
    gamename = f.readline()

vision = Vision("lootside2.jpg")
wincap = WindowCapture(gamename, [510, 349, 775, 500])

start = time.time()

screenshot = wincap.get_screenshot()
original_image = screenshot
# original_image = cv2.blur(screenshot, (1, 2))
# original_image = cv2.blur(original_image, (8, 1))
# original_image = cv2.blur(original_image, (8, 1))

# cv2.imwrite("testytest.jpg", original_image)
# t = 6  # tolerance

# lootbox_thresh1 = cv2.inRange(original_image, np.array(
#     [26 - t, 37 - t, 47 - t]), np.array([26 + t, 37 + t, 47 + t]))

t = 2
# lootbox_thresh2 = cv2.inRange(original_image, np.array(
#     [0, 13, 21]), np.array([8, 19, 30]))
lootbox_thresh2 = cv2.inRange(original_image, np.array(
    [29, 44, 49]), np.array([62, 67, 78]))
# green_thresh = cv2.inRange(original_image, np.array(
#     [104 - t, 214 - t, 99 - t]), np.array([104 + t, 214 + t, 99 + t]))
# red_1_thresh = cv2.inRange(original_image, np.array(
#     [50 - t, 60 - t, 242 - t]), np.array([50 + t, 60 + t, 242 + t]))
# red_2_thresh = cv2.inRange(original_image, np.array(
#     [31 - t, 31 - t, 129 - t]), np.array([31 + t, 31 + t, 129 + t]))

combined_mask = lootbox_thresh2  # + green_thresh + red_1_thresh + red_2_thresh

combined_mask_inv = 255 - combined_mask

combined_mask_rgb = cv2.cvtColor(combined_mask_inv, cv2.COLOR_GRAY2BGR)

final = cv2.max(original_image, combined_mask_rgb)


rectangles = vision.find(
    original_image, threshold=0.81, epsilon=0.5)

print("Time taken: {}s".format(time.time()-start))

output_image = vision.draw_rectangles(screenshot, rectangles)

cv2.imwrite("testycont.jpg", output_image)
cv2.imwrite("testypoints.jpg", final)
