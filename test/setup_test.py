# After
import sys
import os

from setup import setup_freecad_env
setup_freecad_env()

import FreeCAD
import FreeCADGui
import Part

# Test FreeCAD functionality by creating a simple Part object
doc = FreeCAD.newDocument("TestDocument")  # Create a new FreeCAD document
box = Part.makeBox(10, 10, 10)  # Create a simple box shape
doc.addObject("Part::Feature", "Box").Shape = box  # Add the box to the document

# Check if the shape was successfully created
print("Created a Part object: Box")

# Save the document in the current project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(project_dir, "test_box.fcstd")
doc.saveAs(file_path)
print(f"Document saved as '{file_path}'")

