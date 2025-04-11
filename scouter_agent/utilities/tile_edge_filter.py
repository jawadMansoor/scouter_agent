import cv2
import numpy as np


def isolate_tile_edges(image: np.ndarray) -> np.ndarray:
    """
    Filters image to detect whitish tile border lines using relaxed HSV thresholds,
    then applies Canny edge detection.
    """
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Loosened HSV thresholds for broader white detection
    lower_white = np.array([0, 10, 160])
    upper_white = np.array([30, 80, 255])

    # Apply mask
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # No morphology to preserve thin lines
    masked = cv2.bitwise_and(image, image, mask=mask)
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    return edges

