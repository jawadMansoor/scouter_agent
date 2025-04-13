import os
import csv
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Tuple
import pandas as pd

from scouter_agent.domain.entities.map_tile import MapTile
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.object_recognizer.detect_objects import capture_fullscreen
import easyocr

class TileLogger:
    def __init__(self, base_dir: str = "scouter_agent/datalog", log_file: str = "tiles_log.csv"):
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.log_path = self.base_path / log_file
        self.reader = easyocr.Reader(['en'], gpu=False)

        # Ensure log file exists with headers
        if not self.log_path.exists():
            with open(self.log_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["row", "col", "timestamp", "image_path", "ocr_text"])

    def _image_exists(self, row: int, col: int) -> bool:
        tile_folder = self.base_path / f"row_{row}"
        image_path = tile_folder / f"tile_{row}_{col}.png"
        return image_path.exists()

    def _save_image(self, image: np.ndarray, row: int, col: int) -> Path:
        tile_folder = self.base_path / f"row_{row}"
        tile_folder.mkdir(parents=True, exist_ok=True)
        image_path = tile_folder / f"tile_{row}_{col}.png"
        cv2.imwrite(str(image_path), image)
        return image_path

    def _run_ocr(self, image: np.ndarray) -> str:
        results = self.reader.readtext(image)
        return " ".join([text for _, text, _ in results])

    def _log_tile(self, row: int, col: int, image_path: Path, ocr_text: str):
        timestamp = datetime.now().isoformat()
        with open(self.log_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([row, col, timestamp, str(image_path), ocr_text])

    def process_tile(self, row: int, col: int, pixel_coord: Tuple[int, int], window_size: int = 100) -> MapTile:
        if self._image_exists(row, col):
            print(f"[SKIP] Tile ({row}, {col}) already logged.")
            return MapTile(row=row, col=col)

        screenshot = capture_fullscreen()
        if screenshot is None:
            raise RuntimeError("Failed to capture screen.")

        x, y = pixel_coord
        x1, y1 = max(0, x - window_size // 2), max(0, y - window_size // 2)
        x2, y2 = min(screenshot.shape[1], x + window_size // 2), min(screenshot.shape[0], y + window_size // 2)
        cropped = screenshot[y1:y2, x1:x2]

        image_path = self._save_image(cropped, row, col)
        ocr_text = self._run_ocr(cropped)
        self._log_tile(row, col, image_path, ocr_text)

        print(f"[✓] Logged tile ({row}, {col}) | OCR: {ocr_text}")
        return MapTile(row=row, col=col)
