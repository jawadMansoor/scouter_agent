import pyautogui
import time
from typing import Tuple


class ZoomController:
    def __init__(self, screen_center: Tuple[int, int], scroll_amount: int = -500, focus: bool = True):
        """
        Initialize the zoom controller.

        Args:
            screen_center (Tuple[int, int]): The (x, y) screen position of the BlueStacks window center.
            scroll_amount (int): Amount to scroll; negative scrolls down (zoom out).
            focus (bool): If True, clicks on the window to bring it to focus before zooming.
        """
        self.screen_center = screen_center
        self.scroll_amount = scroll_amount
        self.focus = focus

    def zoom_out(self, delay: float = 0.1):
        """
        Perform a Ctrl + Scroll Down gesture at the BlueStacks window center.

        Args:
            delay (float): Delay between key events.
        """
        x, y = self.screen_center
        pyautogui.moveTo(x, y)
        time.sleep(delay)

        if self.focus:
            pyautogui.click()
            time.sleep(delay)

        pyautogui.keyDown('ctrl')
        time.sleep(delay)

        pyautogui.scroll(self.scroll_amount)  # negative = scroll down (zoom out)
        time.sleep(delay)

        pyautogui.keyUp('ctrl')
