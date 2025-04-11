from enum import Enum
from typing import Tuple
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
        swipe_scale: int = 1
    ):
        """
        Navigator to perform swipes in map coordinates using affine transformation.

        :param swipe_executor: Callable to execute swipe with (x1, y1, x2, y2, duration).
        :param geometry: Instance of TileGeometry for pixel↔tile conversions.
        :param swipe_duration: Duration of swipe in ms.
        :param swipe_scale: Number of tiles to move per swipe (recommended 1-3).
        """
        self.swipe_executor = swipe_executor
        self.geometry = geometry
        self.duration = swipe_duration
        self.swipe_scale = max(1, min(swipe_scale, 3))

        self.anchor_map = {
            Direction.RIGHT: (4, 9),  # swipe from right to left → agent moves right
            Direction.LEFT: (5, 6),  # swipe from left to right → agent moves left
            Direction.DOWN: (6, 8),  # swipe from bottom to top → agent moves down
            Direction.UP: (9, 8),  # swipe from top to bottom → agent moves up
        }

    def set_swipe_scale(self, scale: int):
        self.swipe_scale = max(1, min(scale, 3))

    async def swipe_by_tiles(self, dx: int, dy: int, origin_tile: Tuple[int, int]):
        """
        Swipe using a vector of (dx, dy) tiles from a given origin tile,
        scaled by swipe_scale.
        """
        scaled_dx = dx * self.swipe_scale
        scaled_dy = dy * self.swipe_scale

        print(f"[SWIPE_BY_TILES] Scaled vector: ({scaled_dx}, {scaled_dy})")

        start_tile = origin_tile
        end_tile = (
            origin_tile[0] + scaled_dy,  # row shift
            origin_tile[1] + scaled_dx   # column shift
        )

        start_px = self.geometry.tile_to_pixel(start_tile)
        end_px = self.geometry.tile_to_pixel(end_tile)

        print(f"[SWIPE_BY_TILES] From tile: {start_tile} → {end_tile}, {scaled_dx}")
        print(f"                 Pixel: {start_px} → {end_px}\n")

        await self.swipe_executor(*start_px, *end_px, self.duration)


    async def swipe(self, direction: Direction):
        delta = {
            Direction.RIGHT: (1, 0),
            Direction.LEFT: (-1, 0),
            Direction.DOWN: (0, 1),
            Direction.UP: (0, -1)
        }[direction]

        start_tile = self.anchor_map[direction]
        end_tile = (
            start_tile[0] + delta[0] * self.swipe_scale,  # row (y)
            start_tile[1] + delta[1] * self.swipe_scale  # col (x)
        )
        print(f"swipe calculated by {delta[0]} * {self.swipe_scale} =  {delta[0] * self.swipe_scale}")

        start_px = self.geometry.tile_to_pixel(start_tile)
        end_px = self.geometry.tile_to_pixel(end_tile)

        print(f"[SWIPE] Direction: {direction.name} | From tile: {start_tile} → {end_tile}")
        print(f"         Pixel: {start_px} → {end_px}\n")

        await self.swipe_executor(*start_px, *end_px, self.duration)
