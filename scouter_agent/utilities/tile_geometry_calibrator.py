import cv2
import ast
from scouter_agent.domain.tile_geometry import TileGeometryCalibrator

class TileCalibratorGUI:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.clone = self.image.copy()
        self.calibrator = TileGeometryCalibrator()
        self.window_name = "Tile Calibrator"
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.current_click = None

    def click_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"[INFO] Clicked at pixel: ({x}, {y})")
            try:
                tile_input = input(f"Enter tile coordinate for pixel ({x}, {y}) as (row, col): ")
                tile_coord = ast.literal_eval(tile_input)
                assert isinstance(tile_coord, tuple) and len(tile_coord) == 2
                self.calibrator.add_calibration_point((x, y), tile_coord)
                self.current_click = (x, y, tile_coord)
                print(f"[INFO] Added: Pixel {x, y} <-> Tile {tile_coord}")
            except Exception as e:
                print(f"[ERROR] Invalid input: {e}")

    def draw_overlay(self):
        """Draw estimated tile centers on the image for visual validation."""
        if not self.calibrator.fitted:
            print("[WARNING] Cannot draw overlay, model not yet fitted.")
            return

        overlay = self.clone.copy()
        h, w = self.image.shape[:2]
        for row in range(-10, 10):  # limit to reasonable range
            for col in range(-10, 10):
                px, py = self.calibrator.tile_to_pixel((row, col))
                if 0 <= px < w and 0 <= py < h:
                    cv2.circle(overlay, (int(px), int(py)), 5, (0, 255, 0), -1)
                    cv2.putText(overlay, f"{row},{col}", (int(px)+5, int(py)-5),
                                self.font, 0.3, (255, 255, 255), 1)

        return overlay

    def run(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.click_callback)

        print("[INFO] Press 'd' to fit and draw grid, 's' to save model, 'q' to quit.")
        while True:
            if self.current_click:
                x, y, tile = self.current_click
                cv2.circle(self.clone, (x, y), 5, (0, 0, 255), -1)
                cv2.putText(self.clone, f"{tile}", (x + 5, y - 5), self.font, 0.4, (0, 0, 255), 1)
                self.current_click = None

            cv2.imshow(self.window_name, self.clone)
            key = cv2.waitKey(10) & 0xFF

            if key == ord('d'):
                try:
                    self.calibrator.compute_affine_transform()
                    print("[INFO] Fitted affine transformation.")
                    self.clone = self.draw_overlay()
                except Exception as e:
                    print(f"[ERROR] Failed to fit model: {e}")

            elif key == ord('s'):
                import pickle
                with open("tile_geometry_model.pkl", "wb") as f:
                    pickle.dump(self.calibrator, f)
                print("[INFO] Saved tile calibrator model to 'tile_geometry_model.pkl'.")

            elif key == ord('q'):
                break

        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tile_geometry_calibrator.py <image_path>")
    else:
        gui = TileCalibratorGUI(sys.argv[1])
        gui.run()
