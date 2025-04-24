# scouter_agent/infrastructure/ocr_utils.py
import re
import cv2
import numpy as np
import easyocr
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



ocr_reader = easyocr.Reader(
    ['en'], gpu=True, verbose=False,
)

coord_regex_combined = re.compile(
    r"[Xx]\s*[:=]?\s*(-?\d+).*?[Yy]\s*[:=]?\s*(-?\d+)"
)
coord_regex_singleX = re.compile(r"[Xx]\s*[:=]?\s*(-?\d+)")
coord_regex_singleY = re.compile(r"[Yy]\s*[:=]?\s*(-?\d+)")

# Your tuned HSV bounds  (H,S,V)
LOWER_HSV = np.array([94 , 100, 100], dtype=np.uint8)
UPPER_HSV = np.array([100, 236, 246], dtype=np.uint8)

def _hsv_mask(img_bgr: np.ndarray) -> np.ndarray:
    """Isolate the cyan/teal HUD text and return a clean grayscale image."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)

    # Optional: dilate to connect thin strokes
    # kernel = np.ones((3, 3), np.uint8)
    # mask = cv2.dilate(mask, kernel, iterations=1)

    # Apply Gaussian blur


    # Bitwise‑and keeps only HUD text pixels
    isolated = cv2.bitwise_and(img_bgr, img_bgr, mask=mask)
    # blurred_isolated = cv2.GaussianBlur(isolated, (3, 3), 0)
    gray = cv2.cvtColor(isolated, cv2.COLOR_BGR2GRAY)
    # blurred_gray = cv2.GaussianBlur(gray, (3, 3), 0)
    # Improve contrast for OCR
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    # blurred_thresh = cv2.GaussianBlur(gray, (3, 3), 0)
    return isolated, gray, thresh

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
        roi = full_img_bgr[-185:-145, -312:-142, :]  # fallback guess

    # Apply HSV isolation
    isolated, gray, thresh = _hsv_mask(roi)
    roi_prepped = thresh
    roi_x_coord = roi_prepped[:,22:100]
    roi_y_coord =  roi_prepped[:,120:]

    # EasyOCR expects RGB; provide the threshold mask as a single‑channel image
    results = ocr_reader.readtext(roi_prepped, detail=0, paragraph=False,
                                  allowlist="X:Y123456789")
    if debug:
        for (bbox, text, conf) in results:
            # bbox is a list of 4 points [(x1,y1), …]
            print(f"[OCR‑BOX] {bbox} | '{text}' | conf={conf}")

    # look for separate X and Y tokens
    x_val = y_val = None
    for text in results:
        text = text.strip()
        # Remove any non‑digit chars
        digits = re.sub(r"[^0-9]", "", text)
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
        if y_val >= 110 or x_val >= 110:
            print("anomalous reading of HUD")
        return y_val, x_val  # (row, col)
    else:
        print("couldn't read HUD coord")
        #read x and y coordinates separately
        result_x = ocr_reader.readtext(roi_x_coord, detail=0, paragraph=False,
                                  allowlist="123456789")
        result_y = ocr_reader.readtext(roi_y_coord, detail=0, paragraph=False,
                                       allowlist="123456789")
        if x_val is not None and y_val is not None:
            y_val = int(result_y)
            x_val = int(result_x)
            return y_val, x_val
    return None
