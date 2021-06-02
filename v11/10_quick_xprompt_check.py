
from windowcapture import WindowCapture
import cv2
import time
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def xprompt_checker():
    with open("gamename.txt") as f:
        gamename = f.readline()
    wincap = WindowCapture(gamename, custom_rect=[
        1137, 694, 1163, 752])
    # while True:
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    print("abc: {},{},{}".format(a, b, c))
    print("def: {},{},{}".format(d, e, f))
    cv2.imwrite("testytest.jpg", image)
    if a+b+d+e > 960 and c+f == 70:
        return True
    else:
        return False


xprompt_checker()
