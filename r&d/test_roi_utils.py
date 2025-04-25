# test_roi_utils.py
import cv2
from scouter_agent.utilities.roi_utils import compute_roi
from scouter_agent.infrastructure.capture_devices import CaptureConfig

cfg = CaptureConfig(
    game_res=(600, 1054),
    game_anchor="br",
    border_trim=(0.08, 0.16, 0.05, 0.1)
)

img = cv2.imread("path/to/sample_bluestacks_screenshot.png")
roi = compute_roi(img, cfg)
cv2.imshow("Computed ROI", roi)
cv2.waitKey(0)
cv2.destroyAllWindows()
