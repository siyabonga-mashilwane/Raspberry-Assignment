import socket
import cv2
import pickle
import struct
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('raspberrypi.local', 8000))
data = b""
payload_size = struct.calcsize("L")
conn = sock.makefile('rb')

try:
    print("Connected to server. Receiving video stream...")
    count = 0
    while True:
        print("Receiving data from frame {}".format(count))
        while len(data) < payload_size:
            packet = sock.recv(4 * 1024)
            if not packet:
                break
            data += packet
        if not packet:
            break
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += sock.recv(4 * 1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        if frame is None:
            print("No frame received.")
            break
        print("Frame shape: {}".format(frame))
        cv2.imshow("Stream", frame)
        count += 1
        if cv2.waitKey(1) == ord('q'):
            break
        # Alternative method using cv2.imdecode
        #size_bytes = conn.read(4)
        #size = int.from_bytes(size_bytes, 'big')
        #data = conn.read(size)
        #img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        #cv2.imshow("Stream", img)
        #if cv2.waitKey(1) == ord('q'):
        #    break
except KeyboardInterrupt:
    pass
finally:
    sock.close()
    cv2.destroyAllWindows()