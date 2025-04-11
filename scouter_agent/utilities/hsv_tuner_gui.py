import cv2
import numpy as np

class HSVTuner:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise FileNotFoundError("Image not found at given path.")

        self.hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        self.window_name = "HSV Tuner"

        cv2.namedWindow(self.window_name)
        self.create_trackbars()

    def create_trackbars(self):
        # Create 6 trackbars for lower and upper HSV bounds
        cv2.createTrackbar("Lower H", self.window_name, 0, 180, lambda x: None)
        cv2.createTrackbar("Lower S", self.window_name, 0, 255, lambda x: None)
        cv2.createTrackbar("Lower V", self.window_name, 200, 255, lambda x: None)
        cv2.createTrackbar("Upper H", self.window_name, 180, 180, lambda x: None)
        cv2.createTrackbar("Upper S", self.window_name, 50, 255, lambda x: None)
        cv2.createTrackbar("Upper V", self.window_name, 255, 255, lambda x: None)

    def get_trackbar_values(self):
        lh = cv2.getTrackbarPos("Lower H", self.window_name)
        ls = cv2.getTrackbarPos("Lower S", self.window_name)
        lv = cv2.getTrackbarPos("Lower V", self.window_name)
        uh = cv2.getTrackbarPos("Upper H", self.window_name)
        us = cv2.getTrackbarPos("Upper S", self.window_name)
        uv = cv2.getTrackbarPos("Upper V", self.window_name)
        return (np.array([lh, ls, lv]), np.array([uh, us, uv]))

    def apply_mask(self, lower, upper):
        mask = cv2.inRange(self.hsv_image, lower, upper)
        result = cv2.bitwise_and(self.image, self.image, mask=mask)
        return mask, result

    def run(self):
        print("Press 'q' to quit.")
        while True:
            lower, upper = self.get_trackbar_values()
            mask, filtered = self.apply_mask(lower, upper)

            combined = np.hstack((self.image, filtered))
            cv2.imshow(self.window_name, combined)
            cv2.imshow("Mask", mask)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                print(f"Final HSV Range:")
                print(f"Lower: {lower.tolist()}\nUpper: {upper.tolist()}")
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python hsv_tuner.py <image_path>")
    else:
        tuner = HSVTuner(sys.argv[1])
        tuner.run()
