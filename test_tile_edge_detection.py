import cv2
import matplotlib.pyplot as plt
from scouter_agent.utilities.tile_edge_filter import isolate_tile_edges  # Adjust import if needed

def visualize_tile_edges(image_path: str):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Run the tile edge isolation
    edges = isolate_tile_edges(image)

    # Convert for Matplotlib (OpenCV uses BGR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Show original and edges side-by-side
    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(image_rgb)
    plt.title("Original Image")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(edges, cmap='gray')
    plt.title("Detected Tile Edges")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_tile_edge_detection.py path/to/screenshot.png")
    else:
        visualize_tile_edges(sys.argv[1])
