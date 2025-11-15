import RPi.GPIO as GPIO
import time

# Set the GPIO mode (BCM or BOARD)
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin controls the pump via the relay module
RELAY_PIN = 12

# Set the relay pin as an output pin
GPIO.setup(RELAY_PIN, GPIO.OUT)

try:
    # Run the loop function indefinitely
    while True:
        # Turn the relay ON (HIGH) to turn on the pump
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        time.sleep(5)  # Wait for 5 seconds

        # Turn the relay OFF (LOW) to turn off the pump
        GPIO.output(RELAY_PIN, GPIO.LOW)
        time.sleep(5)  # Wait for 5 seconds

except KeyboardInterrupt:
    # If the user presses Ctrl+C, clean up the GPIO configuration
    GPIO.cleanup()
