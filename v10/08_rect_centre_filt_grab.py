# This will be a test file for dynamically detecting items

from windowcapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter
from pytesseract import Output
import pytesseract
from PIL import Image
import os
import cv2
from time import time
from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse, keyboard
from client import ClientUtils

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# print(pytesseract.image_to_string('test_ideal.png'))
# # print(pytesseract.image_to_string(Image.open('test.png')))

# print(pytesseract.image_to_boxes(Image.open('test_ideal.png')))


loop_time = time()

with open("gamename.txt") as f:
    gamename = f.readline()
with open("player.txt") as f:
    main_player = f.readline()
x = 505
y = 250
x2 = x + 245
y2 = y + 180
wincap = WindowCapture(gamename, [x, y, x2, y2])
# initialize the Vision class
vision_limestone = Vision('xprompt67filtv2.jpg')
# initialize the trackbar window
vision_limestone.init_control_gui()
# hsv_filter = HsvFilter(0, 0, 0, 255, 255, 255, 0, 0, 0, 0)
# hsv_filter = HsvFilter(0, 0, 102, 45, 65, 255, 0, 0, 0, 0)
# print("Setup time: {}s".format(time()-loop_time))
game_wincap = WindowCapture(gamename)
scaling = ClientUtils.get_monitor_scaling()
# print(scaling)


def start_keypress_listener():
    listener = Listener(on_press=on_press,
                        on_release=on_release)
    listener.start()


def convert_click_to_ratio(truex, truey):
    global game_wincap
    global scaling
    # This will grab the current rectangle coords of game window
    # and then turn the click values into a ratio of positions
    # versus the game window
    game_wincap.update_window_position(border=False)
    # Turn the screen pos into window pos
    relx = (truex - game_wincap.window_rect[0]) * scaling
    rely = (truey - game_wincap.window_rect[1]) * scaling
    # print("relx={}, rely={}".format(relx, rely))
    # print("winx={}, winy={}".format(
    #     self.game_wincap.window_rect[0], self.game_wincap.window_rect[1]))
    # print("winwidth={}".format(self.game_wincap.w))
    # Then convert to a ratio
    ratx = relx/(game_wincap.w*scaling)
    raty = rely/(game_wincap.h*scaling)
    # Test convert back to a click
    convx, convy = convert_ratio_to_click(ratx, raty)
    print("convx={}, convy={}".format(convx, convy))
    return ratx, raty


def convert_ratio_to_click(ratx, raty):
    global game_wincap
    global scaling
    # This will grab the current rectangle coords of game window
    # and then turn the ratio of positions versus the game window
    # into true x,y coords
    game_wincap.update_window_position(border=False)
    # Turn the ratios into relative
    relx = int(ratx * game_wincap.w)
    rely = int(raty * game_wincap.h)
    # Turn the relative into true
    truex = int((relx + game_wincap.window_rect[0]))
    truey = int((rely + game_wincap.window_rect[1]))
    return truex, truey


def on_press(key):
    global wincap
    global game_wincap
    global x
    global y
    global x2
    global y2
    sensitivity = 5
    if str(key) == "Key.left":
        x = x - sensitivity
        x2 = x2 - sensitivity
        wincap = WindowCapture(gamename, [x, y, x2, y2])
    if str(key) == "Key.right":
        x = x + sensitivity
        x2 = x2 + sensitivity
        wincap = WindowCapture(gamename, [x, y, x2, y2])
    if str(key) == "Key.up":
        y = y - sensitivity
        y2 = y2 - sensitivity
        wincap = WindowCapture(gamename, [x, y, x2, y2])
    if str(key) == "Key.down":
        y = y + sensitivity
        y2 = y2 + sensitivity
        wincap = WindowCapture(gamename, [x, y, x2, y2])
    if key == KeyCode(char='p'):
        print("x={}, y={}, x2={}, y2={}".format(x, y, x2, y2))
        xmid = (x2+x)/2
        ymid = (y2+y)/2
        xrat = xmid/game_wincap.w
        yrat = ymid/game_wincap.h
        print("Centre_ratio={},{}".format(xrat, yrat))
    if str(key) == "<100>":
        x2 = x2 - sensitivity
        wincap = WindowCapture(gamename, [x, y, x2, y2])
    if str(key) == "<102>":
        x2 = x2 + sensitivity
        wincap = WindowCapture(gamename, [x, y, x2, y2])
    if str(key) == "<104>":
        y2 = y2 - sensitivity
        wincap = WindowCapture(gamename, [x, y, x2, y2])
    if str(key) == "<98>":
        y2 = y2 + sensitivity
        wincap = WindowCapture(gamename, [x, y, x2, y2])
    # else:
    #     print(key)


def on_release(key):
    pass


start_keypress_listener()

# loop_time = time()
while(True):

    # get an updated image of the game
    image = wincap.get_screenshot()
    # pre-process the image
    image = vision_limestone.apply_hsv_filter(image)
    # display the processed image

    cv2.imshow('Filtered', image)

    # debug the loop rate
    # print('FPS {}'.format(1 / (time() - loop_time)))
    # print("Calc time: {}s".format(time()-loop_time))
    # loop_time = time()
    # break
    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break
# print(text)

# print("Done")
os._exit(1)
