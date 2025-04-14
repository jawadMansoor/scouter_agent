import asyncio
from typing import Callable, Optional

from scouter_agent.infrastructure.map_navigator import MapNavigator, Direction


class MapExplorer:
    """Serpentine iterator that walks the map in *navigator.swipe_scale* steps.

    There is **no separate stride setting** – the step size is always taken
    from the associated ``MapNavigator`` so that logical iteration and the
    physical swipe distance never drift apart.
    """

    def __init__(
        self,
        navigator: MapNavigator,
        total_rows: int,
        total_columns: int,
        process_tile_fn: Optional[Callable[[int, int], asyncio.Future]] = None,
    ) -> None:
        self.navigator = navigator
        self.total_rows = total_rows
        self.total_columns = total_columns
        self.process_tile_fn = process_tile_fn

        self._override_next: Optional[tuple[int, int]] = None  # drift fix hook

    # ------------------------------------------------------------------
    @property
    def step(self) -> int:
        """Current logical step size in tiles (mirrors navigator.swipe_scale)."""
        return max(1, self.navigator.swipe_scale)

    # ------------------------------------------------------------------
    def override_current_position(self, row: int, col: int) -> None:
        """Called by ScreenshotScoutingService after a corrective swipe."""
        self._override_next = (row, col)

    # ------------------------------------------------------------------
    async def explore(self):
        row = 0
        while row < self.total_rows:
            if self._override_next:
                row, _ = self._override_next
                self._override_next = None

            left_to_right = (row // self.step) % 2 == 0
            await self._traverse_row(row, left_to_right)
            row += self.step
            if row < self.total_rows:
                await self.navigator.swipe(Direction.DOWN)

    # ------------------------------------------------------------------
    async def _traverse_row(self, base_row: int, left_to_right: bool):
        cols = range(0, self.total_columns, self.step)
        if not left_to_right:
            cols = reversed(list(cols))

        direction = Direction.RIGHT if left_to_right else Direction.LEFT

        for base_col in cols:
            if self.process_tile_fn:
                await self.process_tile_fn(base_row, base_col)

            # determine if another horizontal swipe is needed
            end_of_row = (
                (left_to_right and base_col + self.step >= self.total_columns) or
                (not left_to_right and base_col < self.step)
            )
            if not end_of_row:
                await self.navigator.swipe(direction)
