import asyncio
from scouter_agent.navigation.map_navigator import MapNavigator, Direction
from typing import Callable, Optional


class MapExplorer:
    def __init__(
        self,
        navigator: MapNavigator,
        total_rows: int,
        total_columns: int,
        process_tile_fn: Optional[Callable[[int, int], asyncio.Future]] = None,
    ):
        """
        Initializes the grid explorer.

        :param navigator: Instance of MapNavigator.
        :param total_rows: Number of rows in the map grid.
        :param total_columns: Number of columns in the map grid.
        :param process_tile_fn: Optional coroutine function to process a tile at (row, col).
        """
        self.navigator = navigator
        self.total_rows = total_rows
        self.total_columns = total_columns
        self.process_tile_fn = process_tile_fn

    async def explore(self):
        """
        Traverse the entire map using serpentine strategy.
        """
        for row in range(self.total_rows):
            if row % 2 == 0:
                # Left to right
                await self._traverse_row(row, left_to_right=True)
            else:
                # Right to left
                await self._traverse_row(row, left_to_right=False)

            # Swipe down to next row if not at the last
            if row < self.total_rows - 1:
                await self.navigator.swipe(Direction.DOWN)

    async def _traverse_row(self, row: int, left_to_right: bool):
        """
        Traverse a single row either left-to-right or right-to-left.
        """
        direction = Direction.RIGHT if left_to_right else Direction.LEFT

        col_range = range(self.total_columns) if left_to_right else range(self.total_columns - 1, -1, -1)

        for col in col_range:
            if self.process_tile_fn:
                await self.process_tile_fn(row, col)

            # Avoid swiping on last column
            if (left_to_right and col < self.total_columns - 1) or \
               (not left_to_right and col > 0):
                await self.navigator.swipe(direction)
