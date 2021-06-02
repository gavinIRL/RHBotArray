
from windowcapture import WindowCapture
import cv2
import time
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def xprompt_checker():
    with open("gamename.txt") as f:
        gamename = f.readline()
    wincap = WindowCapture(gamename, custom_rect=[
        1135, 691, 1162, 692])
    # while True:
    image = wincap.get_screenshot()
    a, b, c = [int(i) for i in image[0][0]]
    d, e, f = [int(i) for i in image[0][-1]]
    print("abc: {},{},{}".format(a, b, c))
    print("def: {},{},{}".format(d, e, f))
    # if a+b+c > 700 and d+e+f > 700:
    #     print("Detected sect clear")
    #     break
    # else:
    #     time.sleep(0.1)


xprompt_checker()
