from PySide2 import QtCore, QtGui, QtWidgets
import FreeCAD
import FreeCADGui
import Part
import Mesh
from PySide2.QtCore import Signal
from commands import CommandProcessor
import threading

from test_commands import ServerConnect


class CommandWindow(QtWidgets.QWidget):
    def __init__(self, submit_callback, export_callback, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setWindowTitle("Command Input")
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Command history
        self.history_display = QtWidgets.QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setMinimumHeight(100)
        self.history_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(40, 40, 40, 255);
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.history_display)
        
        # Command input area
        input_layout = QtWidgets.QHBoxLayout()
        self.command_input = QtWidgets.QLineEdit()
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 40, 40, 255);
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                font-family: monospace;
            }
        """)
        
        submit_button = QtWidgets.QPushButton("Submit")
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(submit_button)
        layout.addLayout(input_layout)

        # Add export controls
        export_layout = QtWidgets.QHBoxLayout()
        
        # Quality slider
        quality_label = QtWidgets.QLabel("Quality:")
        quality_label.setStyleSheet("color: white;")
        self.quality_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.quality_slider.setRange(1, 1000)
        self.quality_slider.setValue(300)
        self.quality_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #555;
                height: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        
        # Export button
        export_button = QtWidgets.QPushButton("Export STL")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        export_button.clicked.connect(export_callback)
        
        export_layout.addWidget(quality_label)
        export_layout.addWidget(self.quality_slider)
        export_layout.addWidget(export_button)
        layout.addLayout(export_layout)
        
        # Connect signals
        def submit_command():
            command = self.command_input.text()
            if command.strip():
                submit_callback(command)
                self.command_input.clear()
                
        submit_button.clicked.connect(submit_command)
        self.command_input.returnPressed.connect(submit_command)
        
        # Set initial size and position
        self.resize(400, 300)
        self.position_window()
    
    def position_window(self):
        """Position the window in the center of the FreeCAD window"""
        main_window = FreeCADGui.getMainWindow()
        if main_window:
            geometry = main_window.geometry()
            center = geometry.center()
            frame_geometry = self.frameGeometry()
            frame_geometry.moveCenter(center)
            self.move(frame_geometry.topLeft())

class BoxGeneratorApp(QtWidgets.QMainWindow):
    data_received = Signal(str)  # Signal for server data

    def __init__(self):
        super().__init__()
        
        # Initialize FreeCAD document
        self.doc = FreeCAD.newDocument("HandTracking")
        FreeCAD.setActiveDocument("HandTracking")
        FreeCADGui.setActiveDocument("HandTracking")

        # White bg for handtracking window
        self.setup_viewer()

        # Initialize command processor
        self.command_processor = CommandProcessor(self.doc)
        
        # Set up the main window
        self.setWindowTitle("FreeCAD Hand Tracking Interface")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create status bar for basic status messages
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Create command window with export functionality
        self.command_window = CommandWindow(
            self.process_command,
            self.export_stl
        )

        # Initialize ServerConnect and pass the signal's emit method as a callback
        self.server_connect = ServerConnect(self.data_received.emit, self.doc)

        FreeCADGui.ActiveDocument.ActiveView.viewAxonometric()
        FreeCADGui.ActiveDocument.ActiveView.fitAll()

        # Start the server in a separate thread
        self.server_connect.run_server_in_thread()

        # Connect the signal to the process_server_data method
        self.data_received.connect(self.server_connect.process_server_data)

        self.command_window.show()

    def export_stl(self):
        """Export all objects in the model to STL."""
        try:
            if not self.command_processor.objects:
                raise Exception("No objects to export")
                
            self.status_label.setText("Exporting...")
            QtWidgets.QApplication.processEvents()
            
            # Create a compound shape from all visible objects
            shapes = []
            for obj in self.command_processor.objects.values():
                if hasattr(obj, 'Shape') and obj.Visibility:
                    shapes.append(obj.Shape)
                    
            if not shapes:
                raise Exception("No visible objects to export")
                
            # Create compound if multiple shapes, otherwise use single shape
            if len(shapes) > 1:
                shape = Part.Compound(shapes)
            else:
                shape = shapes[0]
                
            # Create mesh with simple linear scale
            mesh = Mesh.Mesh()
            mesh_deviation = 0.05  # Fixed small value for high resolution
            
            mesh.addFacets(shape.tessellate(mesh_deviation))
            
            stl_name = "exported_model.stl"
            mesh.write(stl_name)
            
            self.status_label.setText(f"Exported: {stl_name} (deviation: {mesh_deviation})")
            self.command_window.history_display.append(
                f"Exported {len(shapes)} object(s) to {stl_name}"
            )
                
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.command_window.history_display.append(f"Error: {str(e)}")

    def setup_viewer(self):
        """Set up the viewer with white background"""
        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
        param.SetUnsigned("BackgroundColor", 4294967295)
        param.SetBool("Simple", True)
        param.SetBool("Gradient", False)

    
    def toggle_command_window(self):
        """Toggle the command window visibility"""
        if self.command_window.isVisible():
            self.command_window.hide()
        else:
            self.command_window.show()
            self.command_window.raise_()
            self.command_window.activateWindow()
    
    def process_command(self, command):
        """Process the command from the input area."""
        try:
            self.status_label.setText(f"Processing: {command}")
            result = self.command_processor.process(command)
            self.command_window.history_display.append(f"\n> {command}")
            self.command_window.history_display.append(result)
            self.status_label.setText("Ready")
            
            if result.startswith("Created box"):
                box_name = result.split()[2]
                self.box = self.command_processor.objects.get(box_name)
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.command_window.history_display.append(f"Error: {str(e)}")
    
    def _show_help(self):
        """Show available commands in the history display."""
        help_text = """Available commands:
- box length width height
- sphere radius
- cylinder radius height
- list
- clear

Examples:
> box 10 20 30
> sphere 15
> cylinder 10 40
"""
        self.command_window.history_display.append(help_text)
    
    
    def closeEvent(self, event):
        """Handle application closing."""
        self.command_window.close()
        super().closeEvent(event)

