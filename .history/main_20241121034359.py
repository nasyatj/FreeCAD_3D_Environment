#!C:\Users\kendr\AppData\Local\Programs\FreeCAD 0.21\bin\python.exe

import os
import sys

"""Set up the FreeCAD environment and Python path."""
FREECAD_ROOT = 'C:\Users\kendr\AppData\Local\Programs\FreeCAD 0.21\bin\python.exe'
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

print("Current sys.path:", sys.path)  # Debug print to verify paths

# Set required environment variables
os.environ['PYTHONHOME'] = FREECAD_ROOT
os.environ['DYLD_LIBRARY_PATH'] = FREECAD_LIB
os.environ['PYTHONPATH'] = os.path.join(FREECAD_ROOT, 'lib/python3.10/site-packages')

from PySide2 import QtCore, QtWidgets

# Create Qt Application first
app = QtWidgets.QApplication(sys.argv)

# Then import FreeCAD modules
import FreeCAD
import Mesh
import FreeCADGui

class BoxGeneratorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize FreeCAD document
        self.doc = FreeCAD.newDocument("BoxExample")
        
        # Set up the main window
        self.setWindowTitle("Box Generator")
        self.setGeometry(100, 100, 1000, 600)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Create controls panel
        controls_panel = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(controls_panel)
        controls_panel.setMaximumWidth(250)
        
        # Add dimension inputs
        dimension_group = QtWidgets.QGroupBox("Dimensions")
        dimension_layout = QtWidgets.QFormLayout()
        
        self.length_input = QtWidgets.QDoubleSpinBox()
        self.length_input.setRange(0.1, 1000)
        self.length_input.setValue(10)
        self.length_input.valueChanged.connect(self.update_box)
        dimension_layout.addRow("Length:", self.length_input)
        
        self.width_input = QtWidgets.QDoubleSpinBox()
        self.width_input.setRange(0.1, 1000)
        self.width_input.setValue(10)
        self.width_input.valueChanged.connect(self.update_box)
        dimension_layout.addRow("Width:", self.width_input)
        
        self.height_input = QtWidgets.QDoubleSpinBox()
        self.height_input.setRange(0.1, 1000)
        self.height_input.setValue(10)
        self.height_input.valueChanged.connect(self.update_box)
        dimension_layout.addRow("Height:", self.height_input)
        
        dimension_group.setLayout(dimension_layout)
        controls_layout.addWidget(dimension_group)
        
        # Add mesh quality control
        quality_group = QtWidgets.QGroupBox("Export Settings")
        quality_layout = QtWidgets.QVBoxLayout()
        
        quality_label = QtWidgets.QLabel("Mesh Quality:")
        self.quality_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.quality_slider.setRange(1, 50)
        self.quality_slider.setValue(10)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_slider)
        
        quality_group.setLayout(quality_layout)
        controls_layout.addWidget(quality_group)
        
        # Add export button
        export_button = QtWidgets.QPushButton("Export STL")
        export_button.clicked.connect(self.export_stl)
        controls_layout.addWidget(export_button)
        
        # Add status label
        self.status_label = QtWidgets.QLabel("Ready")
        controls_layout.addWidget(self.status_label)
        
        controls_layout.addStretch()
        
        # Add controls to main layout
        layout.addWidget(controls_panel)
        
        # Create box
        self.box = None
        self.update_box()
        
        # Show the window
        self.show()

    def update_box(self):
        length = self.length_input.value()
        width = self.width_input.value()
        height = self.height_input.value()
        
        # Remove existing box if it exists
        if self.box:
            self.doc.removeObject(self.box.Name)
        
        # Create new box
        self.box = self.doc.addObject("Part::Box", "Box")
        self.box.Length = length
        self.box.Width = width
        self.box.Height = height
        
        # Recompute
        self.doc.recompute()

    def export_stl(self):
        try:
            length = self.length_input.value()
            width = self.width_input.value()
            height = self.height_input.value()
            mesh_deviation = self.quality_slider.value() / 100.0
            
            self.status_label.setText("Exporting...")
            QtWidgets.QApplication.processEvents()
            
            # Create mesh and export
            shape = self.box.Shape
            mesh = Mesh.Mesh()
            mesh.addFacets(shape.tessellate(mesh_deviation))
            stl_name = f"box_{length}x{width}x{height}.stl"
            mesh.write(stl_name)
            
            self.status_label.setText(f"Exported: {stl_name}")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

if __name__ == "__main__":
    try:
        # Initialize GUI system
        FreeCADGui.showMainWindow()
        
        # Create and show the box generator
        box_generator = BoxGeneratorApp()
        
        # Start the application
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)