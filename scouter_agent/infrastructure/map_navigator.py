import asyncio
from enum import Enum
from typing import Tuple


class Direction(Enum):
    RIGHT = "right"
    LEFT = "left"
    DOWN = "down"
    UP = "up"


class MapNavigator:
    def __init__(
        self,
        swipe_executor,
        x1: int = 500,
        x2: int = 300,
        y1: int = 341,
        swipe_duration: int = 500,
        swipe_scaling: float = 0.495726496 * 1.005
    ):
        """
        Initializes the map navigator.

        :param swipe_executor: A callable that takes (x1, y1, x2, y2, duration) and performs the swipe.
        :param x1, x2, y1: Anchor and destination x/y coordinates for swipe gestures.
        :param swipe_duration: Duration in milliseconds for each swipe.
        :param swipe_scaling: Slope-based scaling to transform swipe vector appropriately.
        """
        self.swipe_executor = swipe_executor
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.duration = swipe_duration
        self.scale = swipe_scaling

    def get_swipe_coordinates(self, direction: Direction) -> Tuple[int, int, int, int]:
        """
        Calculates the swipe start and end points based on direction.

        :return: Tuple of (x1, y1, x2, y2)
        """
        dy = int(abs(self.x1 - self.x2) * self.scale)
        if direction == Direction.RIGHT:
            return self.x1, self.y1, self.x2, self.y1 - dy
        elif direction == Direction.LEFT:
            return self.x2, self.y1 - dy, self.x1, self.y1
        elif direction == Direction.DOWN:
            return self.x2, self.y1 + dy, self.x1, self.y1
        elif direction == Direction.UP:
            return self.x1, self.y1, self.x2, self.y1 + dy
        else:
            raise ValueError(f"Unsupported direction: {direction}")

    async def swipe(self, direction: Direction):
        x1, y1, x2, y2 = self.get_swipe_coordinates(direction)
        await self.swipe_executor(x1, y1, x2, y2, self.duration)
