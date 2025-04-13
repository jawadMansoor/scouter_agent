import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.object_recognizer.detect_objects import capture_fullscreen


class ScreenshotService:
    def __init__(self, output_dir: Path, geometry: TileGeometry):
        self.output_dir = output_dir
        self.geometry = geometry
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture_and_save(self, tile_coord: tuple[int, int]) -> Path:
        """
        Captures a screenshot and saves it using the center tile coordinates.
        Returns the path to the saved image.
        """
        image = capture_fullscreen()
        if image is None:
            raise RuntimeError("Failed to capture screen.")

        filename = f"tile_{tile_coord[0]}_{tile_coord[1]}.png"
        filepath = self.output_dir / filename
        cv2.imwrite(str(filepath), image)

        print(f"[SCREENSHOT] Saved {filepath}")
        return filepath

    def get_current_timestamped_name(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"screenshot_{timestamp}.png"
