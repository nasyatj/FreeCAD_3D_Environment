# entry point that sets up the environment and launches the application
import os
import sys

#unneeded?
# # Add the project directory to Python path
# project_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, project_dir)

# Set up FreeCAD environment BEFORE any FreeCAD imports
from setup import setup_freecad_env
setup_freecad_env()

# Now we can import FreeCAD-related modules
from PySide2 import QtWidgets
import FreeCADGui
from gui.main_window import BoxGeneratorApp

if __name__ == "__main__":
    try:
        # Create Qt Application
        app = QtWidgets.QApplication(sys.argv)
        
        # Initialize GUI system
        FreeCADGui.showMainWindow()
        
        # Create and show the box generator
        box_generator = BoxGeneratorApp()
        
        # Start the application
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
