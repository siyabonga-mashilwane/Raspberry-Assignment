import socket
import cv2
import pickle
import struct
import time
from picamera2 import Picamera2
from gpiozero import MotionSensor
from signal import pause

pir = MotionSensor(4)  # Set your correct GPIO pin here

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('raspberrypi.local', 8000))
server.listen(5)

print("Raspberry Pi server started. Waiting for connection...")
client, client_addr = server.accept()
print(f"Connection from {client_addr} accepted")

width = 640
height = 360
pos = (30, 60)
font = cv2.FONT_HERSHEY_SIMPLEX
TextHeight = 1.5
color = (255, 255, 255)
weight = 3

cam = Picamera2()
cam.preview_configuration.main.size = (width, height)
cam.preview_configuration.main.format = "RGB888"
cam.preview_configuration.main.align()
cam.configure("preview")
def on_motion():
    print("Motion detected!")
    try:
        cam.start()
        print("Recording...")
        fps = 0
        while True:
            start = time.time()
            frame = cam.capture_array()
            if frame is None:
                print("No frame captured.")
                break

            cv2.putText(frame, str(int(fps)) + " FPS", pos, font, TextHeight, color, weight)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            message_size = struct.pack("!I", len(frame_data))
            client.sendall(message_size)
            client.sendall(frame_data)

            end = time.time()
            diff = end - start
            fps = .9 * fps + .1 * (1 / diff)
    except KeyboardInterrupt:
        print("Server stopped...")
    finally:
        cam.stop()
        cam.close()
        client.close()
        server.close()
        cv2.destroyAllWindows()
        print("Cleaned up resources.")

try:
    print("Waiting for motion...")
    pir.when_motion = on_motion
    pir.when_no_motion = lambda: print("No motion.")
    pause()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    cv2.destroyAllWindows()
    print("Cleaned up resources.")
