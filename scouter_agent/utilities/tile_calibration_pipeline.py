import cv2
import json
import numpy as np
from calibration_gui_tool import CalibrationAnnotator
from hough_corner_detector import visualize_hough_and_corners


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

    image = cv2.imread(image_path)
    skeleton_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    corners = visualize_hough_and_corners(skeleton_gray)

    annotator = CalibrationAnnotator(image, corners)
    annotations = annotator.annotate()

    save_annotations(annotation_file, annotations)
    print(f"[✓] Saved annotations to {annotation_file}")

    affine_matrix = compute_affine_transform(annotations)
    save_affine_matrix(model_file, affine_matrix)
    print(f"[✓] Saved affine model to {model_file}")
