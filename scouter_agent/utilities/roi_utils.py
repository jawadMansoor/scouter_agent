import pyautogui
import numpy as np


def compute_roi(img: np.ndarray, config) -> np.ndarray:
    """
    Centralized ROI cropping logic.
    """
    if config.manual_roi:
        x1, y1, x2, y2 = config.manual_roi
        core = img[y1:y2, x1:x2]

    elif config.game_res:
        gw, gh = config.game_res
        H, W = img.shape[:2]

        anchor = config.game_anchor.lower()
        if anchor == "tl":
            x1, y1 = 0, 0
        elif anchor == "tr":
            x1, y1 = max(0, W - gw), 0
        elif anchor == "bl":
            x1, y1 = 0, max(0, H - gh)
        elif anchor == "br":
            x1, y1 = max(0, W - gw), max(0, H - gh)
        else:
            raise ValueError(f"Invalid anchor '{anchor}'")

        core = img[y1:y1 + gh, x1:x1 + gw]

    else:
        l, r, b, t = config.border_trim
        H, W, _ = img.shape
        x1, x2 = int(W * l), int(W * (1 - r))
        y1, y2 = int(H * t), int(H * (1 - b))
        core = img[y1:y2, x1:x2]

    # Always apply final border_trim
    l, r, b, t = config.border_trim
    H, W, _ = core.shape
    y1, y2 = int(H * t), int(H * (1 - b))
    x1, x2 = int(W * l), int(W * (1 - r))
    return core[y1:y2, x1:x2]


def get_game_center(window_title: str, config) -> tuple[int, int]:
    window = pyautogui.getWindowsWithTitle(window_title)
    if not window:
        raise Exception(f"❌ No window found with title containing '{window_title}'")
    window = window[0]

    W, H = window.width, window.height
    X0, Y0 = window.left, window.top

    if config.game_res:
        gw, gh = config.game_res
        anchor = config.game_anchor.lower()

        if anchor == "tl":
            x1, y1 = X0, Y0
        elif anchor == "tr":
            x1, y1 = X0 + (W - gw), Y0
        elif anchor == "bl":
            x1, y1 = X0, Y0 + (H - gh)
        elif anchor == "br":
            x1, y1 = X0 + (W - gw), Y0 + (H - gh)
        else:
            raise ValueError(f"Invalid anchor '{anchor}'")

        center_x = x1 + gw // 2
        center_y = y1 + gh // 2
    else:
        l, r, b, t = config.border_trim
        x1 = X0 + int(W * l)
        x2 = X0 + int(W * (1 - r))
        y1 = Y0 + int(H * t)
        y2 = Y0 + int(H * (1 - b))
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

    return center_x, center_y