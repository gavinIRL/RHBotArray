# This file will move the mouse to a particular location
from windowcapture import WindowCapture
import ctypes


class MoveMouse():
    def __init__(self, game=False) -> None:
        with open("gamename.txt") as f:
            self.gamename = f.readline()
        self.game = game
        if game:
            self.game_wincap = WindowCapture(self.gamename)

    def move_mouse(self, x, y, rat=False):
        if rat and self.game:
            x, y = self.convert_ratio_to_click(x, y)
            ctypes.windll.user32.SetCursorPos(x, y)
        elif rat:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
            x = int(x*w)
            y = int(y*h)
            ctypes.windll.user32.SetCursorPos(x, y)
        elif self.game:
            x = x + self.wincap.window_rect[0]
            y = y + self.wincap.window_rect[1]
            ctypes.windll.user32.SetCursorPos(x, y)
        else:
            ctypes.windll.user32.SetCursorPos(x, y)

    def convert_ratio_to_click(self, ratx, raty):
        # This will grab the current rectangle coords of game window
        # and then turn the ratio of positions versus the game window
        # into true x,y coords
        self.wincap.update_window_position(border=False)
        # Turn the ratios into relative
        relx = int(ratx * self.wincap.w)
        rely = int(raty * self.wincap.h)
        # Turn the relative into true
        truex = int((relx + self.wincap.window_rect[0]))
        truey = int((rely + self.wincap.window_rect[1]))
        return truex, truey


if __name__ == "__main__":
    mm = MoveMouse()
    mm.move_mouse(100, 200)
