# Souris Schematic Map Generator

This project generates a schematic SVG map of the Souris River Basin, visualizing water flows and diversions between Canada and the United States. The map uses labeled polygons, arrows, and a pie chart to represent flow data, and can be exported as SVG.

---

## Features

- **SVG Map Generation:** Draws polygons for river segments and reservoirs, with arrows and labels for each location.
- **Pie Chart Visualization:** Shows the proportion of flow received by the US and net depletion by Canada.
- **Custom Labeling:** Automatically positions and formats labels with flow values (in cubic decametres and acre-feet).
- **Scale Rulers:** Includes visual scales for both cubic decametres and acre-feet.
- **Export to PDF:** Optionally opens the SVG in a browser for printing or PDF export.

---

## Requirements

- Python 3.7+
- [svgwrite](https://pypi.org/project/svgwrite/)
- [svgpathtools](https://pypi.org/project/svgpathtools/)
- [pandas](https://pypi.org/project/pandas/)
- [selenium](https://pypi.org/project/selenium/) (for PDF export)
- [pyautogui](https://pypi.org/project/PyAutoGUI/) (for PDF export)
- [Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) (for PDF export)
- [reportlab](https://pypi.org/project/reportlab/) (optional, for advanced PDF features)

Install dependencies with:
```sh
pip install svgwrite svgpathtools pandas selenium pyautogui reportlab
```

---

## Usage

1. **Prepare Data:**
   - Place your flow data in an Excel file (default: `2023 NaturalFlowSchematic.xlsx`, change as needed) with columns: `Name`, `Name to show`, `Cubic Decametres`, `Acre-feet`.
   - Ensure the SVG base map file (default: Asset12.svg) is present. Change path as needed

2. **Run the Script:**
   ```sh
   python svg_py.py
   ```
   This will:
   - Read the Excel data.
   - Adjust the SVG paths based on flow values.
   - Draw the schematic map and pie chart.
   - Save the output as SchematicMap.svg.

3. **Export to PDF (Optional):**
   - This code creates a SoruisSchematic.scg file which can be opened and viewed on a browser. To save it as a sharable picture format, screenshot the interested region from the browser and save it as PNG or Jpeg.

---

## File Structure

- svg_py.py — Main script for SVG generation and export.
- Asset12.svg — Base SVG map file.
- `2023 NaturalFlowSchematic.xlsx` — Excel file with flow data.

---

## Customization
- **Path to Data File:**  
  `path_to_value_file` replace this variable at the top of the script with updated data file. It must have the columns: "Name","Name to show", "Cubic Decametres","Acre-feet".
- **Path to base SVG file:**  
  `base_svg_path` replace this variable at the top of the script as needed.
- **Scaling:**  
  Adjust the `scale_amount` variable to change the scaling of flow distances.
- **Pie Chart:**  
  The pie chart is generated from "Canada net Depletions" and "Flow received by the US" rows in your data.

---

## Example Output

![Example SVG Output](SchematicMap.svg)  
*Sample schematic map with labeled flows and pie chart.*

---

## Contact

For questions or contributions, please open an issue or contact the brianna.vaagen@ec.gc.ca.

---

**Note:**  
This script is designed for a specific SVG and data format. You may need to adjust coordinates or data columns for your own use case.