import socket
import cv2
import pickle
import struct
import time
from picamera2 import Picamera2
from signal import pause
from gpiozero import MotionSensor

# Initialize the motion sensor on GPIO pin 17
pir = MotionSensor(17)  # Make sure this pin matches your setup

# Set up a socket server that listens for incoming connections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('raspberrypi.local', 8000))  # Replace 'raspberrypi.local' with your Pi's hostname or IP if needed
server.listen(5)

print("Raspberry Pi server started. Waiting for connection...")

# Accept a connection from a client
client, client_addr = server.accept()
print(f"Connection from {client_addr} accepted")

# Function to execute when motion is detected
def on_motion():
    print("Motion detected!")
    try:
        # Set camera configuration parameters
        width = 640
        height = 360
        pos = (30, 60)  # Position for the FPS text on the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        TextHeight = 1.5
        color = (255, 255, 255)  # White text
        weight = 3

        # Initialize the Picamera2
        cam = Picamera2()
        cam.preview_configuration.main.size = (width, height)
        cam.preview_configuration.main.format = "RGB888"
        cam.preview_configuration.main.align()
        cam.configure("preview")
        cam.start()
        print("Recording...")

        fps = 0
        start_record = time.time()
        recording_duration = 300  # Record for 5 minutes (300 seconds)

        while True:
            # Stop recording after 5 minutes
            if time.time() - start_record > recording_duration:
                print("Recording stopped after 5 minutes.")
                break

            start = time.time()

            # Capture a frame from the camera
            frame = cam.capture_array()
            if frame is None:
                print("No frame captured.")
                break

            # Display FPS on the frame
            cv2.putText(frame, str(int(fps)) + " FPS", pos, font, TextHeight, color, weight)

            # Serialize frame using pickle and send to client with size header
            frame_data = pickle.dumps(frame)
            message_size = struct.pack("L", len(frame_data))  # Pack message size in bytes
            client.sendall(message_size)
            client.sendall(frame_data)

            # Update FPS calculation
            end = time.time()
            diff = end - start
            fps = .9 * fps + .1 * (1 / diff)

    except KeyboardInterrupt:
        print("Server stopped...")

    finally:
        # Release resources when done
        cam.stop()
        cam.close()
        client.close()
        server.close()
        cv2.destroyAllWindows()
        print("Cleaned up resources.")

# Set up motion detection event listeners
try:
    print("Waiting for motion...")
    pir.when_motion = on_motion  # Call on_motion() when motion is detected
    pir.when_no_motion = lambda: print("No motion.")  # Log when no motion is detected
    pause()  # Keep the script running
except KeyboardInterrupt:
    print("Exiting...")
finally:
    cv2.destroyAllWindows()
    print("Cleaned up resources.")