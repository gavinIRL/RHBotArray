from windowcapture import WindowCapture
import os
import cv2
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open("gamename.txt") as f:
    gamename = f.readline()
# rect=[415, 533, 888, 700])
wincap = WindowCapture(gamename)
wincap.update_window_position(False)
image = wincap.get_screenshot()
cv2.imwrite("testytest.jpg", image)
