import time
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QLabel
from PySide2 import QtCore
import math
from setup import setup_freecad_env
setup_freecad_env()

from commands import CommandProcessor

import socket
import threading
import FreeCAD
import FreeCADGui
import Part


class ServerConnect(QtCore.QObject):
    update_signal = QtCore.Signal(int, float, float)
    snap_signal = QtCore.Signal()

    def __init__(self, process_data_callback, doc):
        super().__init__()

        self.process_data_callback = process_data_callback
        self.doc = FreeCAD.ActiveDocument
        self.CommandProcessor = CommandProcessor(doc)


        self.finger_lines = {}
        self.finger_spheres = {}  # Dictionary to store sphere objects
        self.main_window = FreeCADGui.getMainWindow()

        # Camera resolution
        self.cam_width = 1280
        self.cam_height = 720

        # Define the desired working area in FreeCAD units
        self.freecad_width = 200
        self.freecad_height = 150

        # Sphere radius
        self.sphere_radius = 3.0  # Adjust this value to change sphere size

        self.finger_colors = {
            0: (1.0, 0.0, 0.0),  # Red
            1: (0.0, 1.0, 0.0),  # Green
            2: (0.0, 0.0, 1.0),  # Blue
            3: (1.0, 1.0, 0.0),  # Yellow
            4: (1.0, 0.0, 1.0)  # Magenta
        }

        # Rate limiting parameters
        self.last_update_time = time.time()
        self.update_interval = 0.05  # 50ms between updates (20 fps)
        self.pending_updates = {}  # Store the most recent updates

        if not self.main_window:
            print("Error: Could not get FreeCAD main window.")
            return

        self._initialize_labels()

        # Connect signals
        self.update_signal.connect(self._create_line)
        self.snap_signal.connect(self._snap_lines_to_origin)

        # Create initial objects
        self._create_initial_objects()
        self._create_working_area()

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self._process_pending_updates)
        self.update_timer.start(int(self.update_interval * 1000))  # Convert to milliseconds

    def _process_pending_updates(self):
        """Process any pending updates at the specified interval."""
        try:
            if not self.pending_updates:
                return

            # Process all pending updates
            for finger_id, (x, y) in self.pending_updates.items():
                self._update_objects(finger_id, x, y)

            # Clear pending updates
            self.pending_updates.clear()

            # Update the view
            FreeCAD.ActiveDocument.recompute()

        except Exception as e:
            print(f"Error processing pending updates: {e}")
            import traceback
            traceback.print_exc()

    def _update_objects(self, finger_id, x, y):
        """Update line and sphere positions."""
        try:
            # Transform coordinates
            x_freecad, y_freecad = self._transform_coordinates(x, y)
            endpoint = FreeCAD.Vector(x_freecad, y_freecad, 0)

            line_name = f"FingerLine_{finger_id}"
            sphere_name = f"FingerSphere_{finger_id}"

            # Update line
            if line_name in self.finger_lines:
                line = Part.makeLine(FreeCAD.Vector(0, 0, 0), endpoint)
                self.finger_lines[line_name].Shape = line

            # Update sphere
            if sphere_name in self.finger_spheres:
                sphere = Part.makeSphere(self.sphere_radius, endpoint)
                self.finger_spheres[sphere_name].Shape = sphere

        except Exception as e:
            print(f"Error updating objects: {e}")
            import traceback
            traceback.print_exc()

    def _create_working_area(self):
        """Create a rectangle to show the working area."""
        try:
            # Create corners of working area
            x_offset = -self.freecad_width / 2
            y_offset = -self.freecad_height / 2

            p1 = FreeCAD.Vector(x_offset, y_offset, 0)
            p2 = FreeCAD.Vector(x_offset + self.freecad_width, y_offset, 0)
            p3 = FreeCAD.Vector(x_offset + self.freecad_width, y_offset + self.freecad_height, 0)
            p4 = FreeCAD.Vector(x_offset, y_offset + self.freecad_height, 0)

            # Create edges
            edge1 = Part.makeLine(p1, p2)
            edge2 = Part.makeLine(p2, p3)
            edge3 = Part.makeLine(p3, p4)
            edge4 = Part.makeLine(p4, p1)

            # Create wire
            wire = Part.Wire([edge1, edge2, edge3, edge4])

            # Create shape
            area_obj = FreeCAD.ActiveDocument.addObject("Part::Feature", "WorkingArea")
            area_obj.Shape = wire
            area_obj.ViewObject.LineColor = (0.5, 0.5, 0.5)  # Gray
            area_obj.ViewObject.LineWidth = 1.0

            FreeCAD.ActiveDocument.recompute()
        except Exception as e:
            print(f"Error creating working area: {e}")

    def _create_initial_objects(self):
        """Create initial lines and spheres at origin."""
        try:
            # Create a tiny line at origin
            origin_line = Part.makeLine(
                FreeCAD.Vector(0, 0, 0),
                FreeCAD.Vector(0.1, 0.1, 0)
            )

            # Create a normal-sized sphere at origin
            sphere = Part.makeSphere(self.sphere_radius, FreeCAD.Vector(0, 0, 0))

            for finger_id in range(5):
                # Create line
                line_name = f"FingerLine_{finger_id}"
                line_obj = FreeCAD.ActiveDocument.addObject("Part::Feature", line_name)
                line_obj.Shape = origin_line
                line_obj.ViewObject.LineColor = self.finger_colors[finger_id]
                line_obj.ViewObject.LineWidth = 4.0
                self.finger_lines[line_name] = line_obj

                # Create sphere
                sphere_name = f"FingerSphere_{finger_id}"
                sphere_obj = FreeCAD.ActiveDocument.addObject("Part::Feature", sphere_name)
                sphere_obj.Shape = sphere
                sphere_obj.ViewObject.ShapeColor = self.finger_colors[finger_id]
                self.finger_spheres[sphere_name] = sphere_obj

            FreeCAD.ActiveDocument.recompute()

        except Exception as e:
            print(f"Error creating initial objects: {e}")
            import traceback
            traceback.print_exc()

    def _transform_coordinates(self, x, y):
        """Transform webcam coordinates to FreeCAD coordinates."""
        # Normalize coordinates to [-1, 1] range
        x_norm = (x / self.cam_width) * 2 - 1
        y_norm = -((y / self.cam_height) * 2 - 1)  # Flip Y axis

        # Scale to FreeCAD working area
        x_freecad = x_norm * (self.freecad_width / 2)
        y_freecad = y_norm * (self.freecad_height / 2)

        return x_freecad, y_freecad

    def _create_line(self, finger_id, x, y):
        """Queue update for processing."""
        self.pending_updates[finger_id] = (x, y)

    def _snap_lines_to_origin(self):
        """Safely snap all lines and spheres to origin in the main thread."""
        try:
            # Create a very short line at origin
            origin_line = Part.makeLine(
                FreeCAD.Vector(0, 0, 0),
                FreeCAD.Vector(0.1, 0.1, 0)
            )

            # Create a sphere at origin with normal size
            origin_sphere = Part.makeSphere(self.sphere_radius, FreeCAD.Vector(0, 0, 0))

            # Update each line and sphere
            for finger_id in range(5):
                line_name = f"FingerLine_{finger_id}"
                sphere_name = f"FingerSphere_{finger_id}"

                if line_name in self.finger_lines:
                    self.finger_lines[line_name].Shape = origin_line

                if sphere_name in self.finger_spheres:
                    self.finger_spheres[sphere_name].Shape = origin_sphere

            FreeCAD.ActiveDocument.recompute()
            print("Objects reset to origin")

        except Exception as e:
            print(f"Error snapping objects to origin: {e}")
            import traceback
            traceback.print_exc()

    def process_server_data(self, data):
        """Process the data received from the server."""
        if not FreeCAD.ActiveDocument:
            print("No active document!")
            return

        try:
            finger_data_list = data.split(";")

            # If we don't see exactly 5 fingers, snap all lines to origin
            if len(finger_data_list) != 5:
                self.snap_signal.emit()
                # Update labels for all fingers as not visible
                for i in range(5):
                    self._update_label(i, None, None)
                return

            # Process finger positions
            for finger_data in finger_data_list:
                parts = finger_data.split(",")
                if len(parts) != 3:
                    continue

                finger_id, x, y = map(float, parts)
                # Update label
                self._update_label(int(finger_id), x, y)
                # Queue update
                self.update_signal.emit(int(finger_id), x, y)

        except Exception as e:
            print(f"Error processing data: {e}")
            import traceback
            traceback.print_exc()

    def _update_label(self, finger_id, x, y):
        """Update the label text for a specific finger."""
        if x is None or y is None:
            text = f"Finger {finger_id}: Not visible"
        else:
            text = f"Finger {finger_id}: x={x:.1f}, y={y:.1f}"

        if finger_id == 0:
            self.finger_0_label.setText(text)
        elif finger_id == 1:
            self.finger_1_label.setText(text)
        elif finger_id == 2:
            self.finger_2_label.setText(text)
        elif finger_id == 3:
            self.finger_3_label.setText(text)
        elif finger_id == 4:
            self.finger_4_label.setText(text)

    def _initialize_labels(self):
        """Initialize labels."""
        try:
            self.finger_0_label = self._create_label("Finger 0: Waiting...", 10, 10)
            self.finger_1_label = self._create_label("Finger 1: Waiting...", 10, 50)
            self.finger_2_label = self._create_label("Finger 2: Waiting...", 10, 90)
            self.finger_3_label = self._create_label("Finger 3: Waiting...", 10, 130)
            self.finger_4_label = self._create_label("Finger 4: Waiting...", 10, 170)
            self.gesture_label = self._create_gesture_label("No gesture detected", 10, 210)
        except Exception as e:
            print(f"Error initializing labels: {e}")

    def _create_label(self, text, x, y):
        label = QLabel(self.main_window)
        label.setText(text)
        label.setStyleSheet(
            "QLabel { background-color: black; color: white; padding: 5px; border-radius: 5px; }"
        )
        label.setGeometry(x, y, 300, 30)
        label.show()
        return label

    def _create_gesture_label(self, text, x, y):
        label = QLabel(self.main_window)
        label.setText(text)
        label.setStyleSheet(
            "QLabel { background-color: #2E86C1; color: white; padding: 8px; "
            "border-radius: 8px; font-weight: bold; font-size: 14px; }"
        )
        label.setGeometry(x, y, 300, 40)
        label.show()
        return label

    def start_server(self):
        """Start the server and listen for incoming connections."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 12340))
        server.listen(1)
        print("FreeCAD server listening on port 12340...")

        try:
            while True:
                client, address = server.accept()
                print(f"Connection from {address} has been established.")

                try:
                    while True:
                        data = client.recv(1024).decode('utf-8')
                        if not data:
                            print(f"Client {address} disconnected.")
                            break

                        self.process_server_data(data)
                except (socket.error, ConnectionResetError) as e:
                    print(f"Connection error with {address}: {e}")
                finally:
                    client.close()
                    print(f"Connection with {address} has been closed.")

        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            server.close()

    def run_server_in_thread(self):
        """Run the server in a background thread."""
        server_thread = threading.Thread(
            target=self.start_server,
            daemon=True
        )
        server_thread.start()
        print("Server thread started")