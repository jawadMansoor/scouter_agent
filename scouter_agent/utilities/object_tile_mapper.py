from typing import List, Tuple
import numpy as np
from scouter_agent.domain.tile_geometry import TileGeometry


def get_tile_bbox_for_object(
    pixel_bbox: Tuple[int, int, int, int],  # (x1, y1, x2, y2)
    geometry: TileGeometry
) -> List[Tuple[int, int]]:
    """
    Converts a pixel bounding box to a list of tile coordinates it overlaps.
    bbox = (1032, 875, 1184, 1024)  # (x1, y1, x2, y2)
    tiles = get_tile_bbox_for_object(bbox, tile_geometry)
    print("Occupied tiles:", tiles)
    """
    x1, y1, x2, y2 = pixel_bbox
    corners = [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]

    tile_coords = [geometry.pixel_to_tile(pt) for pt in corners]
    tile_xs = [coord[0] for coord in tile_coords]
    tile_ys = [coord[1] for coord in tile_coords]

    min_col = int(np.floor(min(tile_xs)))
    max_col = int(np.ceil(max(tile_xs)))
    min_row = int(np.floor(min(tile_ys)))
    max_row = int(np.ceil(max(tile_ys)))

    tile_bbox = [
        (r, c)
        for r in range(min_row, max_row)
        for c in range(min_col, max_col)
    ]
    return tile_bbox
