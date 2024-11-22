import socket
import cv2
import mediapipe as mp

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Set up the socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12340)

# Open webcam
cap = cv2.VideoCapture(0)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

print(f"Default resolution: {int(width)}x{int(height)}")

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

print(f"Default resolution: {int(width)}x{int(height)}")
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


# MARK NOTE: Only really needed to you really wanna check for a fist. Otherwise, it just does nothing but that. If you
# decide you want this, there's also another bit you need to uncomment too. Just ctrl+f is_fist() to find it.

def is_fist(hand_landmarks):
    """Determine if the hand forms a fist based on fingertip proximity to the palm."""


    # Define distances between fingertip and respective base joints
    fingertips = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]

    bases = [
        mp_hands.HandLandmark.THUMB_CMC,
        mp_hands.HandLandmark.INDEX_FINGER_MCP,
        mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
        mp_hands.HandLandmark.RING_FINGER_MCP,
        mp_hands.HandLandmark.PINKY_MCP
    ]

    for tip, base in zip(fingertips, bases):
        tip_z = hand_landmarks.landmark[tip].z
        base_z = hand_landmarks.landmark[base].z
        print(f"Tip Z: {tip_z}, Base Z: {base_z}, Difference: {tip_z - base_z}")

        if tip_z - base_z > -0.1:  # Adjust this threshold based on testing
            print(f"Finger {tip} not forming a fist.")
            return False
    return True


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

        #Check for a fist
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if is_fist(hand_landmarks):
                    client.send("fist_detected".encode('utf-8'))
                else:
                    coord_str = format_coordinates(hand_landmarks, frame.shape)
                    client.send(coord_str.encode('utf-8'))

        # Display frame (optional - will still work without seeing camera feed)
        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    client.close()
    cv2.destroyAllWindows()