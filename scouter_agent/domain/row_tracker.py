# scouter_agent/domain/row_tracker.py
from __future__ import annotations
import asyncio
from typing import Callable, Optional, Tuple, Protocol

import numpy as np

from scouter_agent.infrastructure.map_navigator import Direction
# ---------------------------------------------------------------------------

HUDReader = Callable[[ "np.ndarray" ], Optional[Tuple[int, int]]]  # (row,col) or None

class RowTracker:
    """
    Closed‑loop controller that corrects **row** (Y) drift once per serpentine
    row.  Column (X) drift is ignored during traversal for speed.
    """
    def __init__(
        self,
        hud_reader: HUDReader,
        start_row: int,
        start_col: int,
        max_retry: int = 3,
    ) -> None:
        self.hud_reader = hud_reader
        self.row: int   = start_row
        self.col: int   = start_col        # estimate only
        self.max_retry  = max_retry
        self.step: int  = 1                # logical row step size (injected later)

    # ------------------------------------------------------------------
    async def correct_row(
        self,
        frame: "np.ndarray",
        navigator: "MapNavigator",
        on_drift: Optional[Callable[[int], None]] = None,
    ) -> None:
        """Snap to HUD‑row and vertically swipe if |error| ≥ 1 tile."""
        gt: Optional[Tuple[int, int]] = None

        err=np.inf
        for _ in range(self.max_retry):
            if err < 1: break
            for _ in range(self.max_retry):
                gt = self.hud_reader(frame)
                if gt: break
                await asyncio.sleep(0.05)          # OCR blink retry

            if not gt:
                return                            # keep last estimate

            gt_row, _ = gt
            err = gt_row - self.row
            if abs(err) >= 1:
                original = navigator.duration
                navigator.duration = 500      # precise correction
                await navigator.swipe_by_tiles(err, 0, navigator.anchor_map[Direction.DOWN])
                navigator.duration = original
                if on_drift:
                    on_drift(err)

        self.row = gt_row                     # snap even if 0‑error
