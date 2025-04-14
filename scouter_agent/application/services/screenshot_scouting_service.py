from pathlib import Path
from typing import Optional, Tuple
import asyncio
import cv2
from tqdm import tqdm

from scouter_agent.infrastructure.ocr_utils import read_global_coord
from scouter_agent.object_recognizer.detect_objects import capture_fullscreen
from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.infrastructure.map_navigator import Direction


class ScreenshotScoutingService:
    """Serpentine traversal + full‑screen capture with periodic drift correction."""

    def __init__(
        self,
        explorer: MapExplorer,
        tile_geometry: TileGeometry,
        output_dir: Optional[Path] = None,
        hud_crop: Optional[Tuple[int, int, int, int]] = None,
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

        # bind callback
        self.explorer.process_tile_fn = self.process_screen
        self._pbar: Optional[tqdm] = None

    # ------------------------------------------------------------------
    def set_swipe_scale(self, scale: int) -> None:
        self.explorer.navigator.set_swipe_scale(scale)

    # ------------------------------------------------------------------
    async def run(self) -> None:
        self._pbar = tqdm(total=self.total_tiles, desc="Scouting", ncols=80)
        await self.explorer.explore()
        self._pbar.close()

    # ------------------------------------------------------------------
    async def process_screen(self, est_row: int, est_col: int):
        """Capture, optional HUD correction, save image, update bar."""
        self.step_counter += 1
        image = capture_fullscreen()
        if image is None:
            print("[✗] Screen capture failed"); return

        row, col = est_row, est_col

        if self.step_counter % self.sanity_interval == 0:
            gt = read_global_coord(image, self.hud_crop)
            if gt:
                gt_row, gt_col = gt
                err = abs(gt_row - est_row) + abs(gt_col - est_col)
                print(f"Error: {err}, {est_row-gt_row}, {est_col-gt_col}")
                if err >= 1:
                    await self._correct_camera(gt_row, gt_col, est_row, est_col)
                    row, col = gt_row, gt_col
                    print(f"[✔] Corrected drift (err={err} tiles)")

        fname = self.output_dir / f"screen_{row}_{col}.png"
        cv2.imwrite(str(fname), image)

        if self._pbar:
            self._pbar.update(1)
            await asyncio.sleep(0)

    # ------------------------------------------------------------------
    async def _correct_camera(self, gt_row: int, gt_col: int, est_row: int, est_col: int):
        """Swipe exactly the delta in **one‑tile units**, independent of user stride."""
        d_row = gt_row - est_row   # + → down in tile space
        d_col = gt_col - est_col   # + → right in tile space
        if d_row == 0 and d_col == 0:
            return

        navigator = self.explorer.navigator
        original_scale = navigator.swipe_scale
        navigator.set_swipe_scale(1)          # force 1‑tile precision

        anchor = navigator.anchor_map[Direction.RIGHT]  # any anchor works
        await navigator.swipe_by_tiles(d_row, d_col, anchor)

        navigator.set_swipe_scale(original_scale)       # restore user stride
        self.explorer.override_current_position(gt_row, gt_col)
