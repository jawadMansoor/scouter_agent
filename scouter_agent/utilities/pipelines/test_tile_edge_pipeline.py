import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize


def visualize_tile_edge_detection_steps(image: str):
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Updated wider HSV thresholds
    lower_white = np.array([0, 10, 160])
    upper_white = np.array([30, 80, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Skip morphology to preserve thin features
    masked_img = cv2.bitwise_and(image, image, mask=mask)
    gray = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)

    # Skeletonization
    binary = (gray > 0).astype(np.uint8)  # Binarize before skeletonizing
    skeleton = skeletonize(binary).astype(np.uint8) * 255

    titles = [
        "Original Image",
        "HSV Mask",
        "Masked Image (BGR)",
        "Grayscale",
        "Skeletonized"
    ]
    images = [
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
        mask,
        cv2.cvtColor(masked_img, cv2.COLOR_BGR2RGB),
        gray,
        skeleton
    ]

    plt.figure(figsize=(16, 8))
    for i in range(5):
        plt.subplot(2, 3, i + 1)
        cmap = 'gray' if i in [1, 3, 4] else None
        plt.imshow(images[i], cmap=cmap)
        plt.title(titles[i])
        plt.axis("off")

    plt.tight_layout()
    plt.show()
    cv2.imwrite("../../temp/skeleton_image.png",
                skeleton)
    return skeleton

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_tile_edge_pipeline.py path/to/desert_map.png")
    else:
        visualize_tile_edge_detection_steps(sys.argv[1])
