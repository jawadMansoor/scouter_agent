import cv2
import numpy as np
import subprocess

# Function to capture screen using ADB
def capture_screen():
    subprocess.call("adb exec-out screencap -p > screen.png", shell=True)
    return cv2.imread("screen.png")

# Function to simulate tap using ADB
def simulate_tap(x, y):
    subprocess.call(f"adb shell input tap {x} {y}", shell=True)

# Example: Detect a specific color (e.g., red) and tap on it
def detect_and_tap(image):
    # Define color range (e.g., red)
    lower_red = np.array([0, 0, 200])
    upper_red = np.array([50, 50, 255])

    # Create a mask for the color
    mask = cv2.inRange(image, lower_red, upper_red)

    # Find contours of the detected color
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Tap on the first detected contour
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        simulate_tap(x + w // 2, y + h // 2)  # Tap the center of the object
        break

# Main loop
while True:
    screen = capture_screen()
    detect_and_tap(screen)