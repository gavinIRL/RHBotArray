import os
import cv2
import numpy as np
import pytesseract
from hsvfilter import HsvFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class BotUtils():
    def shift_channel(c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c

    def filter_blackwhite_invert(filter, existing_image):
        hsv = cv2.cvtColor(existing_image, cv2.COLOR_BGR2HSV)
        hsv_filter = filter
        # add/subtract saturation and value
        h, s, v = cv2.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
        hsv = cv2.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR
        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
        # now change it to greyscale
        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # now change it to black and white
        (thresh, blackAndWhiteImage) = cv2.threshold(
            grayImage, 67, 255, cv2.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        inverted = cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)
        return inverted

    def detect_level_name(self):
        wincap = WindowCapture(self.gamename, [1121, 31, 1248, 44])
        existing_image = wincap.get_screenshot()
        filter = HsvFilter(0, 0, 0, 169, 34, 255, 0, 0, 0, 0)
        # cv2.imwrite("testy2.jpg", existing_image)
        save_image = BotUtils.apply_hsv_filter(existing_image, filter)
        # cv2.imwrite("testy3.jpg", save_image)
        gray_image = cv2.cvtColor(save_image, cv2.COLOR_BGR2GRAY)
        (thresh, blackAndWhiteImage) = cv2.threshold(
            gray_image, 129, 255, cv2.THRESH_BINARY)
        # now invert it
        inverted = (255-blackAndWhiteImage)
        save_image = cv2.cvtColor(inverted, cv2.COLOR_GRAY2BGR)
        rgb = cv2.cvtColor(save_image, cv2.COLOR_BGR2RGB)
        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = pytesseract.image_to_string(
            rgb, lang='eng', config=tess_config)[:-2]
        return result

    def apply_hsv_filter(original_image, hsv_filter):
        # convert image to HSV
        hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

        # add/subtract saturation and value
        h, s, v = cv2.split(hsv)
        s = BotUtils.shift_channel(s, hsv_filter.sAdd)
        s = BotUtils.shift_channel(s, -hsv_filter.sSub)
        v = BotUtils.shift_channel(v, hsv_filter.vAdd)
        v = BotUtils.shift_channel(v, -hsv_filter.vSub)
        hsv = cv2.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR for imshow() to display it properly
        img = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)

        return img

    def detect_bigmap_open(self, gamename):
        wincap = WindowCapture(gamename, custom_rect=[819, 263, 855, 264])
        image = wincap.get_screenshot()
        cv2.imwrite("testy.jpg", image)
        a, b, c = [int(i) for i in image[0][0]]
        d, e, f = [int(i) for i in image[0][-2]]
        if a+b+c < 30:
            if d+e+f > 700:
                return True
        return False

    def grab_player_pos(self, gamename, map_rect=None):
        if not map_rect:
            wincap = WindowCapture(gamename)
        else:
            wincap = WindowCapture(gamename, map_rect)
        filter = HsvFilter(34, 160, 122, 50, 255, 255, 0, 0, 0, 0)
        image = wincap.get_screenshot()
        save_image = self.filter_blackwhite_invert(filter, image)
        vision_limestone = Vision('plyr.jpg')
        rectangles = vision_limestone.find(
            save_image, threshold=0.31, epsilon=0.5)
        points = vision_limestone.get_click_points(rectangles)
        x, y = points[0]
        if not self.map_rect:
            return x, y
        else:
            x += wincap.window_rect[0]
            y += wincap.window_rect[1]
            return x, y

    def grab_level_catalogue(self):
        # Load the translation from name to num
        with open("lvl_name_num.txt") as f:
            self.num_names = f.readlines()
        for i, entry in enumerate(self.num_names):
            self.num_names[i] = entry.split("-")
        # Load the num to rect catalogue
        with open("catalogue.txt") as f:
            nums_rects = f.readlines()
        for i, entry in enumerate(nums_rects):
            nums_rects[i] = entry.split("-")
        # Then add each rect to the rects dict against name
        for number, name in self.num_names:
            for num, area, rect in nums_rects:
                if area == "FM" and num == number:
                    self.rects[name.rstrip().replace(" ", "")] = rect.rstrip()
                    if "1" in name:
                        self.rects[name.rstrip().replace(
                            " ", "").replace("1", "L")] = rect.rstrip()
                    if "ri" in name:
                        self.rects[name.rstrip().replace(
                            " ", "").replace("ri", "n").replace("1", "L")] = rect.rstrip()
                    break


class Vision:
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    def __init__(self, needle_img_path, method=cv2.TM_CCOEFF_NORMED):
        self.needle_img = cv2.imread(needle_img_path, cv2.IMREAD_UNCHANGED)
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method

    def find(self, haystack_img, threshold=0.7, max_results=15, epsilon=0.5):
        result = cv2.matchTemplate(haystack_img, self.needle_img, self.method)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            rectangles.append(rect)
            rectangles.append(rect)
        rectangles, weights = cv2.groupRectangles(
            rectangles, groupThreshold=1, eps=epsilon)
        return rectangles

    def get_click_points(self, rectangles):
        points = []
        for (x, y, w, h) in rectangles:
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
        return points

    def draw_rectangles(self, haystack_img, rectangles):
        # BGR
        line_color = (0, 255, 0)
        line_type = cv2.LINE_4
        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv2.rectangle(haystack_img, top_left, bottom_right,
                          line_color, lineType=line_type)
        return haystack_img

    def draw_crosshairs(self, haystack_img, points):
        # BGR
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS

        for (center_x, center_y) in points:
            cv2.drawMarker(haystack_img, (center_x, center_y),
                           marker_color, marker_type)

        return haystack_img


class DynamicFilter():
    TRACKBAR_WINDOW = "Trackbars"
    # create gui window with controls for adjusting arguments in real-time

    def init_control_gui(self):
        cv2.namedWindow(self.TRACKBAR_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        # required callback. we'll be using getTrackbarPos() to do lookups
        # instead of using the callback.
        def nothing(position):
            pass

        # create trackbars for bracketing.
        # OpenCV scale for HSV is H: 0-179, S: 0-255, V: 0-255
        cv2.createTrackbar('HMin', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv2.createTrackbar('SMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('HMax', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv2.createTrackbar('SMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        # Set default value for Max HSV trackbars
        cv2.setTrackbarPos('HMax', self.TRACKBAR_WINDOW, 179)
        cv2.setTrackbarPos('SMax', self.TRACKBAR_WINDOW, 255)
        cv2.setTrackbarPos('VMax', self.TRACKBAR_WINDOW, 255)

        # trackbars for increasing/decreasing saturation and value
        cv2.createTrackbar('SAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('SSub', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv2.createTrackbar('VSub', self.TRACKBAR_WINDOW, 0, 255, nothing)

    # returns an HSV filter object based on the control GUI values
    def get_hsv_filter_from_controls(self):
        # Get current positions of all trackbars
        hsv_filter = HsvFilter()
        hsv_filter.hMin = cv2.getTrackbarPos('HMin', self.TRACKBAR_WINDOW)
        hsv_filter.sMin = cv2.getTrackbarPos('SMin', self.TRACKBAR_WINDOW)
        hsv_filter.vMin = cv2.getTrackbarPos('VMin', self.TRACKBAR_WINDOW)
        hsv_filter.hMax = cv2.getTrackbarPos('HMax', self.TRACKBAR_WINDOW)
        hsv_filter.sMax = cv2.getTrackbarPos('SMax', self.TRACKBAR_WINDOW)
        hsv_filter.vMax = cv2.getTrackbarPos('VMax', self.TRACKBAR_WINDOW)
        hsv_filter.sAdd = cv2.getTrackbarPos('SAdd', self.TRACKBAR_WINDOW)
        hsv_filter.sSub = cv2.getTrackbarPos('SSub', self.TRACKBAR_WINDOW)
        hsv_filter.vAdd = cv2.getTrackbarPos('VAdd', self.TRACKBAR_WINDOW)
        hsv_filter.vSub = cv2.getTrackbarPos('VSub', self.TRACKBAR_WINDOW)
        return hsv_filter


class HsvFilter:
    def __init__(self, hMin=None, sMin=None, vMin=None, hMax=None, sMax=None, vMax=None,
                 sAdd=None, sSub=None, vAdd=None, vSub=None):
        self.hMin = hMin
        self.sMin = sMin
        self.vMin = vMin
        self.hMax = hMax
        self.sMax = sMax
        self.vMax = vMax
        self.sAdd = sAdd
        self.sSub = sSub
        self.vAdd = vAdd
        self.vSub = vSub
