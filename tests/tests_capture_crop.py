import numpy as np, cv2
from scouter_agent.infrastructure.capture_devices import WindowCapture, CaptureConfig

def test_crop_produces_expected_shape():
    cfg = CaptureConfig(game_res=(600, 1054), game_anchor="br",
                        border_trim=(0.08, 0.16, 0.05, 0.10))
    cap = WindowCapture(cfg)
    frame = cap.grab()
    h, w = frame.shape[:2]
    # ~10 % top & 5 % bottom trimmed off 1054 ⇒ 848 ish
    assert abs(w - 600)  < 2
    assert 820 < h < 880
    cap.close()
