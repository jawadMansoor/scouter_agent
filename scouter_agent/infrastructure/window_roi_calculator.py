import pyautogui
from scouter_agent.utilities.roi_utils import get_game_center

class WindowAreaCalculator:
    def __init__(self, window_title="BlueStacks", game_res=None, game_anchor="br", border_trim=(0.1, 0.05, 0.05, 0.05)):
        """
        Args:
            window_title (str): Title of the BlueStacks window.
            game_res (tuple): (width, height) of the game area if known.
            game_anchor (str): Anchor point for cropping (tl, tr, bl, br).
            border_trim (tuple): Percentages (left, right, bottom, top) to trim if game_res not set.
        """
        self.window_title = window_title
        self.game_res = game_res
        self.game_anchor = game_anchor.lower()
        self.border_trim = border_trim

    def get_game_center(self):
        window = pyautogui.getWindowsWithTitle(self.window_title)
        if not window:
            raise Exception(f"❌ No window found with title containing '{self.window_title}'")
        window = window[0]

        rect = (window.left, window.top, window.width, window.height)
        return get_game_center(rect, self)
