# Final Calibraion but it doesn't accurate , the realWorld.py file isn't important

import cv2
import torch
import time
import numpy as np
import math
from torchvision import transforms

# Load MiDaS model
model_type = "DPT_Hybrid"  # MiDaS v3 - Hybrid model
midas = torch.hub.load("intel-isl/MiDaS", model_type)
# Ensure CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using device: {device}')
# Move model to GPU if available
midas.to(device)
midas.eval()

# Custom transform pipeline
transform = transforms.Compose([
    transforms.ToTensor(),  # Convert PIL image or numpy array to tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize
])

# Calibration parameters
REAL_DISTANCE = 30.0  # Real-world distance of the reference object in cm
scaling_factor = 1.0  # Initial scaling factor (will be updated during calibration)

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Global variables for points and measurements
points = []
fixed_measurement = None  # To store the fixed measurement
fixed_depth1 = None  # To store the depth value at the first point
fixed_depth2 = None  # To store the depth value at the second point


def draw_circle(event, x, y, flags, params):
    global points, fixed_measurement, fixed_depth1, fixed_depth2
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) == 2:
            points = []
            fixed_measurement = None  # Reset fixed measurement when new points are selected
            fixed_depth1 = None
            fixed_depth2 = None
        points.append((x, y))


cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", draw_circle)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame from webcam.")
        break

    start = time.time()

    # Convert frame to RGB
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Ensure the image has 3 channels
    if img.shape[2] != 3:
        raise ValueError("Input image must have 3 channels (RGB).")

    # Apply custom transform
    img = transform(img)

    # Add batch dimension
    img = img.unsqueeze(0)

    # Move to device
    img = img.to(device)

    # Run inference
    with torch.no_grad():
        prediction = midas(img)

    # Resize prediction to match original frame size
    prediction = torch.nn.functional.interpolate(
        prediction.unsqueeze(1),
        size=frame.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()

    # Convert prediction to numpy array
    depth_map = prediction.cpu().numpy()

    # Apply blur for stability
    depth_map = cv2.GaussianBlur(depth_map, (5, 5), 0)

    # Normalize the depth map to the range [0, 255]
    depth_map = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    # Apply colormap
    depth_map_colored = cv2.applyColorMap(depth_map, cv2.COLORMAP_JET)

    # Calculate FPS
    end = time.time()
    totalTime = end - start
    fps = 1 / (totalTime + 1e-6)

    # Display FPS
    cv2.putText(depth_map_colored, f"FPS: {fps:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Draw points
    for pt in points:
        cv2.circle(frame, pt, 6, (0, 255, 0), -1)

    # Distance calculation
    if len(points) == 2:
        pt1, pt2 = points
        cv2.line(frame, pt1, pt2, (0, 255, 255), 2)

        # Calculate depth values only once when the points are selected
        if fixed_depth1 is None or fixed_depth2 is None:
            fixed_depth1 = depth_map[pt1[1], pt1[0]]
            fixed_depth2 = depth_map[pt2[1], pt2[0]]

        pixel_distance = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])

        # Use the fixed depth values for calculation
        avg_depth = (fixed_depth1 + fixed_depth2) / 2.0
        cm_distance = pixel_distance * scaling_factor  # Apply scaling factor

        # Store the fixed measurement
        fixed_measurement = cm_distance

    # Display fixed measurement if available
    if fixed_measurement is not None:
        text_x, text_y = frame.shape[1] // 2, frame.shape[0] // 2
        text = f"{fixed_measurement:.2f} cm"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        cv2.putText(frame, text, (text_x - text_size[0] // 2, text_y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show frames
    cv2.imshow("Depth Map", depth_map_colored)
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)

    # Calibration: Press 'c' to calibrate
    if key == ord('c'):
        if len(points) == 2:
            pt1, pt2 = points
            pixel_distance = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
            depth1, depth2 = depth_map[pt1[1], pt1[0]], depth_map[pt2[1], pt2[0]]
            avg_depth = (depth1 + depth2) / 2.0

            # Calculate the scaling factor
            scaling_factor = REAL_DISTANCE / pixel_distance
            print(f"Scaling factor calculated: {scaling_factor:.2f}")

    if key == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()