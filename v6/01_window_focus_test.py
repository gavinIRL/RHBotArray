from win32gui import GetWindowText, GetForegroundWindow
import time

start_time = time.time()
with open("gamename.txt") as f:
    gamename = f.readline()
mid_time = time.time()
fg = GetWindowText(GetForegroundWindow())
end_time = time.time()
print("Open: {}s, GetWindow {}s".format(
    mid_time-start_time, end_time-mid_time))
