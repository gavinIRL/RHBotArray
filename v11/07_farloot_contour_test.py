import cv2
import os
import time
from rhba_utils import BotUtils, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))

start_time = time.time()

original_image = cv2.imread(os.path.dirname(
    os.path.abspath(__file__)) + "/testimages/lootscene.jpg")

filter = HsvFilter(16, 140, 0, 26, 255, 49, 0, 0, 0, 0)
output_image = BotUtils.filter_blackwhite_invert(
    filter, original_image, True, 0, 180)

cv2.imwrite("testytest.jpg", output_image)

output_image = cv2.blur(output_image, (3, 2))
_, thresh = cv2.threshold(output_image, 127, 255, 0)
contours, _ = cv2.findContours(
    thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)
contours.pop(0)
rectangles = []
for contour in contours:
    (x, y), _ = cv2.minEnclosingCircle(contour)
    rectangles.append([x-50, y, 100, 5])
    rectangles.append([x-50, y, 100, 5])
rectangles, _ = cv2.groupRectangles(
    rectangles, groupThreshold=1, eps=0.9)
points = []
for (x, y, w, h) in rectangles:
    center_x = x + int(w/2)
    center_y = y + int(h/2)
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
