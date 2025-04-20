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
    async def process_screen(self, est_row: int, est_col: int) -> "np.ndarray":
        """
        Capture screen, save PNG, update coverage bitmap, enqueue progress.
        Returns the captured frame so MapExplorer can do HUD / boundary logic.
        """
        frame = await self.capture_device.grab()
        if frame is None:
            print("[✗] Screen capture failed")
            return frame

        hud = self.hud_reader(frame)
        if hud:
            row_true, col_true = hud
        else:
            row_true, col_true = est_row, est_col  # graceful fallback

        # -------- coverage bitmap -------------------------------------
        tiles = get_tile_bbox_for_object(
            pixel_bbox=(0, 0, frame.shape[1], frame.shape[0]),
            geometry=self.tile_geometry,
        )
        self.coverage_bitmap.mark([(r+row_true,c+col_true) for r,c in tiles])
        # --------------------------------------------------------------

        # save PNG asynchronously to avoid blocking event loop
        fname = self.output_dir / f"screen_{row_true}_{col_true}.png"
        await asyncio.to_thread(cv2.imwrite, str(fname), frame)

        if self._pbar:
            self._pbar.update(1)

        return row_true, col_true
