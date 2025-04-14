# scouter_agent/infrastructure/ocr_utils.py
import re
import cv2
import numpy as np
import easyocr




ocr_reader = easyocr.Reader(
    ['en'], gpu=False, verbose=False
)

# Regex to capture “123,456” (with or without parentheses / spaces)
coord_regex = re.compile(
    r"[Xx][: ]\s*(-?\d+)\s+[Yy][: ]\s*(-?\d+)"
)

# Your tuned HSV bounds  (H,S,V)
LOWER_HSV = np.array([96, 176, 147], dtype=np.uint8)
UPPER_HSV = np.array([101, 236, 248], dtype=np.uint8)

def _hsv_mask(img_bgr: np.ndarray) -> np.ndarray:
    """Isolate the cyan/teal HUD text and return a clean grayscale image."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)

    # Optional: dilate to connect thin strokes
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # Bitwise‑and keeps only HUD text pixels
    isolated = cv2.bitwise_and(img_bgr, img_bgr, mask=mask)
    gray = cv2.cvtColor(isolated, cv2.COLOR_BGR2GRAY)

    # Improve contrast for OCR
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    return thresh

def read_global_coord(full_img_bgr, crop_box=None):
    """
    Extract (row,col) from HUD text using HSV mask + EasyOCR.
    :param full_img_bgr: full screenshot (BGR)
    :param crop_box: (x1,y1,x2,y2) ROI where HUD sits
    :return: (row,col) ints or None
    """
    if full_img_bgr is None:
        raise FileNotFoundError(f"Couldn’t load image")
    if crop_box:
        x1, y1, x2, y2 = crop_box
        roi = full_img_bgr[y1:y2, x1:x2]
    else:
        h, w = full_img_bgr.shape[:2]
        roi = full_img_bgr[int(0.85*h):, :int(0.35*w)]  # fallback guess

    # Apply HSV isolation
    roi_prepped = _hsv_mask(roi)

    # EasyOCR expects RGB; provide the thresholded mask as a single‑channel image
    result = ocr_reader.readtext(roi_prepped, detail=0, paragraph=False)
    for text in result:
        m = coord_regex.search(text)
        if m:
            try:
                col = int(m.group(1))  # X is column
                row = int(m.group(2))  # Y is row
                return row, col  # return (row, col) order
            except ValueError:
                continue
    return None
