import cv2
import os
import time
from rhba_utils import BotUtils, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))

start_time = time.time()

original_image = cv2.imread(os.path.dirname(
    os.path.abspath(__file__)) + "/testimages/healthbars.jpg")
