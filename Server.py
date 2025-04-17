from gpiozero import MotionSensor
from signal import pause
from picamera import PiCamera2
import cv2

import time
import RPi.GPIO as GPIO

pir = MotionSensor(17)  # GPIO pin for PIR sensor

def on_motion():
	cam= PiCamera2()
	cam.preview_configuration.main.size = (640, 480)
	cam.preview_configuration.main.format = "RGB888"
	cam.preview_configuration.main.align()
	cam.configure("preview")
	cam.start()
	
	print("Motion detected! Recording...")

	timestamp = time.strftime("%Y%m%d-%H%M%S")
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter(f'motion_{timestamp}.mp4', fourcc, 30.0, (640, 480))

	start_time = time.time()
	record_duration = 30  # seconds
	while (time.time() - start_time < record_duration):
		picture = cam.capture_array()
		out.write(picture)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	out.release()
	cam.release()  # Release camera
	cv2.destroyAllWindows()
	print("Recording stopped.")

try:
	print("Waiting for motion...")
	pir.when_motion = on_motion
	pir.when_no_motion = lambda: print("No motion.")
	pause()
except KeyboardInterrupt:
	print("Exiting...")
finally:
	cv2.destroyAllWindows()
	GPIO.cleanup()

	print("Cleaned up resources.")