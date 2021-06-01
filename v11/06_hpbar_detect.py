import cv2
import numpy as np
import os
from rhba_utils import BotUtils, HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))

original_image = cv2.imread(os.path.dirname(
    os.path.abspath(__file__)) + "/testimages/healthbars.jpg")

filter = HsvFilter(20, 176, 245, 26, 193, 255, 0, 0, 0, 0)
# output_image = BotUtils.apply_hsv_filter(original_image, filter)
output_image = BotUtils.filter_blackwhite_invert(filter, original_image)

# output_image = 255 - output_image
output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2GRAY)
cv2.imwrite("testytest.jpg", output_image)

# imnorm = cv2.imread("testytest.jpg")
im = cv2.imread("testytest.jpg", cv2.IMREAD_GRAYSCALE)
ret, thresh = cv2.threshold(im, 127, 255, 0)
contours, hierarchy = cv2.findContours(
    thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for contour in contours:
    (x, y), radius = cv2.minEnclosingCircle(contour)
    center = (int(x), int(y))
    print(center)

cv2.drawContours(original_image, contours, -1, (0, 255, 0), 3)
cv2.imwrite("testycont.jpg", original_image)

# # Set up the detector with default parameters.
# params = cv2.SimpleBlobDetector_Params()
# # Change thresholds
# params.minThreshold = 10    # the graylevel of images
# params.maxThreshold = 220
# params.filterByColor = True
# params.blobColor = 255
# params.filterByCircularity = False
# params.filterByConvexity = False
# params.filterByInertia = False
# # Filter by Area
# params.filterByArea = True
# params.minArea = 100
# detector = cv2.SimpleBlobDetector(params)
# # Detect blobs.
# keypoints = detector.detect(im)
# print(keypoints)
# # Draw detected blobs as red circles.
# # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
# im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array(
#     []), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
# # Show keypoints
# cv2.imshow("Keypoints", im_with_keypoints)
# cv2.waitKey(0)

# img = output_image.copy()
# detector = cv2.SimpleBlobDetector()
# keypoints = detector.detect(img)
# print(keypoints)
# blank = np.zeros((1, 1))
# blobs = cv2.drawKeypoints(img, keypoints, blank,
#                           (0, 255, 255), cv2.DRAW_MATCHES_FLAGS_DEFAULT)
# cv2.imwrite("testyblob.jpg", img)


# cnts = cv2.findContours(output_image, cv2.RETR_EXTERNAL,
#                         cv2.CHAIN_APPROX_SIMPLE)
# cnts = cnts[0] if len(cnts) == 2 else cnts[1]
# big_contour = max(cnts, key=cv2.contourArea)

# blob_area_thresh = 10
# blob_area = cv2.contourArea(big_contour)
# if blob_area < blob_area_thresh:
#     print("Blob Is Too Small")

# cv2.drawContours(output_image, [big_contour], -1, (0, 0, 255), 1)
# cv2.imwrite("testyblob.jpg", output_image)


# params = cv2.SimpleBlobDetector_Params()
# # Change thresholds
# params.minThreshold = 0
# params.maxThreshold = 20
# # Filter by Area.
# params.filterByColor = True
# params.blobColor = 0
# params.filterByArea = False
# params.filterByCircularity = False
# params.filterByConvexity = False
# params.filterByInertia = False

# # print(params.filterByColor)
# # print(params.filterByArea)
# # print(params.filterByCircularity)
# # print(params.filterByInertia)
# # print(params.filterByConvexity)

# detector = cv2.SimpleBlobDetector(params)
# keypoints = detector.detect(output_image)
# print(keypoints)
# output_keypoints = cv2.drawKeypoints(output_image, keypoints, np.array(
#     []), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


# cv2.imwrite("testyblob.jpg", output_keypoints)
