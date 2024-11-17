import socket

# Set up the server to listen for incoming connections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen(1)
print("FreeCAD server listening on port 12345...")

try:
    while True:
        # Accept a connection from the client
        client, address = server.accept()
        print(f"Connection from {address} has been established.")

        try:
            while True:
                # Receive data from the client
                data = client.recv(1024).decode('utf-8')
                if not data:
                    print(f"Client {address} disconnected.")
                    break

                print(f"Received coordinates: {data}")
        except (socket.error, ConnectionResetError) as e:
            print(f"Connection error with {address}: {e}")
        finally:
            client.close()
            print(f"Connection with {address} has been closed.")

except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    server.close()
