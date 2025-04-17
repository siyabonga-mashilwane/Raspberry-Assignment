from gpiozero import MotionSensor
from signal import pause

# Initialize the PIR sensor on GPIO 17
pir = MotionSensor(17)

# Event handler for motion detected
def motion_detected():
    print("Motion detected!")

# Event handler for no motion
def no_motion():
    print("No motion detected.")

# Assign event handlers
pir.when_motion = motion_detected
pir.when_no_motion = no_motion

# Keep the script running
print("Testing motion sensor on GPIO 17. Press Ctrl+C to exit.")
pause()