from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.domain.entities.map_tile import MapTile

class MapScouterService:
    def __init__(self, explorer: MapExplorer):
        self.explorer = explorer

    def run(self):
        # Start exploring the map
        self.explorer.explore()

    def process_tile(self, row: int, col: int) -> MapTile:
        # Process the map tile here (e.g., save, analyze, or detect objects)
        return MapTile(row=row, col=col)
