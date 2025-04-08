import asyncio
from typing import Optional

from scouter_agent.domain.entities.tile import Tile
from scouter_agent.domain.services.tile_processor import TileProcessor
from scouter_agent.infrastructure.map_navigator import MapNavigator, Direction
from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.object_recognizer.detect_objects import capture_screen


class MapExplorationService:
    def __init__(self, map_navigator: MapNavigator, map_explorer: MapExplorer, tile_processor: TileProcessor):
        self.map_navigator = map_navigator
        self.map_explorer = map_explorer
        self.tile_processor = tile_processor
        self.exploration_task: Optional[asyncio.Task] = None

    async def explore(self):
        self.map_explorer.initialize_map()
        try:
            while True:
                image = await capture_screen()
                tile = self.tile_processor.process_tile(image)
                self.map_explorer.update_map(tile)

                direction = self.map_explorer.get_next_direction()
                if direction is None:
                    break

                await self.map_navigator.move(direction)
                await asyncio.sleep(1)  # Add delay if necessary between moves
        except asyncio.CancelledError:
            print("Exploration was cancelled.")

    def start_exploration(self):
        if not self.exploration_task or self.exploration_task.done():
            self.exploration_task = asyncio.create_task(self.explore())

    def stop_exploration(self):
        if self.exploration_task and not self.exploration_task.done():
            self.exploration_task.cancel()
