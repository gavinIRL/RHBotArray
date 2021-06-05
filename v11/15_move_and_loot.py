import pydirectinput
from rhba_utils import BotUtils, WindowCapture, HsvFilter, Looting
from custom_input import CustomInput
import time
import os
import cv2
import math
import pytesseract
with open("gamename.txt") as f:
    gamename = f.readline()
start_time = time.time()
Looting.check_for_loot(gamename)
print("Time taken: {}s".format(time.time()-start_time))

# 0.3s appears to be worst case time for check for loot
