from enum import Enum
from typing import Tuple
import asyncio
from scouter_agent.domain.tile_geometry import TileGeometry



class Direction(Enum):
    RIGHT = "right"   # move left in pixel space (→ in visual map)
    LEFT = "left"     # move right in pixel space (← in visual map)
    DOWN = "down"     # move up in pixel space (↓ in visual map)
    UP = "up"         # move down in pixel space (↑ in visual map)


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

        # Direction deltas (row, col)
        self.tile_deltas = {
            Direction.RIGHT: (0, -1),   # → right in pixel space (left in tile space)
            Direction.LEFT:  (0, 1),    # ← left in pixel space (right in tile space)
            Direction.DOWN:  (-1, 0),   # ↓ down in pixel space (up in tile space)
            Direction.UP:    (1, 0),    # ↑ up in pixel space (down in tile space)
        }

        # Anchor tile positions to start swipes from
        self.anchor_map = {
            Direction.RIGHT: (4, 9),
            Direction.LEFT: (5, 6),
            Direction.DOWN: (6, 8),
            Direction.UP:   (9, 8),
        }

    def set_swipe_scale(self, scale: int):
        """Set the number of tiles to move in a single swipe."""
        self.swipe_scale = max(1, min(scale, 3))

    async def swipe_by_tiles(self, delta_row: int, delta_col: int, origin_tile: Tuple[int, int]):
        """
        Swipe using a (delta_row, delta_col) from a given origin tile, scaled by swipe_scale.

        :param delta_row: Vertical motion in tile space
        :param delta_col: Horizontal motion in tile space
        :param origin_tile: (row, col) tuple of starting tile
        """
        scaled_row = delta_row
        scaled_col = delta_col

        start_row, start_col = origin_tile
        end_row = start_row + scaled_row
        end_col = start_col + scaled_col

        start_px = self.geometry.tile_to_pixel((start_row, start_col))
        end_px = self.geometry.tile_to_pixel((end_row, end_col))

        print(f"[SWIPE_BY_TILES] From tile: ({start_row}, {start_col}) → ({end_row}, {end_col})")
        print(f"                 Pixel: {start_px} → {end_px}\n")

        await self.swipe_executor(*start_px, *end_px, self.duration)

    async def swipe(self, direction: Direction):
        """
        Perform a swipe in the given direction using anchor-based tile positions.
        """
        delta_row, delta_col = self.tile_deltas[direction]

        anchor_row, anchor_col = self.anchor_map[direction]
        end_row = anchor_row + delta_row * self.swipe_scale
        end_col = anchor_col + delta_col * self.swipe_scale

        start_px = self.geometry.tile_to_pixel((anchor_row, anchor_col))
        end_px = self.geometry.tile_to_pixel((end_row, end_col))

        print(f"[SWIPE] Direction: {direction.name}")
        print(f"        From tile: ({anchor_row}, {anchor_col}) → ({end_row}, {end_col})")
        print(f"        Pixel: {start_px} → {end_px}\n")

        await self.swipe_executor(*start_px, *end_px, self.duration)
