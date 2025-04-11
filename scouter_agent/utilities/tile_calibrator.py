import cv2
from scouter_agent.utilities.hough_corner_detector import visualize_hough_and_corners
from scouter_agent.utilities.calibration_gui_tool import CalibrationAnnotator

skeleton_image_path = "C:\\Users\\JM\Documents\\JM-codeworld\\LSS_automation\\scouter_agent\\temp\\skeleton_image.png"

if __name__ == "__main__":
    image_path = skeleton_image_path  # or use your original color image
    image = cv2.imread(image_path)

    skeleton_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    corners = visualize_hough_and_corners(skeleton_gray)

    annotator = CalibrationAnnotator(image, corners)
    annotations = annotator.annotate()

    print("📝 Final annotations:")
    for px, tile in annotations:
        print(f"{px} => {tile}")
