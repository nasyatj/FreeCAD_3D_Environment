#  Contains FreeCAD environment setup code
import os
import sys

#SAVED

def setup_freecad_env():
    """Set up the FreeCAD environment and Python path."""
    FREECAD_ROOT = '/Applications/FreeCAD.app/Contents/Resources'
    FREECAD_LIB = os.path.join(FREECAD_ROOT, 'lib')

    if not os.path.exists(FREECAD_ROOT):
        raise EnvironmentError(f"FreeCAD root directory not found: {FREECAD_ROOT}")
    
    # Clear existing sys.path to avoid conflicts
    sys.path.clear()
    sys.path.extend([
        '',
        os.path.join(FREECAD_ROOT, 'lib/python310.zip'),
        os.path.join(FREECAD_ROOT, 'lib/python3.10'),
        os.path.join(FREECAD_ROOT, 'lib/python3.10/lib-dynload'),
        os.path.join(FREECAD_ROOT, 'lib/python3.10/site-packages'),
        FREECAD_LIB
    ])

    #print("Current sys.path:", sys.path)  # Debug print to verify paths

    # Set required environment variables
    os.environ['PYTHONHOME'] = FREECAD_ROOT
    os.environ['DYLD_LIBRARY_PATH'] = FREECAD_LIB
    os.environ['PYTHONPATH'] = os.path.join(FREECAD_ROOT, 'lib/python3.10/site-packages')