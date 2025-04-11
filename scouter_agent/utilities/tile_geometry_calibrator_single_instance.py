# A tool to manually calibrate the tile geometry from a screenshot

import cv2
import numpy as np


def calibrate_tile_geometry(image_path):
    image = cv2.imread(image_path)
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Calibration", image)

    print("Click the four corners of one tile in this order: E, N, W, S")
    cv2.imshow("Calibration", image)
    cv2.setMouseCallback("Calibration", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(points) != 4:
        raise ValueError("You must select exactly 4 points.")

    east, north, west, south = points
    tile_width = np.linalg.norm(np.array(east) - np.array(west))
    tile_height = np.linalg.norm(np.array(north) - np.array(south))
    center_x = int((east[0] + west[0]) / 2)
    center_y = int((north[1] + south[1]) / 2)

    print(f"Tile Width: {tile_width}")
    print(f"Tile Height: {tile_height}")
    print(f"Origin Offset: ({center_x}, {center_y})")

    return {
        "tile_width": tile_width,
        "tile_height": tile_height,
        "origin": (center_x, center_y)
    }
