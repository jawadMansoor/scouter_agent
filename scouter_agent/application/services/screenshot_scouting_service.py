from scouter_agent.infrastructure.screen_capture import capture_fullscreen
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.infrastructure.map_navigator import MapNavigator
from pathlib import Path
import shutil
import cv2


class ScreenshotScoutingService:
    def __init__(self, explorer: MapExplorer, tile_geometry: TileGeometry, output_dir: Path = None):
        self.explorer = explorer
        self.tile_geometry = tile_geometry
        self.output_dir = output_dir or Path("scouter_agent/temp/screenshots")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.explorer.process_tile_fn = self.process_tile

    def set_swipe_scale(self, scale: int):
        self.explorer.navigator.set_swipe_scale(scale)

    async def run(self):
        await self.explorer.explore()

    async def process_tile(self, row: int, col: int):
        pixel_coord = self.tile_geometry.tile_to_pixel((row, col))
        image = capture_fullscreen()
        if image is None:
            raise RuntimeError("Failed to capture screen from device.")

        filename = f"screen_{row}_{col}.png"
        save_path = self.output_dir / filename
        cv2.imwrite(str(save_path), image)
        print(f"[✓] Saved screenshot at tile ({row}, {col}) to {save_path}")
