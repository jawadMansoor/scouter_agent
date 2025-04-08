import subprocess
import asyncio
from typing import Tuple

async def swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 500):
    command = f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}"
    process = await asyncio.create_subprocess_shell(command)
    await process.wait()

def get_swipe_coordinates(x1: int, x2: int, y1: int, scale: float, direction: str) -> Tuple[int, int, int, int]:
    dy = int(abs(x1 - x2) * scale)
    if direction == 'right':
        return x1, y1, x2, y1 - dy
    elif direction == 'left':
        return x2, y1 - dy, x1, y1
    elif direction == 'down':
        return x2, y1 + dy, x1, y1
    elif direction == 'up':
        return x1, y1, x2, y1 + dy
    else:
        raise ValueError(f"Unsupported direction: {direction}")
