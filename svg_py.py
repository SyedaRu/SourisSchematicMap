from svgpathtools import svg2paths
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import math,svgwrite
import pandas as pd
import xml.etree.ElementTree as ET
import os
from pdfdocument.document import PDFDocument

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, keyboard
import pyautogui
import pdfkit

path_to_value_file = "C:/Users/syedaR/Desktop/Souris/2023 NaturalFlowSchematic.xlsx"
base_svg_path = "Asset12.svg"
scale_amount = 0.001

### Coordinates of each location within the specific base SVG
### These names should be the same as the "Name" column of the Excel data file
location_coordinates = {
    0: {
        "Below Rafferty": [(0, 21)],
        "Unlabeled Numbers below Boundary Dam": [(2, 3)],
        "Short Creek near Roche Percee": [(5, 7)],
        "Sherwood Recorded Flow": [(10, 11)],
        'Moose Mountain Creek below Grant Devine (used to be "near Oxbow")': [(16, 17)],
    },
    1: {
        "Grant Devine Reservoir Diversion": [(0, 11)],
        "Moose Mountain Creek above Grant Devine": [(1, 9)],
        "Moose Mountain Creek below Moose Mountain Lake": [(4, 7)],
    },
    
    3: {
        "Rafferty to Boundary Reservoir Pumpage": [(7, 10),(0, 4), (2, 3), (8, 9),  (6, 11), (5, 12)],
    },
    4: {
        "Yellow Grass Ditch & Tatagwa Lake Contribution": [(1, 4)],
    },
    5: {
        "Nickel Lake & Wayburn Diversion": [(3, 4)],
    },
    6: {
        'Souris River near Ralph (used to be "near Halbrite")': [(0, 3)],
        "Rafferty Reservoir & Estevan Usage": [(1, 2)],
    },
    7: {
        "Moose Mountain Lake Diversion": [(0, 2)],
    },
    2: {
        "Boundary Reservoir Diversion Canal": [(11, 18),(9, 20), (10, 19),  (12, 17), (13, 16), (14, 15)],
        "Long Creek near Maxim": [(4, 6)],
        "Long Creek at Western Crossing": [(3, 7)],
        "Net Gain in North Dakota": [(0, 2)],
        "Long Creek near Noonan": [(9, 23)],
    },
    8: {
        "Boundary Reservoir Diversion": [(2, 3)],
    }
}

##### Functions for SVG maniplation

"""Function to calculate the Euclidean distance between two points"""
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

"""Function to calculate new coordinates of a line for a given ratio
    x1,y1: x and y coordinates of start point of the line
    x2,y2: x and y coordinates of end point of the line
    ratio: 
""" 
def adjust_coordinates(x1, y1, x2, y2, ratio):
    x1_new = x1 + (x2 - x1) * (1 - ratio) / 2
    y1_new = y1 + (y2 - y1) * (1 - ratio) / 2
    x2_new = x2 - (x2 - x1) * (1 - ratio) / 2
    y2_new = y2 - (y2 - y1) * (1 - ratio) / 2
    return (x1_new, y1_new, x2_new, y2_new)


"""Breaks a complex number into its real (x) and imaginary (y) parts."""
def get_xy(point):
   return point.real, point.imag

def path_to_points(path):
    """
    Converts a list of path segments into a list of unique 2D points.

    Parameters:
        path (list): A list of path segment objects. Each segment is expected to have a
                     `start` attribute, which is a complex number representing the starting
                     point of the segment.

    Returns:
        list: A list of tuples `(x, y)`, where:
              - `x` is the real part of the segment's start point.
              - `y` is the imaginary part of the segment's start point.
              The list contains unique points without consecutive duplicates.


     # Example path with segments
        path = [
            Segment(1 + 2j),
            Segment(3 + 4j),
            Segment(3 + 4j),  # Duplicate start point
            Segment(5 + 6j)
        ]

        points = path_to_points(path)
        print(points)  # Output: [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]
        ```

    """
    points = []
    for segment in path:
        start_point = (segment.start.real, segment.start.imag)
           
        # Add the start point if it's not already in the list
        if not points or points[-1] != start_point:
            points.append(start_point)
   
    return points

# This function gets the decameter value when given the dataframe and name of location
def get_value_by_name(df, name):
    # Using boolean indexing to filter the DataFrame
    value = df.loc[df["Name"] == name, "Cubic Decametres"]
    if not value.empty:
        return value.iloc[0]
    else:
        return 0

def change_svg_points(paths, coor,value_df, scale):
    """
    Updates the path coordinates based on scaling the distances between specified locations.

    Parameters:
        paths (list): List of SVG path objects with start coordinates as complex numbers.
        coor (dict): Dictionary containing the indices of path segments that represent locations.
        value_df (DataFrame): DataFrame containing the desired distances between points.
        scale (float): Scaling factor to adjust the distances between points.

    Returns:
        None: The function updates the `paths` in place by modifying the start coordinates.
    
    Notes:
        - The function calculates the current distance between two points, then adjusts 
          the coordinates according to the desired distance from `value_df` scaled by `scale`.
        - Special handling is applied to the "Rafferty to Boundary Reservoir Pumpage" and 
          "Net Gain in North Dakota" locations to update additional path points.
    """
    for object_idx, object in coor.items():
        for location, coords in object.items():
            for indices in coords:
                i = indices[0]
                j = indices[1]   

                # get x and y from complex numbers
                point1 = get_xy(paths[object_idx][i].start)
                point2 = get_xy(paths[object_idx][j].start)

                # Calculate current distance between the two points
                current_distance = calculate_distance(*point1, *point2)

                # Get the desired distance distance between two points(representing the volume at the location)
                desired_distance = int(get_value_by_name(value_df,location))* scale

                # Calculate the ratio
                ratio = desired_distance / current_distance
        
                # Adjust coordinates and separate the two points
                A1, A2 = adjust_coordinates(*point1, *point2, ratio)[:2], adjust_coordinates(*point1, *point2, ratio)[2:]

                # Convert the points into complex number to be able to draw it using the svg package
                paths[object_idx][i].start = complex(*A1)
                paths[object_idx][j].start = complex(*A2)
                
                # Extra points adjsted for the two specific locations
                if location == "Rafferty to Boundary Reservoir Pumpage":
                    if indices[0] == 0:
                        paths[object_idx][13].start = complex(*A1) 
                elif location == "Net Gain in North Dakota":
                    paths[object_idx][24].start = complex(*A1)

        
def draw_pie_chart(dwg, center, radius, data, colors, labels):
    """
    Draws a pie chart with arrows, labels, and a side label showing Canada's diversion percentage.
    
    Parameters:
        dwg (svgwrite.Drawing): An SVG drawing object used to draw the pie chart.
        center (tuple): The (x, y) coordinates for the center of the pie chart.
        radius (float): The radius of the pie chart.
        data (list): A list of values representing the size of each pie slice.
        colors (list): A list of colors corresponding to each pie slice.
        labels (list): A list of labels corresponding to each pie slice. Each label should include both text and a numerical part.

    Returns:
        None: The function draws the pie chart directly on the provided SVG drawing (`dwg`).
    
    Description:
        - This function draws a pie chart by iterating over the `data` list, calculating the slice angle for each value based on its proportion of the total.
        - For each slice, it draws a path to represent the pie slice, with a white stroke between slices for clarity.
        - Arrows are drawn from each slice to its corresponding label, which is split into two lines: the text part and the numerical part.
        - It also adds a side label for Canada's diversion, showing the percentage of the natural flow diverted by Canada.

    Example:
        ```python
        import svgwrite
        import math

        # Create an SVG drawing object
        dwg = svgwrite.Drawing('pie_chart.svg', profile='tiny')

        # Define pie chart parameters
        center = (150, 150)
        radius = 100
        data = [97,604, 120,395]
        colors = ['blue', 'red']
        labels = ['Flow received by the US 120,395 (97,604)', 'Canada net depletion 97,604 (60,304)']

        # Draw pie chart
        draw_pie_chart(dwg, center, radius, data, colors, labels)

        # Save the SVG file
        dwg.save()
        ```
    """
    # Total portion of the pie (Canada net depletion + Flow received by USA)
    total = sum(data)
    start_angle = 0

    # Loops through the two data values and creates its slice on the pie 
    for i, value in enumerate(data):
        slice_angle = 360 * (value / total)
        end_angle = start_angle + slice_angle

        # Convert angles to radians
        mid_angle = start_angle + (slice_angle / 2)
        mid_rad = math.radians(mid_angle)

        # Calculate the coordinates for the arc
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        start_x = center[0] + radius * math.cos(start_rad)
        start_y = center[1] + radius * math.sin(start_rad)
        end_x = center[0] + radius * math.cos(end_rad)
        end_y = center[1] + radius * math.sin(end_rad)

        # Large arc flag
        large_arc_flag = 1 if slice_angle > 180 else 0

        # Path description of a circle
        path_data = [
            f"M{center[0]},{center[1]}",
            f"L{start_x},{start_y}",
            f"A{radius},{radius} 0 {large_arc_flag},1 {end_x},{end_y}",
            "Z"
        ]

        # Add the pie slice with a stroke (white line between slices)
        dwg.add(dwg.path(d=" ".join(path_data), fill=colors[i], stroke='white', stroke_width=1))

        # Calculate arrow and label positions
        arrow_start_x = center[0] + radius * 0.8 * math.cos(mid_rad)
        arrow_start_y = center[1] + radius * 0.8 * math.sin(mid_rad)
        arrow_end_x = center[0] + radius * 1.6 * math.cos(mid_rad)
        arrow_end_y = center[1] + radius * 1.6 * math.sin(mid_rad)

        # Add arrow line
        dwg.add(dwg.line(start=(arrow_start_x, arrow_start_y), end=(arrow_end_x, arrow_end_y), 
                         stroke='black', stroke_width=0.5, marker_end='url(#arrow)'))

        # Add label
        label_x = arrow_end_x + (5 if math.cos(mid_rad) >= 0 else -10)
        label_y = arrow_end_y + (7 if math.sin(mid_rad) >= 0 else -5)

        # Split the label into two parts: text and numbers
        text_part = labels[i].rsplit(' ', 2)[0]  # Everything before the first number
        number_part = ' '.join(labels[i].rsplit(' ', 2)[1:])  # The last number and parentheses

        # Add the text part on the first line
        dwg.add(dwg.text(text_part, insert=(label_x, label_y), fill='black', font_size='6px'))
        dwg.add(dwg.text(number_part, insert=(label_x, label_y + 8), fill='black', font_size='6px'))

        # Update start angle for the next slice
        start_angle = end_angle

    ## Prepare the Box and info
    # Calculate the percentage of Canada's diversion
    canada_net = data[1] 
    canada_percentage = (canada_net / total) * 100

    # Add side label with a box split into two lines
    line1_text = f"Canada diverted"
    line2_text = f"{canada_percentage:.1f}% of the"
    line3_text = "Natural flow"
    
    # Adjust the position of the box as needed
    side_label_x = center[0] + radius + 20 
    side_label_y = center[1] 
    
    # Determine the box size based on the text size
    box_padding = 5
    text_width = 50  # Fixed width to accommodate the longest line
    box_height = 30  # Adjusted for two lines of text

    # Draw the box
    dwg.add(dwg.rect(insert=(side_label_x - box_padding, side_label_y - 13), 
                     size=(text_width + box_padding * 2, box_height + box_padding * 2), 
                     fill='lightgray', stroke='black'))

    # Add the text inside the box
    dwg.add(dwg.text(line1_text, insert=(side_label_x, side_label_y), fill='black', font_size='8px'))
    dwg.add(dwg.text(line2_text, insert=(side_label_x+4, side_label_y + 10), fill='black', font_size='8px'))
    dwg.add(dwg.text(line3_text, insert=(side_label_x+4, side_label_y + 20), fill='black', font_size='8px'))



def draw_svg(paths, svg_filename, location_coordinates, data, y_shift=100):
    data.set_index("Name",inplace = True)    

    # Initialize drawing
    dwg = svgwrite.Drawing(svg_filename + ".svg", profile='full', size=(1000, 1000))

    # Define an arrow marker
    arrow_marker = dwg.marker(insert=(2, 2), size=(4, 4), orient="auto")
    arrow_marker.add(dwg.path(d="M0,0 L0,4 L4,2 Z", fill='black'))
    dwg.defs.add(arrow_marker)

    # Variables to track bounding box
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    # Draw the paths and labels
    for i, path in enumerate(paths):
        points = path_to_points(paths[i])
        # Adjust the y-coordinates by adding y_shift
        # adjusted_points = [(x, y + y_shift) for x, y in points]
        polygon = dwg.polygon(
            points=points,
            fill="#d3d3d3",
            stroke='gray',
            stroke_miterlimit=10,
            stroke_opacity=0.4
        )
        dwg.add(polygon)
        # Update bounding box
        for (x, y) in points:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

    for object_idx, object in location_coordinates.items():
        for location, coords in object.items():
            for indices in coords[:1]:
                i = indices[0]
                j = indices[1]

                x1, y1 = get_xy(paths[object_idx][i].start)
                x2, y2 = get_xy(paths[object_idx][j].start)

                # Adjusting specific arrow positions
                if object_idx == 1 and location == "Grant Devine Reservoir Diversion":
                    y1 -= 5
                    y2 -= 5
                if location == "Below Rafferty":
                    x1 += 12
                    y1 += (4)
                    x2 += 3
                    y2 += 8
                if location == "Nickel Lake & Wayburn Diversion":
                    x1 += 0
                    y1 += -7
                    x2 += -3
                    y2 += -2
                
                if location == 'Souris River near Ralph (used to be "near Halbrite")':
                    x1 += 7
                    y1 += 5
                    x2 += 5
                    y2 += 8
                if location == 'Short Creek near Roche Percee':
                    x1 += -4
                    y1 += 20
                    x2 += -8
                    y2 += 20
                if location == 'Moose Mountain Creek below Grant Devine (used to be "near Oxbow")':
                    x1 += 0
                    y1 += 10
                    x2 += 4
                    y2 += 10
                if location == "Moose Mountain Lake Diversion":
                    x1 += -2
                    y1 += -4
                    x2 += -2
                    y2 += -2
                if location == "Unlabeled Numbers below Boundary Dam":
                    x1 += 0
                    y1 += -2
                    x2 += 0
                    y2 += -2
               
                ## Arrows
                arrow_length = 15

                # Calculate the distance between the points
                current_distance = calculate_distance(x1, y1, x2, y2)

                if current_distance == 0:
                    # Handle zero distance case
                    current_distance = 1

                # Calculate the ratio to move the arrow a bit further apart than the points
                new_distance = current_distance + 8
                ratio = (new_distance) / current_distance

                x1,y2,x2,y2 = adjust_coordinates(x1,y1,x2,y2, ratio)
              
                # Calculate arrow start positions based on fixed arrow length
                arrow_start_x1 = x1 + (x1 - x2) * (arrow_length / new_distance)
                arrow_start_y1 = y1 + (y1 - y2) * (arrow_length / new_distance)

                arrow_start_x2 = x2 + (x2 - x1) * (arrow_length / new_distance)
                arrow_start_y2 = y2 + (y2 - y1) * (arrow_length / new_distance)

                # Label position from the arrow adjustment
                label_offset_x = 5
                label_offset_y = -5
                line_height = 6
                
                # Label and values to display
                deca_value = data.at[location, 'Cubic Decametres']
                acre_value = data.at[location, 'Acre-feet']
                name_to_display = data.at[location, 'Name to show']

                label_to_display = name_to_display + " " + f"{deca_value:,}" + " (" + f"{round(float(acre_value)):,}" + ")"
                split_label = label_to_display.split()
                combined_last_two = " ".join(split_label[-2:])
                new_split_label = split_label[:-2] +[(combined_last_two)]

                # Position the labels of each location
                # These can be used the reposition the labels if any is overlapping or in the wrong position
                for idx, char in enumerate(new_split_label):
                    label_x = arrow_start_x1 + label_offset_x
                    label_y = arrow_start_y1 + label_offset_y + idx * (line_height) + 5

                    #`object_idx` corresponds to the keys in the `location_coordinates` dictionary 
                    # at the top of this file. This dictionary contains specific indices as its keys,
                    # each representing a location.
                    if object_idx == 0:
                        label_x += 0
                        label_y += 10 -3
                    if object_idx == 1:
                        label_x += 0
                        label_y += - 8 
                    if location == "Moose Mountain Lake Diversion":
                        label_x += -35
                        label_y += -33
                    if location == "Moose Mountain Creek below Moose Mountain Lake":
                        label_x += -3
                        label_y += -5
                    if location == 'Moose Mountain Creek below Grant Devine (used to be "near Oxbow")':
                        label_x += -2
                        label_y += -18
                    if location == "Unlabeled Numbers below Boundary Dam":
                        label_x += 25
                        label_y += 3
                    if location == "Boundary Reservoir Diversion":
                        label_x += 20
                        label_y += 10
                    if location == "Yellow Grass Ditch & Tatagwa Lake Contribution":
                        label_x += -3
                        label_y += -40
                    if location == 'Souris River near Ralph (used to be "near Halbrite")':
                        label_x -= 20
                        label_y += 0
                    if object_idx == 2:
                        label_x -= 10
                        label_y += 5
                    if location == "Nickel Lake & Wayburn Diversion":
                        label_x += -25
                        label_y += -40
                    if location == "Rafferty Reservoir & Estevan Usage":
                        label_x = arrow_start_x2 + label_offset_x -30
                        label_y = arrow_start_y2 + label_offset_y + idx * line_height - 35
                    if location == "Below Rafferty":
                        label_x += -15
                        label_y += -8
                    if location == 'Short Creek near Roche Percee':
                        label_x += 42
                        label_y += -10
                    if location == 'Grant Devine Reservoir Diversion':
                        label_x += -1
                        label_y += -23
                    if location == "Rafferty to Boundary Reservoir Pumpage":
                        label_x += -9
                        label_y += 2
                    if location == "Long Creek near Maxim":
                        label_x += -9
                        label_y += -4
                    if location == "Long Creek near Noonan":
                        label_x += 65
                        label_y += -10
                    if location == "Net Gain in North Dakota":
                        label_x += -10
                        label_y += -2
                    if location == "Boundary Reservoir Diversion Canal":
                        label_x += 10
                        label_y += -7
                    
                    # Drawing in the label
                    dwg.add(dwg.text(char, insert=(label_x, label_y+5), fill='black', font_size='6px'))
                
                #Drawing the two arrows of each location
                dwg.add(dwg.line(start=(arrow_start_x1, arrow_start_y1), end=(x1, y1), stroke='black', stroke_width=0.5, marker_end=arrow_marker.get_funciri()))
                dwg.add(dwg.line(start=(arrow_start_x2, arrow_start_y2), end=(x2, y2), stroke='black', stroke_width=0.5, marker_end=arrow_marker.get_funciri()))

                # Update bounding box with label positions
                min_x = min(min_x, label_x)
                max_x = max(max_x, label_x)
                min_y = min(min_y, label_y)
                max_y = max(max_y, label_y)

    # Calculate the dimensions and center of the bounding box
    width = max_x - min_x + 50
    height = max_y - min_y + 50
    center_x = min_x + width / 2
    center_y = min_y + height / 2

    # Update drawing with centered viewBox
    dwg.viewbox(minx=min_x, miny=min_y, width=width, height=height)
    dwg.add(dwg.g(transform=f'translate({-center_x + width / 2}, {-center_y + height / 2})'))

    # Add the Canada-USA border line
    canada_usa_y = 300  # Adjust this Y position to place the line where it belongs
    dwg.add(dwg.line(start=(0, canada_usa_y), end=(800, canada_usa_y), stroke='black', stroke_width=0.5, stroke_dasharray="5,5"))

    # Label the line as "CANADA - UNITED STATES"s
    dwg.add(dwg.text("CANADA", insert=(270, canada_usa_y - 5), fill='black', font_size='10px'))
    dwg.add(dwg.text("UNITED STATES", insert=(260, canada_usa_y+10), fill='black', font_size='10px'))

    # Add the pie chart
    pie_center = (430, 300)  # Adjust this position to place the pie chart correctly
    pie_radius = 30000 * scale_amount
    
    canada_net = data.at["Canada net Depletions", 'Cubic Decametres']
    us_net = data.at["Flow received by the US",'Cubic Decametres']
    pie_data = [us_net,canada_net]  
    pie_colors = ["blue", "red"]  
    
    country_labels = ["Flow received by the US","Canada net Depletions"]
    pie_labels = list()
    for location in country_labels:
        deca_value = data.at[location, 'Cubic Decametres']
        acre_value = data.at[location, 'Acre-feet']
        name_to_display = data.at[location, 'Name to show']
        label_to_display = name_to_display + " " + f"{deca_value:,}" + " (" + f"{round(float(acre_value)):,}" + ")"
        pie_labels.append(label_to_display)

    # Define arrow marker
    arrow_marker = dwg.marker(insert=(2, 2), size=(4, 4), orient="auto")
    arrow_marker.add(dwg.path(d="M0,0 L0,4 L4,2 Z", fill='black'))
    dwg.defs.add(arrow_marker)
    draw_pie_chart(dwg, pie_center, pie_radius, pie_data, pie_colors,pie_labels)

    
    # Add Title
    dwg.add(dwg.text("SCHEMATIC REPRESENTATION OF 2023 FLOWS IN THE SOURIS RIVER BASIN",
                     insert=(center_x -120, -40), fill='black', font_size='7px', font_weight="bold"))
    dwg.add(dwg.text("ABOVE SHERWOOD, NORTH DAKOTA, U.S.A.",
                     insert=(center_x -80, -30), fill='black', font_size='7px', font_weight="bold"))

    # Add Scale Ruler
    scale_x = 420
    scale_y = 30
    scale_length = 50
    tick_height = 6
    for i in range(0, 101, 20):
        tick_x = scale_x + i * (scale_length / 100)
        tick_y = scale_y + tick_height
        dwg.add(dwg.line(start=(tick_x, scale_y), end=(tick_x, tick_y), stroke='black', stroke_width=1))
        dwg.add(dwg.text(str(i), insert=(tick_x, scale_y - 2), fill='black', font_size='5px'))    
    dwg.add(dwg.line(start=(scale_x, scale_y+tick_height), end=(scale_x + scale_length, scale_y+tick_height), stroke='black', stroke_width=2))
    dwg.add(dwg.text("CUBIC DECAMETRES", insert=(scale_x + scale_length + 10, scale_y + 5), fill='black', font_size='5px'))
    dwg.add(dwg.text("Dam³ x 1000", insert=(scale_x , tick_y + 7), fill='black', font_size='5px'))
    dwg.add(dwg.text("VALUES SHOWN ARE IN CUBIC",
                     insert=(scale_x -5, scale_y - 15), fill='black', font_size='5px'))
    dwg.add(dwg.text("DECAMETRES (ACRE-FEET)",
                     insert=(scale_x -3, scale_y - 10), fill='black', font_size='5px'))
    
    # Acre feet scale
    scale_x = 420
    scale_y = 55
    scale_length = 50 /0.8107
    tick_height = 6
    for i in range(0, 101, 20):
        tick_x = scale_x + i * (scale_length / 100)
        tick_y = scale_y + tick_height
        dwg.add(dwg.line(start=(tick_x, scale_y), end=(tick_x, tick_y), stroke='black', stroke_width=1))
        dwg.add(dwg.text(str(i), insert=(tick_x, scale_y - 2), fill='black', font_size='5px'))    
    dwg.add(dwg.line(start=(scale_x, scale_y+tick_height), end=(scale_x + scale_length, scale_y+tick_height), stroke='black', stroke_width=2))
    dwg.add(dwg.text("ACRE-FEET", insert=(scale_x + scale_length + 10, scale_y + 5), fill='black', font_size='5px'))
    dwg.add(dwg.text("ACRE-FEET x 1000", insert=(scale_x , tick_y + 7), fill='black', font_size='5px'))

    #Save the SVG file
    dwg.save()

"""
Opens the svg in Edge browser and urges user to print it 
This code attempts to automate the printing of an SVG file to PDF using Selenium.
However, it does not currently work properly.
"""
def svgToPdf(path):
    # Start the browser
    driver = webdriver.chrome()  # Or whichever browser you're using

    try:
        # Open the SVG file in the browser
        driver.get(path)

        # Allow the page to load (you can tweak the delay if necessary)
        time.sleep(2)

        # Simulate Ctrl+P to open the print dialog
        driver.execute_script('window.print();')

        # Wait for the print dialog to process (adjust this timing as needed)
        time.sleep(20)

    finally:
        # Always ensure the browser closes after the operation
        driver.quit()


if __name__ == "__main__":
    filename = "SchematicMap"

    # Path to the SVG file that will be manipulated. The SVG file has been  
    # created using Adobe Illustrator which will be adjusted based on data provided
    paths, attribtue = svg2paths(base_svg_path)

    # Read the Excel file containing the data for the schematic
    # The Excel file contains the flow data for each location in the Souris River Basin
    #The names in the "Name" column of the Excel file should match the keys in the `location_coordinates` dictionary
    value_datatframe = pd.read_excel(path_to_value_file, "Natural Flow Schematic",usecols=["Name","Name to show", "Cubic Decametres","Acre-feet"],header=1,nrows=25)
    print(value_datatframe)

    # Change the SVG points based on the data from the Excel file
    change_svg_points(paths,location_coordinates,value_datatframe,scale_amount)

    # Draw the SVG with the adjusted paths and labels
    draw_svg(paths,filename, location_coordinates, value_datatframe)

    # svgToPdf(f'file:///{os.path.abspath(filename + ".svg")}')




