import cv2
import numpy as np
import json
import pandas as pd
import openpyxl as px

print("Mapping module loaded")

def run_mapping(excel_file_path):
    print("Running Mapping Mission")
    print(f"Using Excel file: {excel_file_path}")

    # Function to display an image in a properly sized window
    def display_image(image, window_name, display_time, position=None, size=None):
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        if size is not None:
            cv2.resizeWindow(window_name, size[0], size[1])
        if position is not None:
            cv2.moveWindow(window_name, position[0], position[1])
        cv2.imshow(window_name, image)
        cv2.waitKey(display_time)

    # Load the table image
    table_image_path = 'mapping/table.jpg'  # Update this path if necessary
    print(f"Loading table image from: {table_image_path}")
    table_image = cv2.imread(table_image_path)
    if table_image is None:
        print("Error: Could not load table image.")
        return

    # Load the map image
    image_path = 'mapping/map.jpg'  # Update this path if necessary
    print(f"Loading map image from: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load map image.")
        return

    # Get screen dimensions
    screen_width = 1920
    screen_height = 1080

    # Define the left half of the screen
    left_half_width = screen_width // 2
    left_half_height = screen_height
    left_half_position = (0, 0)

    # Display the table image in the left half of the screen (initial display)
    table_window_size = (left_half_width, left_half_height)
    display_image(table_image, 'Table', 5000, left_half_position, table_window_size)  # Display for 5 seconds

    # Display the map image in the left half of the screen
    map_window_size = (left_half_width, left_half_height)
    display_image(image, 'Map', 2000, left_half_position, map_window_size)  # Display for 2 seconds

    # Load the regions data from the JSON file
    regions_file = 'mapping/regions_data.json'  # Update this path if necessary
    print(f"Loading regions data from: {regions_file}")
    try:
        with open(regions_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not load regions data from {regions_file}.")
        return

    no_region_point = data["no_region_point"]
    regions = data["regions"]

    # Load the table data from the selected Excel file
    print(f"Loading Excel data from: {excel_file_path}")
    try:
        df = pd.read_excel(excel_file_path, engine='openpyxl')
    except FileNotFoundError:
        print(f"Error: Could not load Excel data from {excel_file_path}.")
        return

    print(df.columns)  # Debugging: Print column names

    # Convert the Excel data to a dictionary
    year_data = df.set_index('Year').to_dict(orient='index')

    # Define red color in BGR format
    red_color = (0, 0, 255)

    # Function to draw a specific region's polyline in red
    def draw_region(image, region_name, regions):
        if region_name in regions:
            region_data = regions[region_name]
            polyline_points = region_data["points"]
            polyline_points_np = np.array(polyline_points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [polyline_points_np], isClosed=False, color=red_color, thickness=5)

    # Function to get the highest region (smallest Y-coordinate) with "Y"
    def get_highest_region(regions_to_draw, regions):
        highest_region = None
        min_y = float('inf')
        for region_name, value in regions_to_draw.items():
            if value == "Y" and region_name in regions:
                text_point = regions[region_name]["text_point"]
                if text_point and text_point[1] < min_y:
                    min_y = text_point[1]
                    highest_region = region_name
        return highest_region

    # Main loop to iterate through the years
    for year, regions_to_draw in year_data.items():
        print(f"Year: {year}, Type: {type(year)}")  # Debugging
        current_image = image.copy()
        if any(value == "Y" for value in regions_to_draw.values()):
            for region_name, value in regions_to_draw.items():
                if value == "Y":
                    draw_region(current_image, region_name, regions)
            highest_region = get_highest_region(regions_to_draw, regions)
            if highest_region:
                text_point = regions[highest_region]["text_point"]
                cv2.putText(current_image, str(year), tuple(text_point), cv2.FONT_HERSHEY_SIMPLEX, 1.0, red_color, 2)
            display_image(current_image, 'Map', 2000, left_half_position, map_window_size)
        else:
            cv2.putText(current_image, str(year), tuple(no_region_point), cv2.FONT_HERSHEY_SIMPLEX, 1.0, red_color, 2)
            display_image(current_image, 'Map', 2000, left_half_position, map_window_size)

    # Close the map window after all years are processed
    cv2.destroyWindow('Map')

    # Display the table image again for 3 seconds
    display_image(table_image, 'Table', 3000, left_half_position, table_window_size)

    # Close the table window after 3 seconds
    cv2.destroyWindow('Table')

    # Close all OpenCV windows (if any are still open)
    cv2.destroyAllWindows()