import asyncio
from scouter_agent.infrastructure.map_navigator import MapNavigator, Direction
from typing import Callable, Optional
from pathlib import Path
import numpy as np
from datetime import datetime
import cv2
from tqdm import tqdm


class MapExplorer:
    def __init__(
        self,
        navigator: MapNavigator,
        total_rows: int,
        total_columns: int,
        stride: int = 4,
        screenshot_dir: Path = Path("scouter_agent/temp/screenshots"),
    ):
        self.navigator = navigator
        self.total_rows = total_rows
        self.total_columns = total_columns
        self.stride = stride
        self.screenshot_dir = screenshot_dir
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.visited_tiles = []

    async def explore(self):
        """
        Traverse the entire map using serpentine strategy with stride, capturing a screenshot at each center tile.
        """
        total_steps = ((self.total_rows // self.stride) * (self.total_columns // self.stride))
        with tqdm(total=total_steps, desc="🗺️  Scouting Progress", unit="tile") as pbar:
            for row in range(0, self.total_rows, self.stride):
                if (row // self.stride) % 2 == 0:
                    col_range = range(0, self.total_columns, self.stride)
                    direction = Direction.RIGHT
                else:
                    col_range = range(self.total_columns - 1, -1, -self.stride)
                    direction = Direction.LEFT

                for col in col_range:
                    await self.capture_and_log_tile(row, col)
                    self.visited_tiles.append((row, col))

                    if (direction == Direction.RIGHT and col + self.stride < self.total_columns) or \
                       (direction == Direction.LEFT and col - self.stride >= 0):
                        await self.navigator.swipe(direction)

                if row + self.stride < self.total_rows:
                    await self.navigator.swipe(Direction.DOWN)

    async def capture_and_log_tile(self, row: int, col: int):
        from scouter_agent.object_recognizer.detect_objects import capture_fullscreen

        screenshot = capture_fullscreen()
        if screenshot is not None:
            filename = f"tile_{row}_{col}.png"
            filepath = self.screenshot_dir / filename
            cv2.imwrite(str(filepath), screenshot)
            # print(f"[✓] Saved screenshot for tile ({row}, {col}) → {filepath}")
        # else:
            # print(f"[✗] Failed to capture screenshot for tile ({row}, {col})")


