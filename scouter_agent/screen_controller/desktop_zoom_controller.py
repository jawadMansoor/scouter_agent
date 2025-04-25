import pyautogui
import time
from scouter_agent.utilities.roi_utils import get_game_center


class DesktopZoomController:
    def __init__(self, config, scroll_steps=3, scroll_amount=-200):
        self.config = config
        self.window_title = config.title
        self.scroll_steps = scroll_steps
        self.scroll_amount = scroll_amount

    def zoom_out(self):
        print("🎯 Calculating game area center via ROI utils...")
        center_x, center_y = get_game_center(self.window_title, self.config)
        pyautogui.moveTo(center_x, center_y)
        pyautogui.click()
        time.sleep(0.3)

        print(f"🔍 Performing zoom out at ({center_x}, {center_y})...")
        pyautogui.keyDown('ctrl')
        for _ in range(self.scroll_steps):
            pyautogui.scroll(self.scroll_amount)
            time.sleep(0.2)
        pyautogui.keyUp('ctrl')
        print("✅ Zoom out completed.")

