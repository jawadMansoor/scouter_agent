import cv2
import numpy as np
import subprocess
import pytesseract
import asyncio
import multiprocessing
import subprocess
import time
from datetime import datetime

# Function to capture screen using ADB
def capture_screen(r,c):
    subprocess.call(f"adb exec-out screencap -p > ../../temp/screen_{r}_{c}.png", shell=True)
    return ignore_borders(cv2.imread(f"../../temp/screen_{r}_{c}.png"))

def continuous_screenshots(stop_event, screenshot_interval=0.1):
    screenshot_count = 0
    while not stop_event.is_set():
        # Capture screenshot
        filename = f"""screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.png"""
        subprocess.call(f"adb exec-out screencap -p > ../../temp/{filename}.png", shell=True)
        print(f"Captured {filename}")
        screenshot_count += 1

        # Wait for the next screenshot
        time.sleep(screenshot_interval)

def ignore_borders(image):
    image_shape = image.shape
    # print(image_shape)
    clip_right = int(0.037 * image_shape[0])
    clip_left = int(0.04 * image_shape[0])
    clip_bot = int(0.08* image_shape[1])
    clip_top = int(0.08 * image_shape[1])
    image_out = image[clip_top:-clip_bot,clip_right:-clip_left,:]
    # print(image_out.shape)
    return image_out

def swipe(x1, y1, x2, y2, duration=500):
    command = f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}"
    print(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
    subprocess.call(command)


def scroll_map(stop_event, swipe_interval=0.1):
    tasks = []
    x1 = 500
    x2 = 300
    y1 = 341
    y2 = int((x1 - x2) * -0.495726496 * 1.005 + y1)

    scroll_delay = 100  # Delay between swipes (in seconds)
    screenshot_delay = 20  # Delay between screenshots (in seconds)
    screenshot_count = 0  # Counter for screenshot filenames

    while not stop_event.is_set():  # Scroll 5 times
        # Swipe right (adjust coordinates as needed)
        swipe(x1, y1, x2, y2, scroll_delay)
        time.sleep(swipe_interval)


# Main function to run the program
def main():
    # Create a stop event to signal when to stop the processes
    stop_event = multiprocessing.Event()

    # Create processes for screen capture and swiping
    capture_process = multiprocessing.Process(
        target=continuous_screenshots,
        args=(stop_event,)
    )
    swipe_process = multiprocessing.Process(
        target=scroll_map,
        args=(stop_event,)
    )

    # Start the processes
    capture_process.start()
    swipe_process.start()

    try:
        # Let the processes run for a while (e.g., 10 seconds)
        print("test")
    except KeyboardInterrupt:
        print("Stopping processes...")
    finally:
        # Signal the processes to stop
        stop_event.set()

        # Wait for the processes to finish
        capture_process.join()
        swipe_process.join()

        print("All processes stopped.")

# Run the program
if __name__ == "__main__":
    main()



# #Display the image
# def show_screen(image):
#     window_name= "screen"
#     cv2.imshow(window_name, image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
# def read_text(tile):
#     return None
#
# def swipe_right():
#     x1 = 500
#     x2 = 300
#     y1 = 341
#     y2 = int((x1 - x2) * -0.495726496 * 1.005 + y1)
#     swipe(x1, y1, x2, y2, 200)
#
# def swipe_bot():
#     x1 = 500
#     x2 = 300
#     y1 = 341
#     y2 = int((x1 - x2) * 0.495726496 * 1.005 + y1)
#     swipe(x2, y2, x1, y1, 200)
#
# def swipe_left():
#     x1 = 500
#     x2 = 300
#     y1 = 341
#     y2 = int((x1 - x2) * -0.495726496 * 1.005 + y1)
#     swipe(x2, y2, x1, y1, 200)
#
# def map_to_right_edge(r):
#     # Main loop
#     for c in range(381):
#         screen = capture_screen(r, c)
#         map_tile = ignore_borders(screen)
#         # show_screen(map_tile)
#         swipe_right()
#
# def map_to_next_row():
#     for n in range(5):
#         swipe_bot()
#
#
# def map_to_left_edge(r):
#     for c in range(381):
#         screen = capture_screen(r, c)
#         map_tile = ignore_borders(screen)
#         # show_screen(map_tile)
#         swipe_left()
#
# def map_arena():
#     for r in range(381):
#         if r%2==0:
#             map_to_right_edge(r)
#             swipe_bot()
#         else:
#             map_to_left_edge(r)
#             swipe_bot()
#
#
# map_arena()
#
# # read text on image
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#
# tile = cv2.imread(f"../../temp/screen_{0}_{0}.png")
# map_tile = ignore_borders(tile)
# gray = cv2.cvtColor(map_tile, cv2.COLOR_BGR2GRAY)
# _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
# mask = np.ma.masked_array(gray>250, gray)
# new_gray = np.ma.masked_where(np.ma.getmask(mask), gray)
# # gray = cv2.cvtColor(map_tile, cv2.COLOR_BGR2GRAY)
# _, binary_2 = cv2.threshold(new_gray, 150, 255, cv2.THRESH_BINARY)
# # show_screen(binary)
# # show_screen(gray)
# # show_screen(map_tile)
# # show_screen(binary_2)
# text = pytesseract.image_to_string(binary, lang='eng')
#
# import easyocr
#
# # Initialize the EasyOCR reader
# reader = easyocr.Reader(['en', 'ru'])
# results = reader.readtext(map_tile)
# for (bbox, text, confidence) in results:
#     print(f"Text: {text}, Confidence: {confidence}")
#
#
# print("Extracted Text:")
# print(text)
# text = pytesseract.image_to_string(binary_2, lang='eng')
#
# print("Extracted Text:")
# print(text)