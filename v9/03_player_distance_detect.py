# This file will dynamically calculate and print out the
# distance between the current player tag and the
# target player tag

from windowcapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter
from pytesseract import Output
import pytesseract
from PIL import Image
import os
import cv2
from time import time

with open("gamename.txt") as f:
    gamename = f.readline()
with open("player.txt") as f:
    main_player = f.readline()
with open("currplayer.txt") as f:
    curr_player = f.readline()
wincap = WindowCapture(gamename, [510, 260, 755, 450])
# initialize the Vision class
vision_limestone = Vision('xprompt67filtv2.jpg')
# initialize the trackbar window
# vision_limestone.init_control_gui()
hsv_filter = HsvFilter(94, 188, 255, 137, 255, 255, 0, 0, 0, 0)

loop_time = time()
while(True):

    # get an updated image of the game
    image = wincap.get_screenshot()
    # pre-process the image
    image = vision_limestone.apply_hsv_filter(image, hsv_filter)
    # display the processed image

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = pytesseract.image_to_data(
        rgb, output_type=Output.DICT, lang='eng')

    # format is currplayer x, y, mainplayer x, y
    positions = [0, 0, 0, 0]

    for i in range(0, len(results["text"])):
        if results["text"][i] == main_player:
            positions[2] = results["left"][i] + (results["width"][i]/2)
            positions[3] = results["top"][i] + (results["height"][i]/2)
        elif results["text"][i] == curr_player:
            positions[2] = results["left"][i] + (results["width"][i]/2)
            positions[3] = results["top"][i] + (results["height"][i]/2)

        # if(tmp_level == 5):
        #     cv2.putText(image, text, (tmp_tl_x, tmp_tl_y - 10),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        #     cv2.rectangle(image, (tmp_tl_x, tmp_tl_y),
        #                   (tmp_br_x, tmp_br_y), (0, 0, 255), 1)
    xrel = positions[2] - positions[0]
    yrel = positions[3] - positions[1]
    print("xrel: {}, yrel: {}".format(xrel, yrel))
    #cv2.imshow('Filtered', image)

    # debug the loop rate
    # print('FPS {}'.format(1 / (time() - loop_time)))
    # loop_time = time()
    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break
