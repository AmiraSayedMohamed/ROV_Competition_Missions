# This code first will measure objects in pixels of a known length
# and i will use this length in pixel to convert to cm to measure new thing in cm in the file named getMeasurement
# from a specific distance , all you need to do is run this file and put two point of the
# object you want to measure length will appear a readinng in pixel use this reading in pixel
# to put in the varible in CM_PER_PIXEL in the file getMeasurement.py you should put the actula lenth in cm divided by the measurement in pixels you have found
## This camera have been calibrated from a 46 cm
import cv2
import math

# List to store selected points
calibration_points = []

cap = cv2.VideoCapture(0)


def draw_circle(event, x, y, flags, params):
    global calibration_points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(calibration_points) == 2:
            calibration_points = []
        calibration_points.append((x, y))  # Store points as tuples


cv2.namedWindow("Calibration")
cv2.setMouseCallback("Calibration", draw_circle)

print("Calibration Instructions:")
print("1. Place an object of a known length (e.g., 30 cm) in view.")
print("2. Click on both ends of the object to measure its length in pixels.")
print("3. Press 'c' to calculate the new CM_PER_PIXEL value.")
print("4. Press 'Esc' to exit.")

while True:
    _, frame = cap.read()

    # Draw calibration points
    for pt in calibration_points:
        cv2.circle(frame, pt, 5, (0, 255, 0), -1)  # Green points

    # Draw a line between the calibration points
    if len(calibration_points) == 2:
        pt1, pt2 = calibration_points
        cv2.line(frame, pt1, pt2, (255, 0, 0), 2)  # Blue line

        # Calculate pixel distance
        pixel_distance = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])

        # Display pixel distance
        cv2.putText(frame, f"Pixel Distance: {pixel_distance:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show the frame
    cv2.imshow("Calibration", frame)
    key = cv2.waitKey(1)

    if key == ord('c') and len(calibration_points) == 2:
        # Input actual length
        actual_length_cm = float(input("Enter the actual length in cm: "))

        # Calculate new CM_PER_PIXEL
        CM_PER_PIXEL = actual_length_cm / pixel_distance
        print(f"Calibration Complete! New CM_PER_PIXEL = {CM_PER_PIXEL:.6f} cm/pixel")
        break

    if key == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
