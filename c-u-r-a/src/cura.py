import os
import time
import subprocess
import win32gui
from PIL import ImageGrab
import cv2 as cv
import numpy
import pyautogui


class Cura():
    def __init__(self):
        self.top_level_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.ftl_game_dir = os.path.join(self.top_level_dir, "flt_game_files")
        self.ftl_process = None
        self.ftl_hwnd = 0
        self.ftl_game_rect = (0, 0, 0, 0)
        self.game_image = None
        self.image_dir = os.path.join(self.top_level_dir, "images")
        self.launch_ftl()
        self.wait_until_title_menu()

    def launch_ftl(self):
        # The game makes some files when it runs so we run the game 
        # from a known directory so it doesn't pollute anything
        os.makedirs(self.ftl_game_dir, exist_ok=True)
        self.ftl_process = subprocess.Popen(
            ["C:\\Program Files (x86)\\Steam\\steamapps\\common\\FTL Faster Than Light\\FTLGame.exe"],
            cwd=self.ftl_game_dir
        )
        # Get a handle for the game window then move it to a known location
        while(self.ftl_hwnd == 0):
            self.ftl_hwnd = win32gui.FindWindow(None, "FTL: Multiverse")
        win32gui.SetActiveWindow(self.ftl_hwnd)
        win_left, win_top, win_right, win_bottom = win32gui.GetWindowRect(self.ftl_hwnd)
        win_width = win_right - win_left
        win_height = win_bottom - win_top
        win32gui.MoveWindow(self.ftl_hwnd, -7, 0, win_width, win_height, True)
        # Figure out the actual rect for the game window. No borders, no padding, no title
        win_left, win_top, win_right, win_bottom = win32gui.GetWindowRect(self.ftl_hwnd)
        self.ftl_game_rect = (win_left + 8, win_top + 32, win_right - 8, win_bottom - 8)

    def open_image(self, image_name):
        return cv.imread(os.path.join(self.image_dir, image_name))

    def wait_until_title_menu(self):
        self.wait_for_image(self.open_image("title_screen_new_game.png"))

    def wait_for_image(self, image):
        image_found = False
        while not image_found:
            self.grab_game_image()
            image_found = self.look_for_image(image)
            
    def look_for_image(self, image, confidence=0.99):
        res = cv.matchTemplate(self.game_image, image, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(res)
        return max_val > confidence

    def grab_game_image(self):
        pil_image = ImageGrab.grab(self.ftl_game_rect).convert("RGB")
        self.game_image = cv.cvtColor(numpy.array(pil_image), cv.COLOR_RGB2BGR)


if __name__ == "__main__":
    cura = Cura()
