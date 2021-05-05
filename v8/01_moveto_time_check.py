import time
import pyautogui
import pydirectinput
import ctypes

start_time = time.time()
# pyautogui.moveTo(900, 500, 0.01)
ctypes.windll.user32.SetCursorPos(900, 500)
end_time = time.time()
print(end_time-start_time)
