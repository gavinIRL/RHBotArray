import cv2
import numpy as np
import os
from rhba_utils import BotUtils, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))

original_image = cv2.imread(os.path.dirname(
    os.path.abspath(__file__)) + "/testimages/healthbars.jpg")

filter = HsvFilter(20, 174, 245, 26, 193, 255, 0, 0, 0, 0)
# output_image = BotUtils.apply_hsv_filter(original_image, filter)
output_image = BotUtils.filter_blackwhite_invert(filter, original_image)

# output_image = 255 - output_image
output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2GRAY)
cv2.imwrite("testytest.jpg", output_image)

# imnorm = cv2.imread("testytest.jpg")
im = cv2.imread("testytest.jpg", cv2.IMREAD_GRAYSCALE)
im = cv2.blur(im, (2, 2))
ret, thresh = cv2.threshold(im, 127, 255, 0)
contours, hierarchy = cv2.findContours(
    thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

contours = sorted(contours, key=cv2.contourArea, reverse=True)
contours.pop(0)

rectangles = []

for contour in contours:
    (x, y), radius = cv2.minEnclosingCircle(contour)
    rectangles.append([x-10, y, 20, 5])
    rectangles.append([x-10, y, 20, 5])
    # center = (int(x), int(y))
    # print(center)

rectangles, weights = cv2.groupRectangles(
    rectangles, groupThreshold=1, eps=0.8)

points = []
# Loop over all the rectangles
for (x, y, w, h) in rectangles:
    # Determine the center position
    center_x = x + int(w/2)
    center_y = y + int(h/2)
    # Save the points
    points.append((center_x, center_y))
print(points)

cv2.drawContours(original_image, contours, -1, (0, 255, 0), 3)
cv2.imwrite("testycont.jpg", original_image)

marker_color = (255, 0, 255)
marker_type = cv2.MARKER_CROSS
for (center_x, center_y) in points:
    # draw the center point
    cv2.drawMarker(original_image, (center_x, center_y),
                   marker_color, marker_type)

cv2.imwrite("testypoints.jpg", original_image)
