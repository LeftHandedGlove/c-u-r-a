import os
import time
import subprocess
import win32gui
from PIL import ImageGrab
import cv2 as cv
import numpy
import pyautogui
import shutil
import pytesseract
import re
from cv2.typing import MatLike
import sqlite3


top_level_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class GameImages:
    @staticmethod
    def __get_image(image_name:str):
        return cv.imread(os.path.join(top_level_dir, "Images", f"{image_name}.png"))

    LANG_SELECT_ENG = __get_image("language_select_english")
    SHIP_SEL_EASY = __get_image("ship_select_easy")
    SHIP_SEL_START = __get_image("ship_select_start")
    TITLE_CONFIRM_OVERRIDE = __get_image("title_screen_confirm_override_save")
    TITLE_NEW_GAME = __get_image("title_screen_new_game")
    TITLE_OVERRIDE_SAVE = __get_image("title_screen_override_save")


class EventMemory:
    def __init__(self):
        self.db_conn = sqlite3.connect(os.path.join(top_level_dir, "event_memory.db"))
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("CREATE TABLE events(event_text, options)")


class GameEvent:
    def __init__(self, event_text:str):
        # Check if this is just a placeholder
        if len(event_text) == 0:
            return
        # If not then fill out useful info
        self.pre_options_text = event_text[:event_text.index("\n\n1. ")]
        all_options_text = event_text[event_text.index("\n\n1. "):]
        options_matcher = re.compile(r"\n\d+. .*")
        self.options_text = []
        for match in options_matcher.finditer(all_options_text):
            self.options_text.append(match.string.strip())
            


class GameWindow():
    def __init__(self):
        self.ftl_game_dir = os.path.join(top_level_dir, "flt_game_files")
        self.ftl_process = None
        self.ftl_hwnd = 0
        self.ftl_game_rect = (0, 0, 0, 0)
        self.image_dir = os.path.join(top_level_dir, "images")
        self.game_image = GameImages.SHIP_SEL_EASY
        self.mouse_speed = 0.2

    def launch_ftl(self):
        # The game makes some files when it runs so we run the game 
        # from a known directory so it doesn't pollute anything
        shutil.rmtree(self.ftl_game_dir, ignore_errors=True)
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
        self.ftl_game_rect = (win_left + 8, win_top + 0, win_right - 8, win_bottom - 8)
        # Center the mouse on the window
        pyautogui.moveTo(win_width//2, win_height//2, self.mouse_speed)

    def read_event_text(self) -> GameEvent:
        event_image = self.__crop_game_image(340, 190, 590, 350)
        all_event_text = str(pytesseract.image_to_string(event_image, lang="eng"))
        game_event = GameEvent(all_event_text)
        return game_event

    def wait_for_image(self, image:MatLike, timeout:int = 0) -> tuple[bool, tuple[int, int]]:
        start_time = time.time()
        while True:
            if (timeout != 0) and ((time.time() - start_time) > timeout):
                return False, (-1, -1)
            self.grab_game_image()
            found, center = self.look_for_image(image)
            if found:
                return True, center
            
    def wait_for_image_then_click(self, image:MatLike, timeout:int = 0) -> tuple[bool, tuple[int, int]]:
        found, center = self.wait_for_image(image, timeout)
        if found:
            pyautogui.moveTo(center[0], center[1], self.mouse_speed)
            pyautogui.click()
        return found, center
            
    def look_for_image(self, image:MatLike, confidence:float = 0.99) -> tuple[bool, tuple[int, int]]:
        height, width, _ = image.shape
        res = cv.matchTemplate(self.game_image, image, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        if max_val > confidence:
            center = (max_loc[0] + int(width / 2), max_loc[1] + int(height / 2))
            return True, center
        return False, (-1, -1)
    
    def click_on_image(self, image):
        found, center = self.look_for_image(image)
        if found:
            pyautogui.moveTo(center[0], center[1], self.mouse_speed)
            pyautogui.click()

    def grab_game_image(self):
        pil_image = ImageGrab.grab(self.ftl_game_rect).convert("RGB")
        self.game_image = cv.cvtColor(numpy.array(pil_image), cv.COLOR_RGB2BGR)

    def __crop_game_image(self, left, top, width, height):
        self.grab_game_image()
        return self.game_image[top:top+height, left:left+width].copy()
    
