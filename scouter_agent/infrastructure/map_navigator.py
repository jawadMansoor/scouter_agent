from scouter_agent.screen_controller.screen_gestures import swipe, get_swipe_coordinates
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
        self.swipe_executor = swipe_executor
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.duration = swipe_duration
        self.scale = swipe_scaling

    async def swipe(self, direction: Direction):
        x1, y1, x2, y2 = get_swipe_coordinates(self.x1, self.x2, self.y1, self.scale, direction.value)
        await self.swipe_executor(x1, y1, x2, y2, self.duration)
