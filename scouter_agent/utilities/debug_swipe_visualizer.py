import cv2
import numpy as np
from scouter_agent.domain.tile_geometry import TileGeometry
from scouter_agent.infrastructure.map_navigator import Direction

def visualize_swipe_directions(image_path: str, tile_geometry: TileGeometry, tile_offset: int = 3):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image from {image_path}")

    directions = [
        Direction.RIGHT,
        Direction.LEFT,
        Direction.DOWN,
        Direction.UP
    ]

    color_map = {
        Direction.RIGHT: (255, 0, 0),   # Blue
        Direction.LEFT: (0, 255, 0),    # Green
        Direction.DOWN: (0, 0, 255),    # Red
        Direction.UP: (255, 255, 0)     # Cyan
    }

    label_map = {
        Direction.RIGHT: "RIGHT",
        Direction.LEFT: "LEFT",
        Direction.DOWN: "DOWN",
        Direction.UP: "UP"
    }

    anchor_map = {
        Direction.RIGHT: (5, 6),
        Direction.LEFT: (4, 9),
        Direction.DOWN: (9, 8),
        Direction.UP: (6, 8),
    }

    delta_map = {
        Direction.RIGHT: (0, tile_offset),
        Direction.LEFT: (0, -tile_offset),
        Direction.DOWN: (tile_offset, 0),
        Direction.UP: (-tile_offset, 0),
    }

    for direction in directions:
        anchor_tile = anchor_map[direction]
        delta = delta_map[direction]
        target_tile = (anchor_tile[0] + delta[0], anchor_tile[1] + delta[1])

        start_px = tile_geometry.tile_to_pixel(anchor_tile)
        end_px = tile_geometry.tile_to_pixel(target_tile)

        color = color_map[direction]
        label = label_map[direction]

        cv2.arrowedLine(image, start_px, end_px, color, 2, tipLength=0.2)
        mid_point = ((start_px[0] + end_px[0]) // 2, (start_px[1] + end_px[1]) // 2)
        cv2.putText(image, label, mid_point, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Swipe Directions", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    import sys
    from scouter_agent.domain.tile_geometry import TileGeometry
    import numpy as np

    image_path = "../../temp/screen_10_10.png"  # update path if needed
    affine_path = "../models/tile_affine_model.npy"
    affine_matrix = np.load(affine_path)
    tile_geometry = TileGeometry(affine_matrix)

    visualize_swipe_directions(image_path, tile_geometry)
