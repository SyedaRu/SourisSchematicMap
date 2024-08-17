from svgpathtools import svg2paths
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import math,svgwrite
import pandas as pd
import xml.etree.ElementTree as ET
import os
from pdfdocument.document import PDFDocument
# import cairosvg

path_to_value_file = "C:/Users/syedaR/Desktop/Souris/2023 NaturalFlowSchematic.xlsx"
base_svg_path = "Asset12.svg"
scale_amount = 0.001

### Coordinates of each location within the specific base SVG
location_coordinates = {
    0: {
        "Below Rafferty": [(0, 21)],
        "Boundary Reservoir Diversion": [(2, 3)],
        "Short Creek near Roche Percee": [(5, 7)],
        "Natural Flow at Sherwood": [(10, 11)],
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
        "Unlabeled Numbers below Boundary Dam": [(2, 3)],
    }
}

##### Functions for SVG maniplation
# Function to calculate the Euclidean distance between two points
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to calculate new coordinates for a given ratio
def adjust_coordinates(x1, y1, x2, y2, ratio):
    x1_new = x1 + (x2 - x1) * (1 - ratio) / 2
    y1_new = y1 + (y2 - y1) * (1 - ratio) / 2
    x2_new = x2 - (x2 - x1) * (1 - ratio) / 2
    y2_new = y2 - (y2 - y1) * (1 - ratio) / 2
    return (x1_new, y1_new, x2_new, y2_new)


def get_xy(point):
    return point.real, point.imag

def path_to_points(path):
    points = []
    for segment in path:
        start_point = (segment.start.real, segment.start.imag)
           
        # Add the start point if it's not already in the list
        if not points or points[-1] != start_point:
            points.append(start_point)
   
    return points

# This function gets the decameter value given the dataframe and name of location
def get_value_by_name(df, name):
    # Using boolean indexing to filter the DataFrame
    value = df.loc[df["Name"] == name, "Cubic Decametres"]
    if not value.empty:
        return value.iloc[0]
    else:
        return 0

def change_svg_points(paths, coor,value_df, scale):
    """Updates the path variable with the new corrdinates of each location based on the scale amount
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    for object_idx, object in coor.items():
        for location, coords in object.items():
            for indices in coords:
                i = indices[0]
                j = indices[1]   
     
                # print("Before adjust => ", location, ": ",paths[object_idx][i].start, paths[object_idx][j].start)
                point1 = get_xy(paths[object_idx][i].start)
                point2 = get_xy(paths[object_idx][j].start)

                # Calculate current distance between the two points
                current_distance = calculate_distance(*point1, *point2)
                # Get the new distance to change to 
                desired_distance = int(get_value_by_name(value_df,location))* scale

                # Calculate the ratio
                ratio = desired_distance / current_distance
        

                # Adjust coordinates
                A1, A2 = adjust_coordinates(*point1, *point2, ratio)[:2], adjust_coordinates(*point1, *point2, ratio)[2:]

                paths[object_idx][i].start = complex(*A1)
                paths[object_idx][j].start = complex(*A2)
                

                if location == "Rafferty to Boundary Reservoir Pumpage":
                    if indices[0] == 0:
                        paths[object_idx][13].start = complex(*A1) 
                elif location == "Net Gain in North Dakota":
                    paths[object_idx][24].start = complex(*A1)

        
# def draw_svg(paths, svg_filename, location_coordinates):
#     dwg = svgwrite.Drawing(svg_filename + ".svg", profile='full')

#     # Define an arrow marker
#     arrow_marker = dwg.marker(insert=(2, 2), size=(4, 4), orient="auto")
#     arrow_marker.add(dwg.path(d="M0,0 L0,4 L4,2 Z", fill='black'))
#     dwg.defs.add(arrow_marker)

#     # Draw the paths (these are the main flow paths)
#     for i, path in enumerate(paths):
#         points = path_to_points(paths[i])
#         dwg.add(dwg.polygon(
#             points=points,
#             fill="#d3d3d3",
#             stroke='yellow',
#             stroke_miterlimit=10
#         ))

#     # Add labels with arrows
#     for object_idx, object in location_coordinates.items():
#         for location, coords in object.items():
#             for indices in coords[:1]:
#                 i = indices[0]
#                 j = indices[1]
#                 print(location, ": ",paths[object_idx][i].start, paths[object_idx][j].start)

#                 x1, y1 = get_xy(paths[object_idx][i].start)
#                 x2, y2 = get_xy(paths[object_idx][j].start)

#                 if object_idx == 1 and location == "Grant Devine Reservoir Diversion":
#                     y1 -= 5
#                     y2 -=5
#                 if location == "Moose Mountain Creek below Grant Devine (used to be 'near Oxbow')":
#                     y1 += 5
#                     y2 += 5

#                 if (x2-x1)<5:
#                     arrow_length = 2
#                 else:
#                     arrow_length = 0.2
#                 # Calculate an outward position for the arrows to start from
#                 arrow_start_x1 = x1 + (x1 - x2) * arrow_length  # Move slightly outward
#                 arrow_start_y1 = y1 + (y1 - y2) * arrow_length  # Move slightly outward

#                 arrow_start_x2 = x2 + (x2 - x1) * arrow_length  # Move slightly outward
#                 arrow_start_y2 = y2 + (y2 - y1) * arrow_length  # Move slightly outward

#                 # Position the label near one of the arrows
#                 label_offset_x = 5
#                 label_offset_y = -5
#                 # label_x = arrow_start_x1 + label_offset_x
#                 # label_y = arrow_start_y1 + label_offset_y
#                 line_height = 4  # Height between lines of text
#                 num_lines = len(location)

#                 for idx, char in enumerate(location.split()):
#                     label_x = arrow_start_x1 + label_offset_x
#                     label_y = arrow_start_y1 + label_offset_y + idx * line_height
#                     dwg.add(dwg.text(char, insert=(label_x, label_y), fill='black', font_size='4px'))

#                 # Draw the first arrow pointing to (x1, y1)
#                 dwg.add(dwg.line(start=(arrow_start_x1, arrow_start_y1), end=(x1, y1), stroke='black', stroke_width=0.5, marker_end=arrow_marker.get_funciri()))

#                 # Draw the second arrow pointing to (x2, y2)
#                 dwg.add(dwg.line(start=(arrow_start_x2, arrow_start_y2), end=(x2, y2), stroke='black', stroke_width=0.5, marker_end=arrow_marker.get_funciri()))

#     dwg.save()
# def draw_pie_chart(dwg, center, radius, data, colors, labels):
#     total = sum(data)
#     start_angle = 0

#     for i, value in enumerate(data):
#         slice_angle = 360 * (value / total)
#         end_angle = start_angle + slice_angle

#         # Convert angles to radians
#         start_rad = math.radians(start_angle)
#         end_rad = math.radians(end_angle)

#         # Convert angles to radians
#         mid_angle = start_angle + (slice_angle / 2)
#         mid_rad = math.radians(mid_angle)

#         # Calculate the coordinates for the arc
#         start_x = center[0] + radius * math.cos(start_rad)
#         start_y = center[1] + radius * math.sin(start_rad)
#         end_x = center[0] + radius * math.cos(end_rad)
#         end_y = center[1] + radius * math.sin(end_rad)

#         # Large arc flag
#         large_arc_flag = 1 if slice_angle > 180 else 0

#         # Path description
#         path_data = [
#             f"M{center[0]},{center[1]}",
#             f"L{start_x},{start_y}",
#             f"A{radius},{radius} 0 {large_arc_flag},1 {end_x},{end_y}",
#             "Z"
#         ]

#         # Add the pie slice
#         dwg.add(dwg.path(d=" ".join(path_data), fill=colors[i]))

#         # Calculate arrow and label positions
#         arrow_start_x = center[0] + radius * 0.8 * math.cos(mid_rad)
#         arrow_start_y = center[1] + radius * 0.8 * math.sin(mid_rad)
#         arrow_end_x = center[0] + radius * 1.2 * math.cos(mid_rad)
#         arrow_end_y = center[1] + radius * 1.2 * math.sin(mid_rad)

#         # Add arrow line
#         dwg.add(dwg.line(start=(arrow_start_x, arrow_start_y), end=(arrow_end_x, arrow_end_y), 
#                          stroke='black', stroke_width=0.5, marker_end='url(#arrow)'))

#         # Add label
#         label_x = arrow_end_x + (10 if math.cos(mid_rad) >= 0 else -50)
#         label_y = arrow_end_y + (15 if math.sin(mid_rad) >= 0 else -7)
#         dwg.add(dwg.text(labels[i], insert=(label_x, label_y), fill='black', font_size='8px'))

#         # Update start angle for the next slice
#         start_angle = end_angle

#     # Calculate the percentage of Canada's diversion
#     canada_net = data[1]  # Assuming data[0] is for Canada
#     canada_percentage = (canada_net / total) * 100

#     # Add side label
#     side_label_text = f"Canada diverted {canada_percentage:.1f}% of the natural flow"
#     side_label_x = center[0] + radius + 20  # Adjust X position as needed
#     side_label_y = center[1] - radius  # Adjust Y position as needed

#     # Determine the box size based on the text size
#     box_padding = 10
#     text_length = len(side_label_text) * 6  # Estimate text length (adjust factor as needed)
#     box_width = text_length + box_padding * 2
#     box_height = 20 + box_padding * 2
    
#     # Draw the box
#     dwg.add(dwg.rect(insert=(side_label_x - box_padding, side_label_y - 15), 
#                      size=(box_width, box_height), 
#                      fill='lightgray', stroke='black'))
#     dwg.add(dwg.text(side_label_text, insert=(side_label_x, side_label_y), fill='black', font_size='12px'))

def draw_pie_chart(dwg, center, radius, data, colors, labels):
    total = sum(data)
    start_angle = 0

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

        # Path description
        path_data = [
            f"M{center[0]},{center[1]}",
            f"L{start_x},{start_y}",
            f"A{radius},{radius} 0 {large_arc_flag},1 {end_x},{end_y}",
            "Z"
        ]

        # Add the pie slice
        dwg.add(dwg.path(d=" ".join(path_data), fill=colors[i]))

        # Calculate arrow and label positions
        arrow_start_x = center[0] + radius * 0.8 * math.cos(mid_rad)
        arrow_start_y = center[1] + radius * 0.8 * math.sin(mid_rad)
        arrow_end_x = center[0] + radius * 1.2 * math.cos(mid_rad)
        arrow_end_y = center[1] + radius * 1.2 * math.sin(mid_rad)

        # Add arrow line
        dwg.add(dwg.line(start=(arrow_start_x, arrow_start_y), end=(arrow_end_x, arrow_end_y), 
                         stroke='black', stroke_width=0.5, marker_end='url(#arrow)'))

        # Add label
        label_x = arrow_end_x + (8 if math.cos(mid_rad) >= 0 else -50)
        label_y = arrow_end_y + (15 if math.sin(mid_rad) >= 0 else -5)
        dwg.add(dwg.text(labels[i], insert=(label_x, label_y), fill='black', font_size='8px'))

        # Update start angle for the next slice
        start_angle = end_angle

    # Calculate the percentage of Canada's diversion
    canada_net = data[1]  # Assuming data[0] is for Canada
    canada_percentage = (canada_net / total) * 100

    # Add side label with a box split into two lines
    line1_text = f"Canada diverted"
    line2_text = f"{canada_percentage:.1f}% of the"
    line3_text = "Natural flow"
    
    side_label_x = center[0] + radius + 20  # Adjust X position as needed
    side_label_y = center[1]  # Adjust Y position as needed
    
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
    print(data)
    # Initialize drawing
    dwg = svgwrite.Drawing(svg_filename + ".svg", profile='full', size=(1000, 1000))  # Specify size if needed


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
        adjusted_points = [(x, y + y_shift) for x, y in points]
        polygon = dwg.polygon(
            points=points,
            fill="#d3d3d3",
            stroke='yellow',
            stroke_miterlimit=10
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

                if object_idx == 1 and location == "Grant Devine Reservoir Diversion":
                    y1 -= 5
                    y2 -= 5
               

                ## Arrows
                arrow_length = 8

                # Calculate the distance between the points
                distance = calculate_distance(x1, y1, x2, y2)
                
                if distance == 0:
                    # Handle zero distance case
                    distance = 1  # Skip this arrow or handle it differently

                # Calculate arrow start positions based on fixed arrow length
                arrow_start_x1 = x1 + (x1 - x2) * (arrow_length / distance)
                arrow_start_y1 = y1 + (y1 - y2) * (arrow_length / distance)

                arrow_start_x2 = x2 + (x2 - x1) * (arrow_length / distance)
                arrow_start_y2 = y2 + (y2 - y1) * (arrow_length / distance)

                label_offset_x = 5
                label_offset_y = -5
                line_height = 4
                
                label_to_display = location + " " + str(data.at[location, 'Cubic Decametres'])
                for idx, char in enumerate(label_to_display.split()):
                    label_x = arrow_start_x1 + label_offset_x
                    label_y = arrow_start_y1 + label_offset_y + idx * line_height
                    if object_idx == 0:
                        label_x = arrow_start_x1 + label_offset_x - 10
                        label_y = arrow_start_y1 + 10 + label_offset_y + idx * 4
                        if location == "Boundary Reservoir Diversion":
                            label_x += 25
                            label_y -= 5
                    if object_idx == 1:
                        label_x = arrow_start_x1 + label_offset_x - 5
                        label_y = arrow_start_y1 - 8 + label_offset_y + idx * 4
                    if location == "Moose Mountain Lake Diversion":
                        label_y = arrow_start_y1 - 7 + label_offset_y + idx * 4
                        label_x -= 10
                    if object_idx == 8:
                        ## for Unlabeled under Bourdary
                        label_x += 10
                        label_y += 17
                    if location == 'Souris River near Ralph (used to be "near Halbrite")':
                        label_x -= 15
                        label_y += 8
                    if object_idx == 2:
                        label_x -= 10
                        label_y += 10
                    if location == "Nickel Lake & Wayburn Diversion":
                        label_x -= 15
                        label_y -= 15
                    if location == "Rafferty Reservoir & Estevan Usage":
                        label_x = arrow_start_x2 + label_offset_x
                        label_y = arrow_start_y2 + label_offset_y + idx * line_height
                        

                    dwg.add(dwg.text(char, insert=(label_x, label_y), fill='black', font_size='4px'))

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
    dwg.add(dwg.text("CANADA", insert=(250, canada_usa_y - 5), fill='black', font_size='12px'))
    dwg.add(dwg.text("UNITED STATES", insert=(260, canada_usa_y+10), fill='black', font_size='12px'))

    # Add the pie chart
    pie_center = (430, 300)  # Adjust this position to place the pie chart correctly
    pie_radius = 30000 * scale_amount

    
    canada_net = data.at["Canada net Depletions", 'Cubic Decametres']
    us_net = data.at["Flow received by the US",'Cubic Decametres']
    pie_data = [us_net,canada_net]  # Example data: Adjust these values
    pie_colors = ["blue", "red"]  # Example colors: Adjust these as needed
    pie_labels = [ "Flow received by the USA","Canada net Depletions"]

    # Define arrow marker
    arrow_marker = dwg.marker(insert=(2, 2), size=(4, 4), orient="auto")
    arrow_marker.add(dwg.path(d="M0,0 L0,4 L4,2 Z", fill='black'))
    dwg.defs.add(arrow_marker)
    draw_pie_chart(dwg, pie_center, pie_radius, pie_data, pie_colors,pie_labels)

    
    # Add Title
    dwg.add(dwg.text("SCHEMATIC REPRESENTATION OF 2023 FLOWS IN THE SOURIS RIVER BASIN",
                     insert=(center_x - 120, 0), fill='black', font_size='7px', font_weight="bold"))
    dwg.add(dwg.text("ABOVE SHERWOOD, NORTH DAKOTA, U.S.A.",
                     insert=(center_x - 80, 5), fill='black', font_size='7px', font_weight="bold"))

    # Add Scale Ruler
    scale_x = 480
    scale_y = 30
    scale_length = 50
    dwg.add(dwg.line(start=(scale_x, scale_y), end=(scale_x + scale_length, scale_y), stroke='black', stroke_width=2))
    for i in range(0, 51, 10):
        tick_x = scale_x + i * (scale_length / 50)
        tick_y = scale_y + 10
        dwg.add(dwg.line(start=(tick_x, scale_y), end=(tick_x, tick_y), stroke='black', stroke_width=1))
        dwg.add(dwg.text(str(i), insert=(tick_x - 5, tick_y + 15), fill='black', font_size='5px'))
    dwg.add(dwg.text("VALUES SHOWN ARE IN CUBIC",
                     insert=(scale_x , scale_y - 10), fill='black', font_size='5px'))
    dwg.add(dwg.text("DECAMETRES (ACRE-FEET)",
                     insert=(scale_x , scale_y - 5), fill='black', font_size='5px'))
    dwg.add(dwg.text("Dam³ x 1000", insert=(scale_x + scale_length + 10, scale_y + 5), fill='black', font_size='5px'))

    # Save the SVG file
    dwg.save()

def get_svg_dimensions(filename):
    # Parse the SVG file
    tree = ET.parse(filename)
    root = tree.getroot()

    # SVG namespace
    svg_namespace = {'svg': 'http://www.w3.org/2000/svg'}

    # Get width and height attributes from the SVG element
    width = root.get('width')
    height = root.get('height')

    # If dimensions are percentages or other units, you might need to handle conversion here
    # For simplicity, assuming dimensions are in pixels
    return float(width.replace('px', '').strip()), float(height.replace('px', '').strip())

def convert_svg_to_pdf(filename):
    doc = PDFDocument()
    # Load an SVG file
    doc.LoadFromSvg(filename)
    # Get the size of the SVG content (assuming you have these methods available)
    svg_width = doc.GetSvgWidth()  # Method to get the SVG width
    svg_height = doc.GetSvgHeight()  # Method to get the SVG height
    
    # Set the page size of the PDF (optional, adjust if needed)
    doc.SetPageSize(svg_width, svg_height)
    
    # Center the SVG content horizontally
    # Calculate the x-position to center the SVG horizontally on the page
    page_width = doc.GetPageWidth()
    x_position = (page_width - svg_width) / 2
    
    # Translate and draw the SVG content
    doc.Translate(x_position, 0)  # Move the content horizontally

    # Save the SVG file to PDF format
    doc.SaveToFile(filename+".pdf", FileFormat.PDF)
    # Close the PdfDocument object
    doc.Close()

    # Function to convert SVG to PNG or PDF
def convert_svg(filename, output_format='pdf'):
    try:
        if output_format.lower() == 'png':
            # Convert SVG to PNG
            cairosvg.svg2png(url=f"{filename}.svg", write_to=f"{filename}.png")
            print(f"SVG has been successfully converted to {filename}.png")
        elif output_format.lower() == 'pdf':
            # Convert SVG to PDF
            cairosvg.svg2pdf(url=f"{filename}.svg", write_to=f"{filename}.pdf")
            print(f"SVG has been successfully converted to {filename}.pdf")
        else:
            print("Unsupported format. Please choose either 'png' or 'pdf'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def convert_svg_to_png(svg_filename, png_filename):
    image = pyvips.Image.thumbnail(svg_filename, 300)
    image.write_to_file(png_filename)


if __name__ == "__main__":
    filename = "SchematicMap"
    
    # The bin folder has the DLLs
    current_dir = os.getcwd()
    libvips = os.path.join(current_dir, "libvips-8.15.2")
    # Construct the path to the bin folder within the libvips directory
    libvips_bin = os.path.join(libvips, "libvips")
    # print(libvips_bin)
    # Add the bin folder to the PATH environment variable
    os.environ['PATH'] += os.pathsep + libvips
    # print(os.environ['PATH'])
    
    paths, attribtue = svg2paths('Asset12.svg')
    value_datatframe = pd.read_excel(path_to_value_file, "Natural Flow Schematic",usecols=["Name","Cubic Decametres"],header=1,nrows=25)
    change_svg_points(paths,location_coordinates,value_datatframe,scale_amount)
    draw_svg(paths,filename, location_coordinates, value_datatframe)

    # import pyvips
    # # convert_svg_to_png("SchematicMap.svg", "SchematicMap.png")
    # image = pyvips.Image.thumbnail("SchematicMap.svg", 300)
    # image.write_to_file("SchematicMap.png")
    input_file = "SchematicMap"
    output_file = "SchematicMap.png"

    # convert_svg(input_file)

    # with wand.image.Image() as image:
    #     with wand.color.Color('transparent') as background_color:
    #         library.MagickSetBackgroundColor(image.wand, 
    #                                         background_color.resource) 
    #         image.read(blob=svg_file.read(), format="svg")
    #         png_image = image.make_blob("png32")

    # with open(output_file, "wb") as out:
    #     out.write(png_image)

    # drawing = svg2rlg(input_file)
    # renderPM.drawToFile(drawing, output_file, fmt="PNG")


