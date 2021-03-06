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
# wincap = WindowCapture(gamename, [395, 745, 591, 788])
# image = wincap.get_screenshot()
# a, _, _ = [int(i) for i in image[0][0]]
# b, _, _ = [int(i) for i in image[0][39]]
# c, _, _ = [int(i) for i in image[0][78]]
# d, _, _ = [int(i) for i in image[0][117]]
# e, _, _ = [int(i) for i in image[0][156]]
# f, _, _ = [int(i) for i in image[0][195]]
# print("abc:{},{},{} def:{},{},{}".format(a, b, c, d, e, f))
# cv2.imwrite("testytest.jpg", image)


def check_off_cooldown(gamename):
    cd_list = [False, False, False, False, False, False]
    wincap = WindowCapture(gamename, [395, 745, 591, 788])
    image = wincap.get_screenshot()
    a, _, _ = [int(i) for i in image[0][0]]
    b, _, _ = [int(i) for i in image[0][39]]
    c, _, _ = [int(i) for i in image[0][78]]
    d, _, _ = [int(i) for i in image[0][117]]
    e, _, _ = [int(i) for i in image[0][156]]
    f, _, _ = [int(i) for i in image[0][195]]
    if a != 56:
        cd_list[0] = True
    if b != 11:
        cd_list[1] = True
    if c != 44:
        cd_list[2] = True
    if d != 245:
        cd_list[3] = True
    if e != 231:
        cd_list[4] = True
    if f != 142:
        cd_list[5] = True
    return cd_list


def check_off_cooldown_tab2(gamename):
    cd_list = [False, False, False, False, False, False]
    wincap = WindowCapture(gamename, [395, 745, 591, 788])
    image = wincap.get_screenshot()
    a, _, _ = [int(i) for i in image[0][0]]
    b, _, _ = [int(i) for i in image[0][39]]
    c, _, _ = [int(i) for i in image[0][78]]
    # d, _, _ = [int(i) for i in image[0][117]]
    # e, _, _ = [int(i) for i in image[0][156]]
    # f, _, _ = [int(i) for i in image[0][195]]
    if a != 56:
        cd_list[0] = True
    if b != 11:
        cd_list[1] = True
    if c != 44:
        cd_list[2] = True
    # if d != 245:
    #     cd_list[3] = True
    # if e != 231:
    #     cd_list[4] = True
    # if f != 142:
    #     cd_list[5] = True
    return cd_list


def grab_skilltab(gamename):
    wincap = WindowCapture(gamename, [361, 755, 591, 788])
    image = wincap.get_screenshot()
    # cv2.imwrite("testytest.jpg", image)
    a, _, _ = [int(i) for i in image[0][0]]
    if a == 144:
        return 1
    elif a == 18:
        return 2
    else:
        return False


grab_skilltab(gamename)
# start = time.time()
# print(check_off_cooldown(gamename))
# total = time.time()-start
# print("Time taken: {}s".format(total))
