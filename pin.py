import time
import RPi.GPIO as GPIO


# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set up GPIO pin 17 as an input
GPIO.setup(14, GPIO.OUT, initial=GPIO.LOW)
# Loop indefinitely
while True:
    # Read the state of the GPIO pin
    pin_state = GPIO.input(14)
    print("Pin state: ", pin_state)
    time.sleep(1.0)

# Clean up the GPIO pins
GPIO.cleanup()
