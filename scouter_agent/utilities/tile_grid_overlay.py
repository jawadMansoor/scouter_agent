import cv2
import numpy as np

def load_affine_matrix(filepath):
    return np.load(filepath)


def draw_tile_grid(image, affine_matrix, tile_rows=40, tile_cols=40):
    img_copy = image.copy()

    for row in range(tile_rows):
        for col in range(tile_cols):
            tile_coord = np.array([[col, row]], dtype=np.float32)  # (x=col, y=row)
            pixel_coord = cv2.transform(tile_coord[None, :, :], affine_matrix)[0][0]

            x, y = int(pixel_coord[0]), int(pixel_coord[1])
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                cv2.circle(img_copy, (x, y), 2, (0, 255, 0), -1)
                cv2.putText(img_copy, f"{row},{col}", (x+4, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)

    return img_copy


if __name__ == '__main__':
    image_path = "../../temp/skeleton_image.png"
    model_path = "tile_affine_model.npy"

    image = cv2.imread(image_path)
    affine_matrix = load_affine_matrix(model_path)
    print("Affine matrix:\n", affine_matrix)
    test_tiles = np.array([[0, 0], [10, 10], [20, 5]], dtype=np.float32).reshape(-1, 1, 2)
    mapped = cv2.transform(test_tiles, affine_matrix)
    print("Mapped test tiles:", mapped.reshape(-1, 2))

    overlayed = draw_tile_grid(image, affine_matrix, tile_rows=40, tile_cols=40)
    cv2.imshow("Tile Grid Overlay", overlayed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
