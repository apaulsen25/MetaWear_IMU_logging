
import threading
import RPi.GPIO as GPIO
import time
# Set up the GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

# Create an Event object
e1 = threading.Event()
e2 = threading.Event()
# Define a function to run in a separate thread
def monitor_pin():
    last_state = GPIO.input(18)
    while True:
        current_state = GPIO.input(18)
        print("Pin state: ", current_state)
        if current_state != last_state and current_state == GPIO.HIGH:
            print("Pin 18 has changed from low to high!")
            e1.set() # Set the Event object
        elif current_state != last_state and current_state == GPIO.LOW:
            print("Pin 18 has changed from low!")
            e2.set() # Set the Event object
        last_state = current_state
        time.sleep(1.0)

# Start the thread
t = threading.Thread(target=monitor_pin)
t.start()

# Main thread waits for the event before continuing
while True:
    e1.wait() # Wait for the Event object to be set
    print("Event received!")
    e1.clear() 
    e2.wait() # Wait for the Event object to be set
    print("Event !")
    e2.clear()
