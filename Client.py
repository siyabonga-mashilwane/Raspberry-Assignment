import socket
import cv2
import pickle
import struct
import numpy as np

# Create a socket to connect to the Raspberry Pi server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('raspberrypi.local', 8000))  # Replace with IP or hostname if needed

# Variables to hold incoming data
data = b""
payload_size = struct.calcsize("L")  # Determine the size of the packed message header (used to know frame size)
conn = sock.makefile('rb')  # Optional: create a file-like object from the socket (not used in current implementation)

try:
    print("Connected to server. Receiving video stream...")
    count = 0  # Frame counter for logging

    while True:
        print("Receiving data from frame {}".format(count))

        # Ensure that we have enough bytes for the header (size of frame)
        while len(data) < payload_size:
            packet = sock.recv(4 * 1024)  # Receive 4KB chunks
            if not packet:
                break  # Break if no packet received (server closed or error)
            data += packet

        if not packet:
            break  # Exit loop if no data (likely end of stream)

        # Extract the message size from the header
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]  # Unpack the message size

        # Keep receiving data until we have the full frame
        while len(data) < msg_size:
            data += sock.recv(4 * 1024)

        # Extract the frame data
        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Deserialize the frame
        frame = pickle.loads(frame_data)

        if frame is None:
            print("No frame received.")
            break

        # Optional: print frame shape or other info
        print("Frame shape: {}".format(frame.shape))

        # Display the frame
        cv2.imshow("Stream", frame)
        count += 1

        # Press 'q' to quit the video stream
        if cv2.waitKey(1) == ord('q'):
            break

        # --- Alternative method using imdecode (commented out) ---
        # This is useful if the server sends compressed JPEG images instead of raw numpy arrays
        # size_bytes = conn.read(4)
        # size = int.from_bytes(size_bytes, 'big')
        # data = conn.read(size)
        # img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        # cv2.imshow("Stream", img)
        # if cv2.waitKey(1) == ord('q'):
        #     break

except KeyboardInterrupt:
    # Graceful exit on Ctrl+C
    pass

finally:
    # Cleanup on exit
    sock.close()
    cv2.destroyAllWindows()
    print("Socket closed and resources cleaned up.")