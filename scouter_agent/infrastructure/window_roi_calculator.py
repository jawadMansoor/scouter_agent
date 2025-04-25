import pyautogui

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

        W, H = window.width, window.height
        X0, Y0 = window.left, window.top

        if self.game_res:
            gw, gh = self.game_res

            if self.game_anchor == "tl":
                x1, y1 = X0, Y0
            elif self.game_anchor == "tr":
                x1, y1 = X0 + (W - gw), Y0
            elif self.game_anchor == "bl":
                x1, y1 = X0, Y0 + (H - gh)
            elif self.game_anchor == "br":
                x1, y1 = X0 + (W - gw), Y0 + (H - gh)
            else:
                raise ValueError(f"Invalid anchor '{self.game_anchor}'")

            center_x = x1 + gw // 2
            center_y = y1 + gh // 2

        else:
            l, r, b, t = self.border_trim
            x1 = X0 + int(W * l)
            x2 = X0 + int(W * (1 - r))
            y1 = Y0 + int(H * t)
            y2 = Y0 + int(H * (1 - b))

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

        return center_x, center_y
