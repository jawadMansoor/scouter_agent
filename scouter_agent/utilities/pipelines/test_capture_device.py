from scouter_agent.infrastructure.capture_devices import WindowCapture, CaptureConfig
import cv2

cfg = CaptureConfig(
        game_res=(600, 1054),
        game_anchor="br",          # bottom‑right
        border_trim=(0.08, 0.16, 0.05, 0.1)   # l,r,b,t
)

cap = WindowCapture(cfg)
frame = cap.grab()          # <‑‑ 720×1280 w/out ad bar
cv2.imwrite("../../../debug.png", frame)
cap.close()
