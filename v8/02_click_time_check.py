import time
import pyautogui
import pydirectinput
import ctypes

start_time = time.time()
# pyautogui.moveTo(900, 500, 0.01)
ctypes.windll.user32.SetCursorPos(30, 60)
# pyautogui.click(1800, 900, duration=0.01)
ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)
ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)
end_time = time.time()
print(end_time-start_time)
