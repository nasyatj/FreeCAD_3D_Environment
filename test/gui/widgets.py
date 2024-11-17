# gui/widgets.py
from PySide2 import QtCore, QtWidgets

def create_command_area(submit_callback):
    """Create the command input and history area."""
    command_group = QtWidgets.QGroupBox("Command Input")
    layout = QtWidgets.QVBoxLayout()
    
    # Command history display
    history_display = QtWidgets.QTextEdit()
    history_display.setReadOnly(True)
    history_display.setMinimumHeight(200)
    layout.addWidget(history_display)
    
    # Command input
    input_layout = QtWidgets.QHBoxLayout()
    command_input = QtWidgets.QLineEdit()
    command_input.setPlaceholderText("Enter command...")
    submit_button = QtWidgets.QPushButton("Submit")
    
    input_layout.addWidget(command_input)
    input_layout.addWidget(submit_button)
    layout.addLayout(input_layout)
    
    # Connect signals
    def submit_command():
        command = command_input.text()
        if command.strip():
            submit_callback(command)
            history_display.append(f"> {command}")
            command_input.clear()
    
    submit_button.clicked.connect(submit_command)
    command_input.returnPressed.connect(submit_command)
    
    command_group.setLayout(layout)
    return command_group, history_display, command_input

def create_quality_group():
    """Create the export quality control group."""
    quality_group = QtWidgets.QGroupBox("Export Settings")
    quality_layout = QtWidgets.QVBoxLayout()
    
    quality_label = QtWidgets.QLabel("Mesh Quality:")
    quality_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    quality_slider.setRange(1, 50)
    quality_slider.setValue(10)
    quality_layout.addWidget(quality_label)
    quality_layout.addWidget(quality_slider)
    
    quality_group.setLayout(quality_layout)
    return quality_group, quality_slider