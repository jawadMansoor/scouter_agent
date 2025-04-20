# scouter_agent/infrastructure/map_explorer.py
from __future__ import annotations
import asyncio
from typing import Callable, Optional, Iterable, Tuple

from scouter_agent.infrastructure.map_navigator import MapNavigator, Direction
from scouter_agent.domain.row_tracker import RowTracker

# ---------------------------------------------------------------------------

class MapExplorer:
    """
    Serpentine iterator that walks the map in navigator.swipe_scale steps.

    Closed‑loop policy:
      • We ignore column (X) drift inside a row for speed.
      • At the end of each row we call RowTracker.correct_row() to snap Y.
      • If live HUD‑column crosses map boundary, we break the row early.
    """

    def __init__(
        self,
        navigator: MapNavigator,
        rows_range: Tuple[int,int],
        columns_range: Tuple[int,int],
        process_tile_fn: Optional[Callable[[int, int], "np.ndarray"]] = None,
        row_tracker: RowTracker | None = None,
        capture_device: "CaptureDevice | None" = None,
        row_step: int = 3,
    ) -> None:
        self.navigator        = navigator
        self.row_min, self.row_max = rows_range
        self.col_min, self.col_max = columns_range
        self.row_step = max(1, row_step)
        self.process_tile_fn  = process_tile_fn
        self.row_tracker      = row_tracker            # injected from caller
        self.capture          = capture_device         # for HUD read at row end

    # ------------------------------------------------------------------
    @property
    def horiz_step(self) -> int:
        """Horizontal stride = navigator.swipe_scale"""
        return max(1, self.navigator.swipe_scale)

    # ------------------------------------------------------------------
    async def explore(self):
        cur_row = self.row_tracker.row
        left_to_right = True

        while cur_row < self.row_max:
            await self._traverse_row(cur_row, left_to_right)
            cur_row += self.row_step
            self.row_tracker.row = cur_row

            if cur_row < self.row_max:
                await self.navigator.swipe(Direction.DOWN)
                # Grab frame *after* vertical swipe for row correction
                frame = await self.capture.grab()
                await self.row_tracker.correct_row(
                    frame, self.navigator,
                    on_drift=lambda e: print(f"[ROW‑DRIFT] {e:+d} tiles")
                )
            left_to_right = not left_to_right

    # ------------------------------------------------------------------
    async def _traverse_row(self, base_row: int, left_to_right: bool):
        cols: Iterable[int] = range(self.col_min, self.col_max, self.horiz_step)
        if not left_to_right:
            cols = reversed(list(cols))

        direction = Direction.RIGHT if left_to_right else Direction.LEFT

        for base_col in cols:
            if self.process_tile_fn:
                hud_row, hud_col = await self.process_tile_fn(base_row, base_col)
                base_row, base_col = hud_row, hud_col
                # -------- boundary check --------------------------------
                if hud_row and hud_col:
                    if (
                        ( left_to_right and hud_col >= self.col_max) or
                        ( not left_to_right and hud_col <= self.col_min)
                    ):
                        print(f"[ROW‑END] HUD col={hud_col} → break")
                        break
                # ---------------------------------------------------------

            # another horizontal swipe needed?
            end_of_row = (
                    (left_to_right and base_col + self.horiz_step >= self.col_max) or
                    (not left_to_right and base_col <= self.col_min)
            )
            if not end_of_row:
                await self.navigator.swipe(direction)
