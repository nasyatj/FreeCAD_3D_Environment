import os
import sys

# Add FreeCAD libraries to Python's sys.path
FREECAD_ROOT = r'C:\Users\kendr\AppData\Local\Programs\FreeCAD 0.21'
FREECAD_LIB = os.path.join(FREECAD_ROOT, 'bin')

if not os.path.exists(FREECAD_ROOT):
    raise EnvironmentError(f"FreeCAD root directory not found: {FREECAD_ROOT}")

sys.path.append(os.path.join(FREECAD_LIB, 'Lib'))
sys.path.append(os.path.join(FREECAD_LIB, 'site-packages'))

# Set required environment variables
os.environ['PYTHONHOME'] = FREECAD_ROOT
os.environ['PYTHONPATH'] = os.path.join(FREECAD_LIB, 'site-packages')

# Import necessary modules
from PySide2 import QtCore, QtWidgets
import FreeCAD
import Mesh
import FreeCADGui
# Set the required Qt attribute before creating the QApplication
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)

# Create Qt Application first
app = QtWidgets.QApplication(sys.argv)

# Main application class
class BoxGeneratorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.doc = FreeCAD.newDocument("BoxExample")
        self.setWindowTitle("Box Generator")
        self.setGeometry(100, 100, 1000, 600)
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QHBoxLayout(central_widget)

        controls_panel = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(controls_panel)
        controls_panel.setMaximumWidth(250)

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

        export_button = QtWidgets.QPushButton("Export STL")
        export_button.clicked.connect(self.export_stl)
        controls_layout.addWidget(export_button)

        self.status_label = QtWidgets.QLabel("Ready")
        controls_layout.addWidget(self.status_label)

        controls_layout.addStretch()
        layout.addWidget(controls_panel)
        self.box = None
        self.update_box()
        self.show()

    def update_box(self):
        length = self.length_input.value()
        width = self.width_input.value()
        height = self.height_input.value()

        if self.box:
            self.doc.removeObject(self.box.Name)

        self.box = self.doc.addObject("Part::Box", "Box")
        self.box.Length = length
        self.box.Width = width
        self.box.Height = height
        self.doc.recompute()

    def export_stl(self):
        try:
            length = self.length_input.value()
            width = self.width_input.value()
            height = self.height_input.value()
            mesh_deviation = self.quality_slider.value() / 100.0

            self.status_label.setText("Exporting...")
            QtWidgets.QApplication.processEvents()

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
        FreeCADGui.showMainWindow()
        box_generator = BoxGeneratorApp()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
