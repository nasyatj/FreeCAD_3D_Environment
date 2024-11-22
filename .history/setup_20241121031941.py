import os
import sys

def setup_freecad_env():
    # Path to FreeCAD libraries
    freecad_path = r"C:\Users\kendr\AppData\Local\Programs\FreeCAD 0.21\bin"  # Update this path
    if freecad_path not in sys.path:
        sys.path.append(freecad_path)

    # Optional: Set other environment variables if needed
    # os.environ['FREECAD_LIB_PATH'] = freecad_path
