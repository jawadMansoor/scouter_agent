# scouter_agent/application/services/screenshot_scouting_service.py
from __future__ import annotations
import asyncio
from pathlib import Path
from typing import Optional, Tuple

import cv2
from tqdm import tqdm

from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.utilities.coverage_bitmap import CoverageBitmap
from scouter_agent.utilities.object_tile_mapper import get_tile_bbox_for_object

class ScreenshotScoutingService:
    """
    Serpentine traversal service: captures full‑screen frames supplied
    by *capture_device*, saves PNGs, updates a CoverageBitmap, and
    returns the frame so MapExplorer can reuse it for HUD checks.
    """

    def __init__(
        self,
        explorer: MapExplorer,
        tile_geometry: TileGeometry,
        *,
        capture_device,
        coverage_bitmap: CoverageBitmap,
        hud_reader,
        output_dir: Optional[Path] = None,
        hud_crop: Optional[Tuple[int, int, int, int]] = None,
    ) -> None:
        self.explorer         = explorer
        self.tile_geometry    = tile_geometry
        self.capture_device   = capture_device
        self.coverage_bitmap  = coverage_bitmap
        self.hud_reader = hud_reader
        self.output_dir = output_dir or Path("scouter_agent/temp/screenshots")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.hud_crop   = hud_crop
        self.total_tiles = (explorer.row_max - explorer.row_min) * (explorer.col_max - explorer.col_min)
        self._pbar: Optional[tqdm] = None

        # wire callback
        self.explorer.process_tile_fn = self.process_screen

    # ------------------------------------------------------------------
    def set_swipe_scale(self, scale: int) -> None:
        self.explorer.navigator.set_swipe_scale(scale)

    # ------------------------------------------------------------------
    async def run(self) -> None:
        self._pbar = tqdm(total=self.total_tiles, desc="Scouting", ncols=80)
        await self.explorer.explore()
        self._pbar.close()

    # ------------------------------------------------------------------
    async def process_screen(self, est_row: int, est_col: int, left_to_right: bool) -> "np.ndarray":
        """
        Capture screen, save PNG, update coverage bitmap, enqueue progress.
        Returns the captured frame so MapExplorer can do HUD / boundary logic.
        """
        frame = await self.capture_device.grab()
        if frame is None:
            print("[✗] Screen capture failed")
            return frame

        hud = self.hud_reader(frame)
        row_true = est_row # error in row reading is negligible.
        if hud:
            if abs(hud[1] - est_col) < 5:
                col_true = hud[1]
            else:

                if not left_to_right:
                    col_true = est_col-3
                else:
                    col_true = est_col+3
                print(f"hud bad col reading {hud[1]}, using estimated col coords {est_col}{'+3' if left_to_right else '-3'}")
        else:
            if not left_to_right:
                col_true = est_col - 3
            else:
                col_true = est_col + 3
            row_true = est_row  # graceful fallback
            print(f"hud read failed, using estimated coords ({est_row, est_col})")

        print(f"Final detected coords: {row_true, col_true} ")
        # -------- coverage bitmap -------------------------------------
        tiles = get_tile_bbox_for_object(
            row_true, col_true,
        )
        self.coverage_bitmap.mark([(r+row_true,c+col_true) for r,c in tiles])
        # --------------------------------------------------------------

        # save PNG asynchronously to avoid blocking event loop
        fname = self.output_dir / f"screen_{row_true}_{col_true}.png"
        await asyncio.to_thread(cv2.imwrite, str(fname), frame)

        if self._pbar:
            self._pbar.update(1)

        return row_true, col_true
