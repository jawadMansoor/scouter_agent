from enum import Enum
from typing import Tuple
import numpy as np
import asyncio
from scouter_agent.domain.tile_geometry import TileGeometry

class Direction(Enum):
    RIGHT = "right"
    LEFT = "left"
    DOWN = "down"
    UP = "up"

class MapNavigator:
    def __init__(
        self,
        swipe_executor,
        geometry: TileGeometry,
        swipe_duration: int = 500,
        swipe_scale: int = 1  # number of tiles to move per swipe (max 3 recommended)
    ):
        self.swipe_executor = swipe_executor
        self.geometry = geometry
        self.duration = swipe_duration
        self.swipe_scale = min(max(swipe_scale, 1), 3)  # clamp between 1 and 3

    async def swipe_by_tiles(self, dx: int, dy: int):
        """
        Performs a swipe to move approximately (dx, dy) tiles * swipe_scale.
        """
        scaled_dx = dx * self.swipe_scale
        scaled_dy = dy * self.swipe_scale

        start_tile = (0, 0)
        end_tile = (scaled_dy, scaled_dx)  # row → y, col → x

        start_px = self.geometry.tile_to_pixel(start_tile)
        end_px = self.geometry.tile_to_pixel(end_tile)

        x1, y1 = start_px
        x2, y2 = end_px

        await self.swipe_executor(x1, y1, x2, y2, self.duration)

    async def swipe(self, direction: Direction):
        delta = {
            Direction.RIGHT: (1, 0),
            Direction.LEFT: (-1, 0),
            Direction.DOWN: (0, 1),
            Direction.UP: (0, -1)
        }[direction]
        await self.swipe_by_tiles(*delta)
