from scouter_agent.application.services.map_scouter_service import MapScouterService
from scouter_agent.infrastructure.map_navigator import MapNavigator
from scouter_agent.infrastructure.map_explorer import MapExplorer, Direction
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.screen_controller.screen_gestures import swipe
import asyncio
import numpy as np
from pathlib import Path


def main():
    # Load precomputed affine model
    MODEL_PATH = Path(__file__).parent / "scouter_agent" / "models" / "tile_affine_model.npy"
    affine_matrix = np.load(str(MODEL_PATH))
    tile_geometry = TileGeometry(affine_matrix)

    navigator = MapNavigator(
        swipe_executor=swipe,
        geometry=tile_geometry,
        swipe_duration=500
    )

    explorer = MapExplorer(navigator=navigator, total_rows=4, total_columns=4)
    service = MapScouterService(explorer, tile_geometry)

    # Set tile-level swipe scale (1 to 3)
    service.set_swipe_scale(3)

    asyncio.run(service.run())

if __name__ == "__main__":
    main()
