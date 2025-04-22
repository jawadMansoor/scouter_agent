"""
Thread‑affine window/monitor capture that is safe for repeated grabs on Windows.

▶  Key points
    • mss is created *inside* the capture thread ⇒ no GDI context leak.
    • Public API is synchronous (.grab()) and asynchronous (await capturer.grab()).
    • Automatically crops to the Bluestacks game rectangle (or full monitor fallback).
"""

from __future__ import annotations
import threading, queue, time, asyncio
from dataclasses import dataclass
from typing import Optional
import pygetwindow as gw
import win32con, win32gui


import numpy as np
import cv2
import mss
try:
    import pygetwindow as gw          # lightweight window enumeration
except ImportError:
    gw = None                         # still works in “whole‑monitor” mode

# ---------------------------------------------------------------------------#
@dataclass(slots=True)
class CaptureConfig:
    title: str = "BlueStacks"         # window title substring
    game_res: tuple[int, int] | None = (1280, 720)  # (w,h) of in‑game canvas
    game_anchor: str = "br"  # tl / tr / bl / br
    border_trim: tuple[float, float, float, float] = (0.00, 0.00, 0.0, 0.00)  # pct left, right, bottom, top
    manual_roi: tuple[int, int, int, int] | None = None

# ---------------------------------------------------------------------------#
class _Worker(threading.Thread):
    def __init__(self, monitor: dict, out_q: "queue.Queue[np.ndarray]"):
        super().__init__(daemon=True, name="WindowCaptureWorker")
        self.monitor   = monitor
        self.out_q     : "queue.Queue[np.ndarray]" = out_q
        self._req_q    : "queue.Queue[None]"       = queue.Queue(maxsize=1)
        self._shutdown_evt: threading.Event        = threading.Event()

    # –– public API –– #
    def stop(self) -> None:
        self._shutdown_evt.set()
        self._req_q.put_nowait(None)          # unblock if waiting

    def request_frame(self) -> None:
        try:
            self._req_q.put_nowait(None)      # drop if still busy
        except queue.Full:
            pass

    # –– thread loop –– #
    def run(self) -> None:
        with mss.mss() as sct:
            while not self._shutdown_evt.is_set():
                try:
                    self._req_q.get(timeout=0.5)
                except queue.Empty:
                    continue
                try:
                    raw = np.asarray(sct.grab(self.monitor))
                    self.out_q.put_nowait(raw)
                except Exception as e:
                    self.out_q.put_nowait(e)


# ---------------------------------------------------------------------------#
class WindowCapture:
    """
    Primary user‑facing class.

    Usage (sync):
        cap = WindowCapture()
        frame_bgra = cap.grab()          # returns BGRA uint8
        cap.close()

    Usage (async):
        cap = WindowCapture()
        frame = await cap.grab_async()
    """

    def __init__(self, cfg: Optional[CaptureConfig] = None):
        self.cfg      = cfg or CaptureConfig()
        self.out_q    : "queue.Queue[np.ndarray]" = queue.Queue(maxsize=1)
        self.monitor  = self._resolve_monitor()
        self.worker   = _Worker(self.monitor, self.out_q)
        self.worker.start()

    # ---- public -----------------------------------------------------------#
    def grab(self) -> np.ndarray:
        """Blocking frame fetch (returns **copy** in BGR)."""
        self.worker.request_frame()
        result = self.out_q.get()
        if isinstance(result, Exception):
            raise result
        frame = result[:, :, :3]                 # discard alpha
        return self._crop_if_needed(cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR))

    async def grab_async(self) -> np.ndarray:
        return await asyncio.to_thread(self.grab)

    def close(self) -> None:
        self.worker.stop()
        self.worker.join(timeout=2)

    # ---- helpers ----------------------------------------------------------#
    def _resolve_monitor(self) -> dict:
        """
        Returns an MSS monitor dict.  Prefers a visible window whose title
        contains cfg.title; otherwise falls back to primary monitor (#1).
        """
        if gw:
            wins = [w for w in gw.getWindowsWithTitle(self.cfg.title) if w.visible]
            if wins:
                w = wins[0]
                print(f"[WindowCapture] Capturing window '{w.title}' at "
                      f"{w.left},{w.top} {w.width}×{w.height}")
                return {"top": w.top, "left": w.left,
                        "width": w.width, "height": w.height}
        print("[WindowCapture] No window match; falling back to primary monitor.")
        with mss.mss() as sct:
            return sct.monitors[1]               # full‑screen

    def _crop_if_needed(self, img: np.ndarray) -> np.ndarray:
        """
        1. If manual_roi  → use it.
        2. Else if game_res is set → take the w×h block anchored as requested.
        3. Else fall back to percentage border_trim.
        After that, still apply border_trim (top/bottom) for HUD & bottom bar.
        """
        if self.cfg.manual_roi:
            x1, y1, x2, y2 = self.cfg.manual_roi
            core = img[y1:y2, x1:x2]

        elif self.cfg.game_res:
            gw, gh = self.cfg.game_res
            H, W = img.shape[:2]

            anchor = self.cfg.game_anchor.lower()
            if anchor == "tl":
                x1, y1 = 0, 0
            elif anchor == "tr":
                x1, y1 = max(0,W - gw), 0
            elif anchor == "bl":
                x1, y1 = 0, max(0,H - gh)
            elif anchor == "br":
                x1, y1 = max(0,W - gw), max(0,H - gh)
            else:
                raise ValueError(f"bad anchor {anchor!r}")

            core = img[y1:y1 + gh, x1:x1 + gw]

        else:
            # last‑resort % crop across all four borders
            l, r, b, t = self.cfg.border_trim
            H, W, _ = img.shape
            x1, x2 = int(W * l), int(W * (1 - r))
            y1, y2 = int(H * t), int(H * (1 - b))
            core = img[y1:y2, x1:x2]

        # still strip variable top/bottom UI (percentages usually work)
        l, r, b, t = self.cfg.border_trim
        H, W, _ = core.shape
        y1, y2 = int(H * t), int(H * (1 - b))
        x1, x2 = int(W * l), int(W * (1 - r))
        return core[y1:y2, x1:x2]


# ---------------------------------------------------------------------------#
# convenience async wrapper -------------------------------------------------#
class AsyncWindowCapture:
    def __init__(self, cfg: Optional[CaptureConfig] = None):
        self._cap = WindowCapture(cfg)

    # ------------------------------------------------------------------
    # Helpers                                                             #
    # ------------------------------------------------------------------
    @ property
    def _hwnd(self) -> Optional[int]:
        """Return the window handle (or None if not found)."""
        if gw is None:
            return None
        wins = [w for w in gw.getWindowsWithTitle(self._cap.cfg.title) if w.visible]
        return wins[0]._hWnd if wins else None

    def _ensure_topmost(self) -> None:
        """Keep the game window above other windows to avoid partial grabs."""

        hwnd = self._hwnd
        if hwnd:
            flags = (win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                     win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, flags)

    async def grab(self) -> np.ndarray:
        """Async one‑shot capture (returns BGR image)."""
        self._ensure_topmost()
        # WindowCapture.grab_async() already requests a frame + waits for it
        return await self._cap.grab_async()

    def close(self) -> None:
        self._cap.close()
