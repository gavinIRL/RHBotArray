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

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# print(pytesseract.image_to_string('test_ideal.png'))
# # print(pytesseract.image_to_string(Image.open('test.png')))

# print(pytesseract.image_to_boxes(Image.open('test_ideal.png')))

loop_time = time()

with open("gamename.txt") as f:
    gamename = f.readline()
with open("player.txt") as f:
    main_player = f.readline()
wincap = WindowCapture(gamename, [510, 260, 755, 450])
# initialize the Vision class
vision_limestone = Vision('xprompt67filtv2.jpg')
# initialize the trackbar window
# vision_limestone.init_control_gui()
hsv_filter = HsvFilter(94, 188, 255, 137, 255, 255, 0, 0, 0, 0)
print("Setup time: {}s".format(time()-loop_time))

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

    for i in range(0, len(results["text"])):
        # extract the bounding box coordinates of the text region from the current result
        tmp_tl_x = results["left"][i]
        tmp_tl_y = results["top"][i]
        tmp_br_x = tmp_tl_x + results["width"][i]
        tmp_br_y = tmp_tl_y + results["height"][i]
        tmp_level = results["level"][i]
        conf = results["conf"][i]
        text = results["text"][i]

        if(tmp_level == 5):
            cv2.putText(image, text, (tmp_tl_x, tmp_tl_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.rectangle(image, (tmp_tl_x, tmp_tl_y),
                          (tmp_br_x, tmp_br_y), (0, 0, 255), 1)

    cv2.imshow('Filtered', image)

    # debug the loop rate
    # print('FPS {}'.format(1 / (time() - loop_time)))
    print("Calc time: {}s".format(time()-loop_time))
    loop_time = time()
    # break
    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break
# print(text)
print("Main player detected: {}".format(main_player in results["text"]))

# print("Done")
os._exit(1)
