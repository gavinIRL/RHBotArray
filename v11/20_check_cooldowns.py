import time
import os
import cv2
import ctypes
import pydirectinput
from custom_input import CustomInput
from rhba_utils import BotUtils, Events, SellRepair, RHClick, Looting, WindowCapture
os.chdir(os.path.dirname(os.path.abspath(__file__)))


with open("gamename.txt") as f:
    gamename = f.readline()
wincap = WindowCapture(gamename, [395, 745, 591, 788])
image = wincap.get_screenshot()
a, _, _ = [int(i) for i in image[0][0]]
b, _, _ = [int(i) for i in image[0][39]]
c, _, _ = [int(i) for i in image[0][78]]
d, _, _ = [int(i) for i in image[0][117]]
e, _, _ = [int(i) for i in image[0][156]]
f, _, _ = [int(i) for i in image[0][195]]
print("abc:{},{},{} def:{},{},{}".format(a, b, c, d, e, f))
cv2.imwrite("testytest.jpg", image)
