import cv2
import numpy as np
import json  # For saving and loading the regions dictionary

# Initialize variables
points = []  # List to store points for the polyline
regions = {}  # Dictionary to store region polylines and text points
region_counter = 1  # Counter for regions
no_region_point = None  # Point for "No Region" text
# Colors for each region: Red, Green, Orange, Blue, Purple
colors = [
    (0, 0, 255),    # Red (BGR)
    (0, 255, 0),    # Green (BGR)
    (0, 165, 255),  # Orange (BGR)
    (255, 0, 0),    # Blue (BGR)
    (128, 0, 128)   # Purple (BGR)
]
line_thickness = 5  # Increase this value to make the line thicker

# Load the map image
image_path = 'map.jpg'  # Replace with the path to your map image
image = cv2.imread(image_path)

# Check if the image was loaded successfully
if image is None:
    print("Error: Could not load image.")
    exit()

# Resize the image to fit the screen (adjust the scale factor as needed)
scale_percent = 50  # Resize to 50% of the original size
width = int(image.shape[1] * scale_percent / 60)
height = int(image.shape[0] * scale_percent / 65)
resized_image = cv2.resize(image, (width, height))

# Function to map coordinates from resized image to original image
def map_coordinates(x, y):
    original_x = int(x * (image.shape[1] / resized_image.shape[1]))
    original_y = int(y * (image.shape[0] / resized_image.shape[0]))
    return original_x, original_y

# Mouse callback function
def draw_interactive(event, x, y, flags, param):
    global points, resized_image, region_counter, no_region_point

    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button pressed
        if no_region_point is None:  # First point is for "No Region" text
            no_region_point = (x, y)
            cv2.circle(resized_image, no_region_point, 3, (0, 0, 0), -1)  # Black dot for "No Region"
            print("No Region text point saved.")
        else:
            points.append((x, y))  # Add the point to the list
            cv2.circle(resized_image, (x, y), 3, colors[region_counter - 1], -1)  # Draw a small circle
            if len(points) >= 2:  # Draw polyline if there are at least 2 points
                points_np = np.array(points, np.int32).reshape((-1, 1, 2))
                cv2.polylines(resized_image, [points_np], isClosed=False, color=colors[region_counter - 1], thickness=line_thickness)
        cv2.imshow('Map', resized_image)  # Update the display

# Create a window and bind the mouse callback function
cv2.namedWindow('Map')
cv2.setMouseCallback('Map', draw_interactive)

# Display the resized image and wait for the user to draw
print("Click to add points. First point is for 'No Region' text. Then draw polylines for regions and their text points.")
while True:
    cv2.imshow('Map', resized_image)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):  # Save the polyline for the current region
        if len(points) >= 2:
            region_name = f"Region {region_counter}"  # Automatically assign region name
            mapped_points = [map_coordinates(x, y) for (x, y) in points]
            regions[region_name] = {"points": mapped_points, "color": colors[region_counter - 1], "text_point": None}
            print(f"Polyline saved for {region_name}.")
            points = []  # Reset points for the next region
        else:
            print("Not enough points to save a polyline.")

    elif key == ord('d'):  # Save the text point for the current region
        if len(points) == 1:  # Text point is the last point clicked
            region_name = f"Region {region_counter}"  # Current region
            if region_name in regions:
                text_point = map_coordinates(points[0][0], points[0][1])
                regions[region_name]["text_point"] = text_point
                print(f"Text point saved for {region_name} at {text_point}.")
                points = []  # Reset points for the next region
                region_counter += 1  # Move to the next region
                if region_counter > 5:  # Stop after 5 regions
                    print("All 5 regions have been saved.")
                    break
            else:
                print("No region to save the text point.")
        else:
            print("Please click exactly one point for the text.")

    elif key == ord('q'):  # Quit
        break

# Close all OpenCV windows
cv2.destroyAllWindows()

# Save the regions dictionary to a file
regions_file = 'regions_data.json'
with open(regions_file, 'w') as f:
    json.dump({"no_region_point": map_coordinates(*no_region_point), "regions": regions}, f)
print(f"Regions data saved to {regions_file}.")

# Function to redraw everything
def redraw_all():
    global image, resized_image
    # Redraw "No Region" text point
    if no_region_point:
        original_no_region_point = map_coordinates(*no_region_point)
        cv2.circle(image, original_no_region_point, 3, (0, 0, 0), -1)
    # Redraw regions and their text points
    for region_name, region_data in regions.items():
        polyline_points = region_data["points"]
        polyline_color = region_data["color"]
        text_point = region_data["text_point"]
        # Draw polyline
        polyline_points_np = np.array(polyline_points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(image, [polyline_points_np], isClosed=False, color=polyline_color, thickness=line_thickness)
        # Draw text point
        if text_point:
            cv2.circle(image, text_point, 3, polyline_color, -1)
    # Resize and display the image
    resized_image = cv2.resize(image, (width, height))
    cv2.imshow('Map', resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Redraw everything
redraw_all()

# Save the final image
output_path = 'map_with_regions.jpg'
cv2.imwrite(output_path, image)
print(f"Final image saved to {output_path}.")