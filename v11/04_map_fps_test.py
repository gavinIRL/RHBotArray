import cv2 as cv
import os
from time import time
from windowcapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Choose between either fullmap
wincap = WindowCapture(custom_rect=[561, 282, 1111, 666])
# or room-only
# wincap = WindowCapture(custom_rect=[649, 594, 755, 639])

vision_limestone = Vision('normalenemytag.jpg')
# initialize the trackbar window
# vision_limestone.init_control_gui()
# limestone HSV filter
hsv_filter = HsvFilter(34, 160, 122, 50, 255, 255, 0, 0, 0, 0)

loop_time = time()
while(True):

    # get an updated image of the game
    screenshot = wincap.get_screenshot()
    # pre-process the image
    output_image = vision_limestone.apply_hsv_filter(screenshot, hsv_filter)
    # filter_image = output_image.copy()
    # do object detection
    rectangles = vision_limestone.find(
        output_image, threshold=0.61, epsilon=0.5)
    # draw the detection results onto the original image
    output_image = vision_limestone.draw_rectangles(screenshot, rectangles)
    # display the processed image
    # cv.imshow('Matches', output_image)
    # cv.imshow('Filtered', filter_image)

    # debug the loop rate
    # print('FPS {}'.format(1 / (time() - loop_time)))
    # loop_time = time()

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')
