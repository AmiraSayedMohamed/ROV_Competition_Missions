import cv2
import torch
import time
import numpy as np

# Load MiDaS model
model_type = "DPT_Hybrid"  # MiDaS v3 - Base
midas = torch.hub.load("intel-isl/MiDaS", model_type)

# Move model to GPU
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()

# Load transforms
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.dpt_transform

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame from webcam.")
        break

    start = time.time()

    # Convert frame to RGB and apply transform
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = transform(img).unsqueeze(0).to(device)

    # Debugging: Print input shape
    print("Input shape after transform:", img.shape)

    # Fix input tensor shape if necessary
    if img.ndim == 5:  # If the tensor has 5 dimensions
        img = img.squeeze(1)  # Remove the extra dimension
    print("Input shape after fixing:", img.shape)

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

    # Debug: Print depth map values before normalization
    print("Depth map min:", depth_map.min(), "max:", depth_map.max())

    # Normalize the depth map to the range [0, 255] for visualization
    depth_map = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    # Apply a colormap to the depth map for better visualization
    depth_map_colored = cv2.applyColorMap(depth_map, cv2.COLORMAP_JET)

    # Calculate FPS
    end = time.time()
    totalTime = end - start
    fps = 1 / totalTime

    # Display FPS on the depth map
    cv2.putText(depth_map_colored, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Show the depth map and original frame
    cv2.imshow("Depth Map", depth_map_colored)
    cv2.imshow("Original Frame", frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()