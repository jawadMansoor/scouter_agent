from scouter_agent.infrastructure.capture_devices import WindowCapture
from scouter_agent.application.services.screenshot_scouting_service import ScreenshotScoutingService
from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.infrastructure.map_navigator import MapNavigator
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.screen_controller.screen_gestures import swipe
from scouter_agent.domain.row_tracker import RowTracker
from scouter_agent.infrastructure.capture_devices import AsyncWindowCapture, CaptureConfig
from scouter_agent.utilities.coverage_bitmap import CoverageBitmap
from scouter_agent.infrastructure.ocr_utils import read_global_coord
import asyncio
import numpy as np
from pathlib import Path


def main():
    # Load precomputed affine model
    MODEL_PATH = Path(__file__).parent / "scouter_agent" / "models" / "tile_affine_model.npy"
    affine_matrix = np.load(str(MODEL_PATH))
    tile_geometry = TileGeometry(affine_matrix)
    game_cap_cfg  = CaptureConfig(
        game_res=(634, 1101),
        game_anchor="br",  # bottom‑right
        border_trim=(0.08, 0.16, 0.05, 0.1)  # l,r,b,t
    )
    global_cap = AsyncWindowCapture(game_cap_cfg)
    first_frame = asyncio.run(global_cap.grab())  # sync example
    start_rc = (0, 0) # read_global_coord(first_frame) or

    row_tracker = RowTracker(
        hud_reader=read_global_coord,
        start_row=start_rc[0],
        start_col=start_rc[1],
    )
    coverage_bitmap = CoverageBitmap(1200, 1200)

    navigator = MapNavigator(
        swipe_executor=swipe,
        geometry=tile_geometry,
        swipe_duration=50,
    )

    explorer = MapExplorer(
        navigator=navigator,
        rows_range=(0,100),
        columns_range=(0,100),
        row_step=3,
        process_tile_fn=None,  # your fn
        row_tracker=row_tracker,
        capture_device=global_cap,
    )

    service = ScreenshotScoutingService(
        explorer,
        tile_geometry,
        capture_device=global_cap,
        coverage_bitmap=coverage_bitmap,
        hud_reader=read_global_coord,
    )

    explorer.process_tile_fn = service.process_screen

    asyncio.run(service.run())
    coverage_bitmap.save("coverage.npy")


if __name__ == "__main__":
    main()