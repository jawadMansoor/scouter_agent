from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.domain.entities.map_tile import MapTile
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.object_recognizer.detect_objects import capture_screen
import cv2
import numpy as np
from scouter_agent.object_recognizer.detect_objects import capture_fullscreen

class MapScouterService:
    def __init__(self, explorer: MapExplorer, tile_geometry: TileGeometry):
        self.explorer = explorer
        self.tile_geometry = tile_geometry
        self.explorer.process_tile_fn = self.process_tile

    def set_swipe_scale(self, scale: int):
        self.explorer.navigator.set_swipe_scale(scale)

    async def run(self):
        await self.explorer.explore()

    async def process_tile(self, row: int, col: int) -> MapTile:
        pixel_coord = self.tile_geometry.tile_to_pixel((row, col))
        image = capture_screen_at_pixel(pixel_coord)
        print(f"Scouting tile ({row}, {col}) at pixel {pixel_coord}")
        return MapTile(row=row, col=col)

def capture_screen_at_pixel(pixel_coord, window_size=100):
    # Capture from ADB
    screenshot = capture_fullscreen()  # NEW FUNCTION
    if screenshot is None:
        raise RuntimeError("Failed to capture screen from device.")

    x, y = pixel_coord
    x1 = max(0, x - window_size // 2)
    y1 = max(0, y - window_size // 2)
    x2 = min(screenshot.shape[1], x + window_size // 2)
    y2 = min(screenshot.shape[0], y + window_size // 2)
    return screenshot[y1:y2, x1:x2]
