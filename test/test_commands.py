from setup import setup_freecad_env
setup_freecad_env()

from commands import CommandProcessor

import socket
import threading
import FreeCAD
import FreeCADGui
import Part

class ServerConnect:
    def __init__(self, process_data_callback, doc):

        self.process_data_callback = process_data_callback

        self.CommandProcessor = CommandProcessor(doc)

    def start_server(self):
        """
        Start the server and listen for incoming connections.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 12345))
        server.listen(1)
        print("FreeCAD server listening on port 12345...")

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

                        print(f"Received coordinates: {data}")
                        self.process_data_callback(data)  # Send data to callback function
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
        """
        Run the server in a background thread to avoid blocking the main application.
        """
        server_thread = threading.Thread(
            target=self.start_server,
            daemon=True
        )
        server_thread.start()

    def process_server_data(self, data):
        """Process the data received from the server and update commands in FreeCAD."""
        try:
            if data.startswith("Select"):
                # Split the message to extract coordinates
                command, coordinates = data.split(',', 1)
                x, y = coordinates.split(',')
                x, y = float(x), float(y)
                z = 0  # For simplicity, modify for 3D interaction

                # Print the received coordinates for debugging
                print(f"Received Select command with coordinates: x={x}, y={y}")

                # Create or update an object in FreeCAD at the received location (e.g., create a sphere)
                self._create_object_at_coordinates(x, y, z)

            else:
                # Handle other types of commands (Move,
                print(f"Received unknown command: {data}")

        except ValueError as e:
            print(f"Error processing data: {e}")
            self.command_window.history_display.append("Invalid data format received.")

    def _create_object_at_coordinates(self, x, y, z):

        # Create a sphere (or any other object) at the given coordinates
        sphere = CommandProcessor._create_sphere(['1'])
        sphere.Placement = FreeCAD.Placement(FreeCAD.Vector(x, y, z), FreeCAD.Rotation())

        # Add the object to the document
        FreeCAD.ActiveDocument.addObject("Part::Feature", "Sphere").Shape = sphere
        FreeCAD.ActiveDocument.recompute()

        # Optionally, select the object in the 3D view
        FreeCADGui.Selection.addSelection(FreeCAD.ActiveDocument.ActiveObject)
