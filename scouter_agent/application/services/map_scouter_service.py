import os
from pathlib import Path
import numpy as np
import cv2
from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.object_recognizer.detect_objects import capture_fullscreen


class ScreenshotScoutingService:
    def __init__(self, explorer: MapExplorer, tile_geometry: TileGeometry, output_dir: Path = None):
        """
        Captures full-screen screenshots while navigating the map.

        :param explorer: Instance of MapExplorer to drive serpentine traversal.
        :param tile_geometry: TileGeometry instance for tile↔pixel transformation.
        :param output_dir: Directory to store screenshots. Defaults to ./scouter_agent/temp/screens/
        """
        self.explorer = explorer
        self.tile_geometry = tile_geometry
        self.explorer.process_tile_fn = self.process_tile

        self.output_dir = output_dir or Path(__file__).resolve().parent.parent.parent / "temp" / "screens"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def set_swipe_scale(self, scale: int):
        self.explorer.navigator.set_swipe_scale(scale)

    async def run(self):
        await self.explorer.explore()

    async def process_tile(self, row: int, col: int):
        filename = self.output_dir / f"screen_{row}_{col}.png"

        if filename.exists():
            print(f"[✓] Skipping already saved screenshot: {filename.name}")
            return

        image = capture_fullscreen()
        if image is None:
            print(f"[✗] Failed to capture screenshot at tile ({row}, {col})")
            return

        cv2.imwrite(str(filename), image)
        print(f"[📸] Saved screenshot: {filename.name}")
