import cv2
import math

# Define the scale factor (calibrate this for your setup)
CM_PER_PIXEL = 30 / 437  # Replace with your own measurement!

points = []
reference_length = 44.0  # Fixed reference length in cm
ratio = 1.0  # Initial ratio

# Load the image
image_path = "ShipWreck.jpg"  # Replace with your image path
frame = cv2.imread(image_path)
if frame is None:
    print("Error: Could not load image.")
    exit()

height, width, _ = frame.shape  # Get image dimensions

# Function to handle mouse clicks
def draw_circle(event, x, y, flags, params):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) == 2:
            points = []
        points.append((x, y))  # Store points as tuples
        update_display()

# Function to update the image display
def update_display():
    display_frame = frame.copy()

    # Draw selected points
    for pt in points:
        cv2.circle(display_frame, pt, 6, (0, 255, 0), -1)  # Green points

    # Draw line and display measurements
    if len(points) == 2:
        pt1, pt2 = points
        cv2.line(display_frame, pt1, pt2, (0, 255, 255), 2)  # Yellow line

        pixel_distance = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
        cm_distance = pixel_distance * CM_PER_PIXEL  # Convert to cm

        # Set text position to the center
        text_x = width // 2
        text_y = height // 2

        # Display measured distance in white
        text = f"{cm_distance:.2f} cm"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        cv2.putText(display_frame, text, (text_x - text_size[0] // 2, text_y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # White text

        # If ratio is calculated, display the corrected distance in bold red
        if ratio != 1.0:
            corrected_distance = cm_distance * ratio
            corrected_text = f"Corrected: {corrected_distance:.2f} cm"
            corrected_text_size = cv2.getTextSize(corrected_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)[0]

            cv2.putText(display_frame, corrected_text, (text_x - corrected_text_size[0] // 2, text_y + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)  # Bold red text

    cv2.imshow("Image", display_frame)

# Set up window and mouse callback
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", draw_circle)

update_display()  # Show the image initially

while True:
    key = cv2.waitKey(1)

    if key == ord('q'):  # Press 'q' to calculate the ratio
        if len(points) == 2:
            pt1, pt2 = points
            pixel_distance = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
            cm_distance = pixel_distance * CM_PER_PIXEL
            ratio = reference_length / cm_distance  # Calculate the ratio
            print(f"Ratio calculated: {ratio:.2f}")
            update_display()  # Update the image with corrected measurement

    if key == ord('s'):  # Press 's' to save the annotated image
        save_path = "annotated_image.jpg"
        cv2.imwrite(save_path, frame)
        print(f"Annotated image saved as {save_path}")

    if key == 27:  # Press 'Esc' to exit
        break

cv2.destroyAllWindows()
