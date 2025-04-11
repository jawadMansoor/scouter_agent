from typing import Tuple
import numpy as np
import cv2

class TileGeometry:
    def __init__(self, affine_matrix: np.ndarray):
        self.affine = affine_matrix
        self.inverse_affine = cv2.invertAffineTransform(affine_matrix)

    def tile_to_pixel(self, tile_coord: Tuple[int, int]) -> Tuple[int, int]:
        pt = np.array([[tile_coord]], dtype=np.float32)  # shape (1, 1, 2)
        px = cv2.transform(pt, self.affine)[0][0]
        return int(round(px[0])), int(round(px[1]))

    def pixel_to_tile(self, pixel_coord: Tuple[int, int]) -> Tuple[float, float]:
        pt = np.array([[pixel_coord]], dtype=np.float32)
        tile = cv2.transform(pt, self.inverse_affine)[0][0]
        return float(tile[0]), float(tile[1])
