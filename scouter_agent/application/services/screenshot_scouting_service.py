from pathlib import Path
from typing import Optional
import asyncio
import cv2
from tqdm import tqdm

from scouter_agent.infrastructure.ocr_utils import read_global_coord
from scouter_agent.object_recognizer.detect_objects import capture_fullscreen
from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.infrastructure.map_navigator import Direction


class ScreenshotScoutingService:
    """Traverse the map, capture full‑screen images, and periodically correct drift
    by reading the HUD coordinate and issuing corrective swipes.
    """

    def __init__(
        self,
        explorer: MapExplorer,
        tile_geometry: TileGeometry,
        output_dir: Optional[Path] = None,
        hud_crop: Optional[tuple[int, int, int, int]] = None,
        sanity_interval: int = 100,
    ) -> None:
        self.explorer = explorer
        self.tile_geometry = tile_geometry
        self.output_dir = output_dir or Path("scouter_agent/temp/screenshots")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.hud_crop = hud_crop
        self.sanity_interval = max(1, sanity_interval)
        self.step_counter = 0
        self.total_tiles = explorer.total_rows * explorer.total_columns

        # progress bar is created lazily in run()
        self._pbar: Optional[tqdm] = None

        # inject callback
        self.explorer.process_tile_fn = self.process_tile

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def set_swipe_scale(self, scale: int) -> None:
        """Expose swipe‑scale tuning to main.py"""
        self.explorer.navigator.set_swipe_scale(scale)

    # ------------------------------------------------------------------
    # Core coroutine
    # ------------------------------------------------------------------
    async def run(self) -> None:
        """Kick off serpentine exploration with progress bar."""
        self._pbar = tqdm(total=self.total_tiles, desc="Scouting", ncols=80)
        await self.explorer.explore()
        self._pbar.close()

    # ------------------------------------------------------------------
    async def process_tile(self, est_row: int, est_col: int):
        """Capture screen, correct drift if needed, save image, update bar."""
        self.step_counter += 1
        image = capture_fullscreen()
        if image is None:
            print("[✗] Screen capture failed"); return

        row, col = est_row, est_col  # default to estimate

        # periodic HUD sanity‑check
        if self.step_counter % self.sanity_interval == 0:
            gt = read_global_coord(image, self.hud_crop)
            print("Checking swipe drift")
            print(f"  GT: {gt} | Est: ({est_row}, {est_col})")
            if gt:
                gt_row, gt_col = gt
                err = abs(gt_row - est_row) + abs(gt_col - est_col)
                print(f"  Error: {err} tiles")
                if err >= 1:
                    await self._correct_camera(gt_row, gt_col, est_row, est_col)
                    row, col = gt_row, gt_col
                    print(f"[✔] Corrective swipe applied (err={err} tiles)")

        # Save screenshot
        fname = self.output_dir / f"screen_{row}_{col}.png"
        cv2.imwrite(str(fname), image)

        # progress bar
        if self._pbar is not None:
            self._pbar.update(1)
            await asyncio.sleep(0)  # yield so tqdm refreshes

    # ------------------------------------------------------------------
    async def _correct_camera(self, gt_row: int, gt_col: int, est_row: int, est_col: int):
        """Physically swipe the map so HUD center aligns with ground truth."""
        delta_row = gt_row - est_row  # positive → move down in tile space
        delta_col = gt_col - est_col  # positive → move right in tile space

        # Use navigator's low‑level swipe_by_tiles from an arbitrary anchor
        anchor = self.explorer.navigator.anchor_map[Direction.RIGHT]
        await self.explorer.navigator.swipe_by_tiles(delta_col, delta_row, anchor)

        # Override explorer cursor so traversal continues from GT
        if hasattr(self.explorer, "override_current_position"):
            self.explorer.override_current_position(gt_row, gt_col)
