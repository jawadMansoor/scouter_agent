import pyautogui
import time

class DesktopZoomController:
    def __init__(self, window_title="BlueStacks", scroll_steps=3, scroll_amount=-200, focus_click_offset=(0, 0)):
        """
        Args:
            window_title (str): Title of the BlueStacks window.
            scroll_steps (int): How many times to scroll to ensure proper zoom out.
            scroll_amount (int): Scroll delta per step (negative = scroll down).
            focus_click_offset (tuple): Offset from window center to click for focus.
        """
        self.window_title = window_title
        self.scroll_steps = scroll_steps
        self.scroll_amount = scroll_amount
        self.focus_click_offset = focus_click_offset

    def focus_bluestacks(self):
        window = pyautogui.getWindowsWithTitle(self.window_title)
        if not window:
            raise Exception(f"❌ No window found with title containing '{self.window_title}'")
        window = window[0]
        window.activate()
        time.sleep(0.5)

        center_x = window.left + window.width // 2 + self.focus_click_offset[0]
        center_y = window.top + window.height // 2 + self.focus_click_offset[1]
        pyautogui.moveTo(center_x, center_y)
        pyautogui.click()
        print(f"🖱️ Focused BlueStacks window at ({center_x}, {center_y})")

    def zoom_out(self):
        print("🎯 Calculating game area center...")
        center_x, center_y = self.area_calculator.get_game_center()
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


