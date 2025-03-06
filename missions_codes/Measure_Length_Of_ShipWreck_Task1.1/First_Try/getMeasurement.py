# this code is just measure in cm from a 46 cm distance from the camera
import cv2
import math

# Define the scale factor (calibrate this for your setup)
CM_PER_PIXEL = 30 / 400 # Replace with your own measurement!

points = []

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

    # Draw selected points
    for pt in points:
        cv2.circle(frame, pt, 5, (25, 15, 255), -1)  # Draw points

    # Measure and display distance
    if len(points) == 2:
        pt1, pt2 = points
        pixel_distance = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
        cm_distance = pixel_distance * CM_PER_PIXEL  # Convert to cm

        # Calculate text position (center between two points)
        center_x = (pt1[0] + pt2[0]) // 2
        center_y = (pt1[1] + pt2[1]) // 2

        # Draw a background rectangle for better visibility
        text = f"{cm_distance:.2f} cm"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, 2.5, 2)[0]
        text_x = center_x - text_size[0] // 2
        text_y = center_y + text_size[1] // 2

        cv2.rectangle(frame, (text_x - 5, text_y - text_size[1] - 5),
                      (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)

        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN,
                    2.5, (255, 255, 255), 2)  # White text for contrast

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
