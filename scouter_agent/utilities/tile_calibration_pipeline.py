import cv2
import json
import numpy as np
from calibration_gui_tool import CalibrationAnnotator
from hough_corner_detector import visualize_hough_and_corners
from scouter_agent.infrastructure.capture_devices import AsyncWindowCapture, CaptureConfig
from scouter_agent.utilities.pipelines.test_tile_edge_pipeline import visualize_tile_edge_detection_steps
import asyncio

def save_annotations(filepath, annotations):
    data = [
        {"pixel": list(pixel), "tile": list(tile)}
        for pixel, tile in annotations
    ]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_annotations(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return [(tuple(item['pixel']), tuple(item['tile'])) for item in data]


def compute_affine_transform(pairs):
    pixel_coords, tile_coords = zip(*pairs)
    src = np.array(tile_coords, dtype=np.float32)
    dst = np.array(pixel_coords, dtype=np.float32)
    matrix, _ = cv2.estimateAffine2D(src, dst)
    return matrix


def save_affine_matrix(filepath, matrix):
    np.save(filepath, matrix)


def load_affine_matrix(filepath):
    return np.load(filepath)


if __name__ == '__main__':
    image_path = "../../temp/skeleton_image.png"
    annotation_file = "tile_annotations.json"
    model_file = "../models/tile_affine_model.npy"

    game_cap_cfg = CaptureConfig(
        game_res=(600, 1054),
        game_anchor="br",  # bottom‑right
        border_trim=(0.08, 0.16, 0.05, 0.1)  # l,r,b,t
    )
    global_cap = AsyncWindowCapture(game_cap_cfg)
    image = asyncio.run(global_cap.grab())
    cv2.imwrite(image_path, image)
    skeleton_gray = visualize_tile_edge_detection_steps(image)
    # skeleton_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    corners = visualize_hough_and_corners(skeleton_gray)

    annotator = CalibrationAnnotator(image, corners)
    annotations = annotator.annotate()

    save_annotations(annotation_file, annotations)
    print(f"[✓] Saved annotations to {annotation_file}")

    affine_matrix = compute_affine_transform(annotations)
    save_affine_matrix(model_file, affine_matrix)
    print(f"[✓] Saved affine model to {model_file}")
