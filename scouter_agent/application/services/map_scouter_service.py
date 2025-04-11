from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.domain.entities.map_tile import MapTile
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.object_recognizer.detect_objects import capture_screen
import cv2
import numpy as np

class MapScouterService:
    def __init__(self, explorer: MapExplorer, tile_geometry: TileGeometry):
        self.explorer = explorer
        self.tile_geometry = tile_geometry
        self.explorer.process_tile_fn = self.process_tile

    async def run(self):
        await self.explorer.explore()

    async def process_tile(self, row: int, col: int) -> MapTile:
        # Get pixel location of the tile center
        pixel_coord = self.tile_geometry.tile_to_pixel((row, col))

        # Extract screen centered around pixel_coord
        image = capture_screen_at_pixel(pixel_coord)

        # Optionally: object recognition / logging goes here
        print(f"Scouting tile ({row}, {col}) at pixel {pixel_coord}")

        return MapTile(row=row, col=col)


def capture_screen_at_pixel(pixel_coord, window_size=100):
    # For now, call ADB screenshot and crop locally — placeholder logic
    screenshot = cv2.imread("skeleton_filtered.png")  # Replace with actual capture
    x, y = pixel_coord
    x1 = max(0, x - window_size // 2)
    y1 = max(0, y - window_size // 2)
    x2 = min(screenshot.shape[1], x + window_size // 2)
    y2 = min(screenshot.shape[0], y + window_size // 2)
    return screenshot[y1:y2, x1:x2]
