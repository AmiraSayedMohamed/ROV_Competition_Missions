# This is the first test file that the table we will draw is written in the code not in excel sheet
# you will find the code that do the same thing in the second test2.py file
import cv2
import numpy as np
import json
import time


# Function to display an image in a properly sized window
def display_image(image, window_name, display_time, position=None, size=None):
    # Create the window if it doesn't already exist
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Resize the window if a specific size is provided
    if size is not None:
        cv2.resizeWindow(window_name, size[0], size[1])

    # Move the window to the specified position if provided
    if position is not None:
        cv2.moveWindow(window_name, position[0], position[1])

    # Update the image in the window
    cv2.imshow(window_name, image)
    cv2.waitKey(display_time)  # Display for the specified time


# Load the table image
table_image_path = 'table.jpg'  # Replace with the path to your table image
table_image = cv2.imread(table_image_path)

if table_image is None:
    print("Error: Could not load table image.")
    exit()

# Load the map image
image_path = 'map.jpg'  # Replace with the path to your map image
image = cv2.imread(image_path)

# Check if the image was loaded successfully
if image is None:
    print("Error: Could not load map image.")
    exit()

# Get screen dimensions (adjust these to your screen resolution)
screen_width = 1920  # Replace with your screen width
screen_height = 1080  # Replace with your screen height

# Define the left half of the screen
left_half_width = screen_width // 2
left_half_height = screen_height
left_half_position = (0, 0)  # Top-left corner

# Display the table image in the left half of the screen
table_window_size = (left_half_width, left_half_height)
display_image(table_image, 'Table', 5000, left_half_position, table_window_size)  # Display for 5 seconds

# Display the map image in the left half of the screen
map_window_size = (left_half_width, left_half_height)
display_image(image, 'Map', 2000, left_half_position, map_window_size)  # Display for 2 seconds

# Load the regions data from the JSON file
regions_file = 'regions_data.json'
with open(regions_file, 'r') as f:
    data = json.load(f)

no_region_point = data["no_region_point"]
regions = data["regions"]

# Table data
year_data = {
    "2016": {"Region 1": "N", "Region 2": "N", "Region 3": "N", "Region 4": "N", "Region 5": "N"},
    "2017": {"Region 1": "Y", "Region 2": "N", "Region 3": "N", "Region 4": "N", "Region 5": "N"},
    "2018": {"Region 1": "Y", "Region 2": "N", "Region 3": "N", "Region 4": "N", "Region 5": "N"},
    "2019": {"Region 1": "Y", "Region 2": "N", "Region 3": "N", "Region 4": "N", "Region 5": "N"},
    "2020": {"Region 1": "Y", "Region 2": "Y", "Region 3": "Y", "Region 4": "N", "Region 5": "N"},
    "2021": {"Region 1": "Y", "Region 2": "Y", "Region 3": "Y", "Region 4": "N", "Region 5": "N"},
    "2022": {"Region 1": "Y", "Region 2": "Y", "Region 3": "Y", "Region 4": "N", "Region 5": "N"},
    "2023": {"Region 1": "Y", "Region 2": "Y", "Region 3": "Y", "Region 4": "Y", "Region 5": "N"},
    "2024": {"Region 1": "Y", "Region 2": "Y", "Region 3": "Y", "Region 4": "Y", "Region 5": "N"},
    "2025": {"Region 1": "Y", "Region 2": "Y", "Region 3": "Y", "Region 4": "Y", "Region 5": "N"}
}

# Define red color in BGR format
red_color = (0, 0, 255)  # BGR for red


# Function to draw a specific region's polyline in red (without text points)
def draw_region(image, region_name, regions):
    if region_name in regions:
        region_data = regions[region_name]
        polyline_points = region_data["points"]

        # Draw polyline in red
        polyline_points_np = np.array(polyline_points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(image, [polyline_points_np], isClosed=False, color=red_color, thickness=5)


# Function to get the highest region (smallest Y-coordinate) with "Y"
def get_highest_region(regions_to_draw, regions):
    highest_region = None
    min_y = float('inf')

    for region_name, value in regions_to_draw.items():
        if value == "Y" and region_name in regions:
            text_point = regions[region_name]["text_point"]
            if text_point and text_point[1] < min_y:  # Compare Y-coordinate
                min_y = text_point[1]
                highest_region = region_name
    return highest_region


# Main loop to iterate through the years
for year, regions_to_draw in year_data.items():
    # Create a copy of the original image to draw on
    current_image = image.copy()

    # Check if any region has "Y"
    if any(value == "Y" for value in regions_to_draw.values()):
        # Draw all regions with "Y" in red
        for region_name, value in regions_to_draw.items():
            if value == "Y":
                draw_region(current_image, region_name, regions)

        # Find the highest region with "Y"
        highest_region = get_highest_region(regions_to_draw, regions)
        if highest_region:
            # Write the year text in red at the highest region's text point (larger font size)
            text_point = regions[highest_region]["text_point"]
            cv2.putText(current_image, year, tuple(text_point), cv2.FONT_HERSHEY_SIMPLEX, 1.0, red_color,
                        2)  # Increased font size

        # Display the image in the left half of the screen
        display_image(current_image, 'Map', 2000, left_half_position, map_window_size)  # Display for 2 seconds

    else:
        # No region has "Y", write the year in red at no_region_point (larger font size)
        cv2.putText(current_image, year, tuple(no_region_point), cv2.FONT_HERSHEY_SIMPLEX, 1.0, red_color,
                    2)  # Increased font size
        display_image(current_image, 'Map', 2000, left_half_position, map_window_size)  # Display for 2 seconds

    # Special handling for the year 2025
    if year == "2025":
        # Close the table image window
        cv2.destroyWindow('Table')
        time.sleep(2)  # Wait for 2 seconds

        # Reopen the table image window for 3 seconds
        display_image(table_image, 'Table', 3000, left_half_position, table_window_size)  # Display for 3 seconds

# Close all OpenCV windows
cv2.destroyAllWindows()