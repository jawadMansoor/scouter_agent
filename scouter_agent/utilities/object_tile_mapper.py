from typing import List, Tuple
import numpy as np
from scouter_agent.domain.tile_geometry import TileGeometry


def get_tile_bbox_for_object(
    hud_row: int, hud_col: int,
) -> List[Tuple[int, int]]:
    """
    List of tile coordinates from affine transformation are listed below.
    The Coordinate corresponding to HUD tile is 5,5 therefore we will subtrack
    5,5 from all the coordiantes and add HUD coordinates and return it.

    list of tile coordinates:
    [(5, 1), (8, 9), (9, 8), (2, 2), (7, 10), (4, 2),
    (3, 6), (5, 3), (0, -1), (8, 11), (9, 10), (2, 4),
    (6, 4), (7, 3), (-1, 0), (5, 5), (0, 0), (9, 12),
    (11, 9), (6, 6), (7, 5), (3, 1), (5, 7), (9, 5),
    (0, 2), (1, 3), (7, 7), (3, 3), (9, 7), (10, 8),
    (7, 9), (12, 8), (3, 5), (5, 2), (4, 4), (9, 9),
    (1, -1), (10, 10), (12, 10), (5, 4), (4, 6), (8, 6),
    (1, 0), (10, 12), (11, 11), (7, 4), (6, 8), (3, 0),
    (5, 6), (8, 8), (1, 2), (2, 1), (3, 2), (4, 1),
    (8, 10), (10, 7), (1, 4), (2, 3), (6, 3), (3, 4),
    (4, 3), (10, 9), (9, 11), (11, 8), (2, 5), (6, 5),
    (-1, 1), (12, 9), (4, 5), (8, 5), (0, 1), (2, -1),
    (10, 11), (11, 10), (6, 7), (7, 6), (4, 7), (5, 8),
    (8, 7), (9, 6), (1, 1), (2, 0), (0, 3), (6, 9), (7, 8)]

    Generated:
    affine_matrix = np.load ("scouter_agent/models/tile_affine_model.npy")
    geometry = TileGeometry(affine_matrix)
    cols = range(0, 896,10)
    rows = range(0, 456, 10)
    coords = [(r,c) for r in rows for c in cols]
    tiles_list = [geometry.pixel_to_tile(coord) for coord in coords]
    set((int(r), int(c)) for r, c in tiles_list)
    """
    tile_cords = [
        (5, 1), (8, 9), (9, 8), (2, 2), (7, 10),
        (4, 2), (3, 6), (5, 3), (0, -1), (8, 11),
        (9, 10), (2, 4), (6, 4), (7, 3), (-1, 0),
        (5, 5), (0, 0), (9, 12), (11, 9), (6, 6),
        (7, 5), (3, 1), (5, 7), (9, 5), (0, 2),
        (1, 3), (7, 7), (3, 3), (9, 7), (10, 8),
        (7, 9), (12, 8), (3, 5), (5, 2), (4, 4),
        (9, 9), (1, -1), (10, 10), (12, 10), (5, 4),
        (4, 6), (8, 6), (1, 0), (10, 12), (11, 11),
        (7, 4), (6, 8), (3, 0), (5, 6), (8, 8),
        (1, 2), (2, 1), (3, 2), (4, 1), (8, 10),
        (10, 7), (1, 4), (2, 3), (6, 3), (3, 4),
        (4, 3), (10, 9), (9, 11), (11, 8), (2, 5),
        (6, 5), (-1, 1), (12, 9), (4, 5), (8, 5),
        (0, 1), (2, -1), (10, 11), (11, 10),
        (6, 7), (7, 6), (4, 7), (5, 8), (8, 7),
        (9, 6), (1, 1), (2, 0), (0, 3), (6, 9), (7, 8)
    ]

    # Shift coordinate system to HUD tile 6,6
    # and Add HUD coordiantes
    tile_cords = [(r-6+hud_row,c-6+hud_col) for r,c in tile_cords]

    return tile_cords
