# Visual debugging overlay for a given screenshot
import cv2

def draw_tile_grid(image_path, tile_mapper, grid_size=(10, 10)):
    image = cv2.imread(image_path)

    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            cx, cy = tile_mapper.grid_to_screen(i, j)
            cv2.circle(image, (cx, cy), 3, (0, 0, 255), -1)
            cv2.putText(image, f"({i},{j})", (cx + 5, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    cv2.imshow("Tile Grid Overlay", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()