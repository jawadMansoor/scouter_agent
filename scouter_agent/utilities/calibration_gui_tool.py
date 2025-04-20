import cv2
import numpy as np

class CalibrationAnnotator:
    def __init__(self, image, corners):
        self.image = image.copy()
        self.original_image = image.copy()
        self.corners = sorted(corners, key=lambda pt: (pt[1], pt[0]))  # sort top-to-bottom, then left-to-right
        self.annotations = {}  # dict: pixel_point -> tile_coord
        self.current_index = 0
        self.window_name = "Calibration GUI"
        self.input_buffer = ""

    def annotate(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, lambda *args: None)
        self._draw_interface()

        print("Instructions:")
        print("←/→ : navigate corners, Backspace: delete entry")
        print("Numbers + space: enter row col")
        print("Enter: confirm input, S: save and exit, R: reset, ESC: exit")

        while True:
            self._draw_interface()
            cv2.imshow(self.window_name, self.image)
            key = cv2.waitKey(0)

            if key == 27:  # ESC
                print("[INFO] Exiting without saving.")
                self.annotations.clear()
                break
            elif key in [ord('s'), ord('S')]:
                print("[INFO] Saving annotations and exiting.")
                break
            elif key in [ord('r'), ord('R')]:
                print("[INFO] Resetting annotations.")
                self.annotations.clear()
                self.current_index = 0
                self.input_buffer = ""
            elif key == 8 or key == 127:  # Backspace
                self.input_buffer = self.input_buffer[:-1]
            elif key in [81, 2424832]:  # Left arrow
                self.current_index = max(0, self.current_index - 1)
                self.input_buffer = ""
            elif key in [83, 2555904]:  # Right arrow
                self.current_index = min(len(self.corners) - 1, self.current_index + 1)
                self.input_buffer = ""
            elif key in [13, 10]:  # Enter
                self._confirm_input()
            elif 32 <= key <= 126:
                self.input_buffer += chr(key)

        cv2.destroyAllWindows()
        return [(pt, self.annotations[pt]) for pt in self.annotations]

    def _confirm_input(self):
        if self.input_buffer.strip().lower() == 's':
            self.input_buffer = ""
            return
        try:
            row, col = map(int, self.input_buffer.strip().split())
            px = self.corners[self.current_index]
            self.annotations[px] = (row, col)
            print(f"[OK] {px} => ({row}, {col})")
            self.current_index = min(len(self.corners) - 1, self.current_index + 1)
        except:
            print(f"[ERROR] Invalid input: '{self.input_buffer}'")
        self.input_buffer = ""

    def _draw_interface(self):
        self.image = self.original_image.copy()

        # Draw all corners
        for pt in self.corners:
            cv2.circle(self.image, pt, 3, (0, 255, 255), -1)

        # Highlight current corner
        if self.current_index < len(self.corners):
            cv2.circle(self.image, self.corners[self.current_index], 6, (0, 0, 255), 2)

        # Draw annotations
        for px, tile in self.annotations.items():
            cv2.putText(self.image, f"{tile}", px, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        # Show buffer
        cv2.putText(self.image, f"Input: {self.input_buffer}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


if __name__ == '__main__':
    from pathlib import Path

    img_path = Path("C:\\Users\\JM\\Documents\\JM-codeworld\\LSS_automation\\scouter_agent\\temp\\skeleton_image.png")
    image = cv2.imread(str(img_path))

    # Example detected corners (replace with actual detection output)
    detected_corners = [(100, 120), (200, 150), (300, 180)]  # Replace with actual

    annotator = CalibrationAnnotator(image, detected_corners)
    labeled_pairs = annotator.annotate()

    print("Final annotations:")
    for px, tile in labeled_pairs:
        print(f"{px} => {tile}")
