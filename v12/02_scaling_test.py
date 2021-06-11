import ctypes
import time
import os
from rhba_utils import BotUtils, WindowCapture
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# def get_monitor_scaling():
#     scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
#     return float(scaleFactor)


# time.sleep(2)
# print(get_monitor_scaling())


with open("gamename.txt") as f:
    gamename = f.readline()
wincap = WindowCapture(gamename)
wincap.update_window_position(False)
print(wincap.window_rect[0])
