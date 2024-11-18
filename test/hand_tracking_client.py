import socket
import cv2
import mediapipe as mp

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Set up the socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12345)

# Open webcam
cap = cv2.VideoCapture(0)


def format_coordinates(hand_landmarks, frame_shape):
    """matrix format: finger_id,x,y;finger_id,x,y;..."""
    finger_coords = []

    # finger landmarks in order: thumb, index, middle, ring, pinky
    fingers = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]

    # Get coordinates for each finger
    for finger_id, landmark_id in enumerate(fingers):
        landmark = hand_landmarks.landmark[landmark_id]
        x = int(landmark.x * frame_shape[1])
        y = int(landmark.y * frame_shape[0])

        # Only add if coordinates are within frame
        if 0 <= x < frame_shape[1] and 0 <= y < frame_shape[0]:
            finger_coords.append(f"{finger_id},{x},{y}")

    return ";".join(finger_coords) + "\n"


# Connect to server
try:
    client.connect(server_address)
    print(f"Connected to server at {server_address}")
except Exception as e:
    print(f"Connection error: {e}")
    exit(1)

# Main loop
try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip and convert frame to RGB
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Format and send coordinates
                coord_str = format_coordinates(hand_landmarks, frame.shape)
                client.send(coord_str.encode('utf-8'))
                print(f"Sent: {coord_str.strip()}")  # Strip to remove newline when printing

        # Display frame (optional - will still work without seeing camera feed)
        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    client.close()
    cv2.destroyAllWindows()