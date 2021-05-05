import time
import pyautogui
import pydirectinput
import ctypes

MOUSE_LEFTDOWN = 0x0002     # left button down
MOUSE_LEFTUP = 0x0004       # left button up
MOUSE_RIGHTDOWN = 0x0008    # right button down
MOUSE_RIGHTUP = 0x0010      # right button up
MOUSE_MIDDLEDOWN = 0x0020   # middle button down
MOUSE_MIDDLEUP = 0x0040     # middle button up

start_time = time.time()
# pyautogui.moveTo(900, 500, 0.01)
ctypes.windll.user32.SetCursorPos(30, 60)
# pyautogui.click(1800, 900, duration=0.01)
ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)
ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)
end_time = time.time()
print(end_time-start_time)
