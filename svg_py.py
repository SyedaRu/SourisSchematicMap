from svgpathtools import svg2paths
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import math,svgwrite
import pandas as pd
from spire.pdf.common import *
from spire.pdf import *
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xml.etree.ElementTree as ET
# import pyvips
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

path_to_value_file = "C:/Users/ruban/Desktop/waterResources/Souris/2022 NaturalFlowSchematic_Updated.xlsx"
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
    2: {
        "Boundary Reservoir Diversion Canal": [(9, 20), (10, 19), (11, 18), (12, 17), (13, 16), (14, 15)],
        "Long Creek near Maxim": [(4, 6)],
        "Long Creek at Western Crossing": [(3, 7)],
        "Net Gain in North Dakota": [(0, 2)],
        "Long Creek near Noonan": [(9, 23)],
    },
    3: {
        "Rafferty to Boundary Reservoir Pumpage": [(0, 4), (2, 3), (8, 9), (7, 10), (6, 11), (5, 12)],
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
        return None

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

# def draw_svg(paths, svg_filename):
#     ##### Drawing the shape out
#     dwg = svgwrite.Drawing(svg_filename+".svg", profile='tiny')

#     for i, path in enumerate(paths):
#         dwg.add(dwg.polygon(
#             # Adjusted points to reduce the distance between the top-left and bottom-right points
#             points=path_to_points(paths[i]),
#             fill="#d3d3d3",
#             stroke='#ff0000',  # New stroke color
#             stroke_miterlimit=10
#         ))
        

#     dwg.save()

# Function to draw SVG and add labels
def draw_svg(paths, svg_filename, location_coordinates):
    dwg = svgwrite.Drawing(svg_filename+".svg", profile='tiny')

    for i, path in enumerate(paths):
        points = path_to_points(paths[i])
        dwg.add(dwg.polygon(
            points=points,
            fill="#d3d3d3",
            stroke='#ff0000',
            stroke_miterlimit=10
        ))

    # Adding labels for each location
    for location, coords in location_coordinates.get(i, {}).items():
        for indices in coords:
            x, y = points[indices[0]]
            dwg.add(dwg.text(location, insert=(x + 5, y + 5), fill='blue', font_size='3px'))

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

# def convert_svg_to_pdf(filename):
#     doc = PdfDocument()
#     # Load an SVG file
#     doc.LoadFromSvg(filename +".svg")
#     # Get the size of the SVG content (assuming you have these methods available)
#     svg_width = doc.GetSvgWidth()  # Method to get the SVG width
#     svg_height = doc.GetSvgHeight()  # Method to get the SVG height
    
#     # Set the page size of the PDF (optional, adjust if needed)
#     doc.SetPageSize(svg_width, svg_height)
    
#     # Center the SVG content horizontally
#     # Calculate the x-position to center the SVG horizontally on the page
#     page_width = doc.GetPageWidth()
#     x_position = (page_width - svg_width) / 2
    
#     # Translate and draw the SVG content
#     doc.Translate(x_position, 0)  # Move the content horizontally

#     # Save the SVG file to PDF format
#     doc.SaveToFile(filename+".pdf", FileFormat.PDF)
#     # Close the PdfDocument object
#     doc.Close()

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
    print(libvips_bin)
    # Add the bin folder to the PATH environment variable
    os.environ['PATH'] += os.pathsep + libvips
    # print(os.environ['PATH'])
    
    paths, attribtue = svg2paths('Asset12.svg')
    value_datatframe = pd.read_excel(path_to_value_file, "Natural Flow Schematic",usecols=["Name","Cubic Decametres"],header=1,nrows=25)
    change_svg_points(paths,location_coordinates,value_datatframe,scale_amount)
    draw_svg(paths,filename, location_coordinates)

    # import pyvips
    # # convert_svg_to_png("SchematicMap.svg", "SchematicMap.png")
    # image = pyvips.Image.thumbnail("SchematicMap.svg", 300)
    # image.write_to_file("SchematicMap.png")
    input_file = "SchematicMap.svg"
    output_file = "SchematicMap.png"

    svg_file = open(input_file, "r")

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


