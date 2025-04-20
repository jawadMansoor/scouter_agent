# capture_devices.py
"""CaptureDevice abstractions and concrete back‑ends.

Fix 2025‑04‑16: **WindowCapture** now creates its own `mss` instance *inside* the
worker thread to avoid Win32 handle errors when the grab call runs in a
`asyncio.to_thread` worker.  This resolves the AttributeError
`'_thread._local' object has no attribute 'srcdc'` the user observed.
"""
from __future__ import annotations

import asyncio
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple
from scouter_agent.utilities.border_crop import crop_rel

import numpy as np

# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------
class CaptureDevice(ABC):
    """Minimal contract any capture backend must satisfy."""

    @abstractmethod
    async def grab(self) -> np.ndarray:  # returns BGR image
        """Capture one frame and return it as a NumPy array (dtype=uint8)."""

    async def close(self):
        """Optional clean‑up hook (override if needed)."""
        pass

# ---------------------------------------------------------------------------
# ADB implementation (wrapper around existing capture_streaming logic)
# ---------------------------------------------------------------------------
from scouter_agent.infrastructure.adb.capture_streaming import (
    CaptureConfig as _ADBConfig,
    capture_frame as _adb_capture_frame,
)

class ADBCapture(CaptureDevice):
    def __init__(self, cfg: Optional[_ADBConfig] = None):
        self.cfg = cfg or _ADBConfig()

    async def grab(self) -> np.ndarray:
        return await _adb_capture_frame(self.cfg)

# ---------------------------------------------------------------------------
# Window‑capture implementation (Windows only)
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    import mss
    import cv2
    import win32gui, win32con

    @dataclass(slots=True)
    class WindowCaptureConfig:
        window_title: str = "BlueStacks App Player"   # substring match
        crop: Optional[Tuple[int, int, int, int]] = None  # (left, top, right, bottom)


    class WindowCapture:
        """
        Host‑side grabber for BlueStacks that returns *only* the game viewport
        (no ads strip, no window chrome).  The default crop works for a
        1920×1080 monitor with BlueStacks 1280×720 game area centred; adjust
        OFF_X / OFF_Y if your layout differs.
        """
        VIEW_W, VIEW_H = 720, 1280
        OFF_X, OFF_Y = 482, 440  # ← tune once with a screenshot

        def __init__(self, window_title: str = "BlueStacks App Player") -> None:
            import win32gui
            self.hwnd = win32gui.FindWindow(None, window_title)
            if not self.hwnd:
                raise RuntimeError(f"Window '{window_title}' not found")
            # cache monitor rect for speed
            import win32gui
            l, t, r, b = win32gui.GetClientRect(self.hwnd)
            self.win_left, self.win_top = win32gui.ClientToScreen(self.hwnd, (l, t))

        # ------------------------------------------------------------------
        @staticmethod
        def _find_window(title_substr: str):
            def enum_handler(hwnd, result):
                if win32gui.IsWindowVisible(hwnd):
                    text = win32gui.GetWindowText(hwnd)
                    if title_substr.lower() in text.lower():
                        result.append(hwnd)
            found = []
            win32gui.EnumWindows(enum_handler, found)
            return found[0] if found else 0

        @staticmethod
        def _hwnd_to_bbox(hwnd):
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            # ClientRect is relative; map to screen
            pt = win32gui.ClientToScreen(hwnd, (left, top))
            left_screen, top_screen = pt
            width = right - left
            height = bottom - top
            return {"left": left_screen, "top": top_screen, "width": width, "height": height}

        # ------------------------------------------------------------------
        async def grab(self) -> np.ndarray:
            # MSS must be instantiated in the same OS thread that calls grab().
            frame = await asyncio.to_thread(self._capture_sync)
            return frame

        def _capture_sync(self):
            # 1) push BlueStacks above all other windows
            win32gui.SetWindowPos(
                self.hwnd,
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )

            with mss.mss() as sct:
                mon = {
                    "top": self.win_top + self.OFF_Y,
                    "left": self.win_left + self.OFF_X,
                    "width": self.VIEW_W,
                    "height": self.VIEW_H,
                }
                raw = sct.grab(mon)
                img = np.array(raw)[:, :, :3]

                # 2) optionally drop the TOPMOST flag so normal stacking resumes
            win32gui.SetWindowPos(
                self.hwnd,
                win32con.HWND_NOTOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
            frame = crop_rel(img, 0.20, 0.15, 0.08, 0.08)
            return frame
else:
    class WindowCapture(CaptureDevice):  # type: ignore
        def __init__(self, *a, **kw):
            raise NotImplementedError("WindowCapture only supported on Windows hosts")

# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------

def get_default_capture() -> CaptureDevice:
    """Return WindowCapture on Windows desktops, else ADBCapture."""
    if sys.platform == "win32":
        try:
            return WindowCapture()
        except Exception as e:
            print("[WARN] WindowCapture unavailable – falling back to ADB:", e)
    return ADBCapture()
