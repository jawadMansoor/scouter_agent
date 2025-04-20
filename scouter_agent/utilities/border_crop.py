# scouter_agent/utilities/border_crop.py
import numpy as np
from typing import Tuple

def crop_rel(
    img: np.ndarray,
    frac_top: float,
    frac_bot: float,
    frac_left: float,
    frac_right: float,
) -> np.ndarray:
    """
    Trim fractional borders from a frame.

    Parameters
    ----------
    frac_* : float
        Fraction of the corresponding dimension to remove.
        0.08 means 8 % of the width/height.

    Example
    -------
    trimmed = crop_rel(frame, 0.20, 0.15, 0.08, 0.08)
    """
    h, w = img.shape[:2]
    top    = int(frac_top  * h)
    bot    = int(frac_bot  * h)
    left   = int(frac_left * w)
    right  = int(frac_right* w)
    return img[top : h - bot, left : w - right, :]
