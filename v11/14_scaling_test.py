from rhba_utils import BotUtils, WindowCapture
from test2 import scaling, get_monitor_scaling2
import ctypes
from win32api import GetSystemMetrics
import time
import pydirectinput
import threading
with open("gamename.txt") as f:
    gamename = f.readline()
# if BotUtils.detect_bigmap_open(gamename):
#     print("bigmap detected")


def get_monitor_scaling4():
    w1 = GetSystemMetrics(0)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    w2 = GetSystemMetrics(0)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    w3 = GetSystemMetrics(0)
    ctypes.windll.shcore.SetProcessDpiAwareness(0)
    w4 = GetSystemMetrics(0)
    print([w1, w2, w3, w4])
    # return w1, w2, w3, w4


def get_monitor_scaling5():
    scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    print(scaleFactor)


get_monitor_scaling5()
get_monitor_scaling5()
get_monitor_scaling5()
get_monitor_scaling5()


def get_monitor_scaling3():
    user32 = ctypes.windll.user32
    awareness = ctypes.c_int()
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(
        0, ctypes.byref(awareness))
    print(awareness.value)
    w_orig = GetSystemMetrics(0)
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(1)
    # print(w_orig)
    # user32.SetProcessDpiAwareness(1)
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(
        0, ctypes.byref(awareness))
    print(awareness.value)
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(0)
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(
        0, ctypes.byref(awareness))
    print(awareness.value)
    w = user32.GetSystemMetrics(0)
    return float(("{:.3f}".format(w/w_orig)))


# scaling1 = BotUtils.get_monitor_scaling()
# print(scaling1)
# scaling2 = BotUtils.get_monitor_scaling()
# print(scaling2)

# print(scaling())

# print(get_monitor_scaling2())

# get_monitor_scaling3()
# get_monitor_scaling3()
# print(get_monitor_scaling4())

# print(get_monitor_scaling3())
# print(get_monitor_scaling3())

# game_wincap = WindowCapture(gamename)
# print(game_wincap.window_rect[0])
# time.sleep(1)
# game_wincap.focus_window()
# game_wincap.set_position_topleft()
# game_wincap.update_window_position()
# print(game_wincap.window_rect[0])
# pydirectinput.moveTo(100, 150)
# pydirectinput.click()
# game_wincap.focus_window()
# time.sleep(1)
# game_wincap.update_window_position()
# print(game_wincap.window_rect[0])

# BotUtils.close_map_and_menu(gamename)
