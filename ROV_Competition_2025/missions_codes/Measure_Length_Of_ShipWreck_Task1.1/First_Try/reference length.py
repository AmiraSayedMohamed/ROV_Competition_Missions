# when you run this code if you put two point it will measure in cm correctly from a distance 46 cm from the camera
# but if you after putting the two point and press q from keyboard he will consider it a measurement
# of a reference object and he will take that measuremen to calcaulat the ratio of the acual measurment length
# in the variable reference length  and multipy this ratio to any new measurement
# but the camera should be fixed after measuring the length of the reference object
import cv2
import math

# Define the scale factor (calibrate this for your setup)
CM_PER_PIXEL = 30 / 437  # Replace with your own measurement!

points = []
reference_length = 30.0  # Fixed reference length in cm
ratio = 1.0  # Initial ratio

cap = cv2.VideoCapture(0)


def draw_circle(event, x, y, flags, params):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) == 2:
            points = []
        points.append((x, y))  # Store points as tuples


cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", draw_circle)

while True:
    _, frame = cap.read()
    height, width, _ = frame.shape  # Get frame dimensions

    # Draw selected points
    for pt in points:
        cv2.circle(frame, pt, 6, (0, 255, 0), -1)  # Green points

    # Draw line and display measurements
    if len(points) == 2:
        pt1, pt2 = points
        cv2.line(frame, pt1, pt2, (0, 255, 255), 2)  # Yellow line connecting points

        pixel_distance = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
        cm_distance = pixel_distance * CM_PER_PIXEL  # Convert to cm

        # Set text position to the center of the window
        text_x = width // 2
        text_y = height // 2

        # Display measured distance in white
        text = f"{cm_distance:.2f} cm"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        cv2.putText(frame, text, (text_x - text_size[0] // 2, text_y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # White text

        # If ratio is calculated, display the corrected distance in bold red
        if ratio != 1.0:
            corrected_distance = cm_distance * ratio
            corrected_text = f"Corrected: {corrected_distance:.2f} cm"
            corrected_text_size = cv2.getTextSize(corrected_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)[0]

            cv2.putText(frame, corrected_text, (text_x - corrected_text_size[0] // 2, text_y + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)  # Bold red text

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)

    if key == ord('q'):  # Press 'q' to calculate the ratio
        if len(points) == 2:
            pt1, pt2 = points
            pixel_distance = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
            cm_distance = pixel_distance * CM_PER_PIXEL
            ratio = reference_length / cm_distance  # Calculate the ratio
            print(f"Ratio calculated: {ratio:.2f}")

    if key == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
