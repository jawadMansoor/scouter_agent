import numpy as np

def compute_roi(img: np.ndarray, cfg) -> np.ndarray:
    """
    Compute Region of Interest (ROI) from an image based on config.
    Applies:
      1. manual_roi if provided.
      2. game_res + anchor if available.
      3. Fallback to border_trim percentages.
    """
    if cfg.manual_roi:
        x1, y1, x2, y2 = cfg.manual_roi
        core = img[y1:y2, x1:x2]

    elif cfg.game_res:
        gw, gh = cfg.game_res
        H, W = img.shape[:2]
        anchors = {
            "tl": (0, 0),
            "tr": (W - gw, 0),
            "bl": (0, H - gh),
            "br": (W - gw, H - gh),
        }
        x1, y1 = anchors.get(cfg.game_anchor.lower(), (0, 0))
        core = img[y1:y1 + gh, x1:x1 + gw]

    else:
        l, r, b, t = cfg.border_trim
        H, W = img.shape[:2]
        x1, x2 = int(W * l), int(W * (1 - r))
        y1, y2 = int(H * t), int(H * (1 - b))
        core = img[y1:y2, x1:x2]

    # Apply final top/bottom trimming universally
    l, r, b, t = cfg.border_trim
    H, W = core.shape[:2]
    x1, x2 = int(W * l), int(W * (1 - r))
    y1, y2 = int(H * t), int(H * (1 - b))
    return core[y1:y2, x1:x2]


def get_game_center(window_rect: tuple[int, int, int, int], cfg) -> tuple[int, int]:
    """
    Calculate the center point of the game area within a window.
    """
    X0, Y0, W, H = window_rect

    if cfg.game_res:
        gw, gh = cfg.game_res
        anchors = {
            "tl": (X0, Y0),
            "tr": (X0 + (W - gw), Y0),
            "bl": (X0, Y0 + (H - gh)),
            "br": (X0 + (W - gw), Y0 + (H - gh)),
        }
        x1, y1 = anchors.get(cfg.game_anchor.lower(), (X0, Y0))
        center_x = x1 + gw // 2
        center_y = y1 + gh // 2
    else:
        l, r, b, t = cfg.border_trim
        x1 = X0 + int(W * l)
        x2 = X0 + int(W * (1 - r))
        y1 = Y0 + int(H * t)
        y2 = Y0 + int(H * (1 - b))
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

    return center_x, center_y
