# scouter_agent/infrastructure/ocr_utils.py
import re
import cv2
import numpy as np
import easyocr




ocr_reader = easyocr.Reader(
    ['en'], gpu=False, verbose=False
)

coord_regex_combined = re.compile(
    r"[Xx]\s*[:=]?\s*(-?\d+).*?[Yy]\s*[:=]?\s*(-?\d+)"
)
coord_regex_singleX = re.compile(r"[Xx]\s*[:=]?\s*(-?\d+)")
coord_regex_singleY = re.compile(r"[Yy]\s*[:=]?\s*(-?\d+)")

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

def read_global_coord(full_img_bgr, crop_box=None, *, debug=False):
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
    results = ocr_reader.readtext(roi_prepped, detail=0, paragraph=False)
    if debug:
        for (bbox, text, conf) in results:
            # bbox is a list of 4 points [(x1,y1), …]
            print(f"[OCR‑BOX] {bbox} | '{text}' | conf={conf}")

    texts = [r[1] for r in results]  # strip to just strings

    joined = " ".join(texts)
    m = coord_regex_combined.search(joined)
    if m:
        col, row = int(m.group(1)), int(m.group(2))
        return row, col

    # 2) otherwise look for separate X and Y tokens
    x_val = y_val = None
    for text in results:
        text = text.strip()
        # Remove any non‑digit chars except minus
        digits = re.sub(r"[^0-9-]", "", text)
        if not digits:
            continue
        if text.lower().startswith("x"):
            x_val = int(digits)
        elif text.lower().startswith("y"):
            y_val = int(digits)
        else:
            # fallback: if we haven't got x or y yet, guess by order
            if x_val is None:
                x_val = int(digits)
            elif y_val is None:
                y_val = int(digits)

    if x_val is not None and y_val is not None:
        return y_val, x_val  # (row, col)
    return None
