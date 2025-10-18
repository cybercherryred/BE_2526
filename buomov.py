import RPi.GPIO as GPIO
import time
import smbus
import ms5837
import sys
import cgi
import cgitb
import datetime
import webbrowser
import threading
import collect_data
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from gpiozero import MCP3008

#Configuration
PUMP_PIN = 18         # GPIO pin connected to pump control (relay or MOSFET)
INFLATE_TIME = 8      # Seconds
DEFLATE_TIME = 8      # Seconds

#Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUMP_PIN, GPIO.OUT)

def pump_on():
    GPIO.output(PUMP_PIN, GPIO.HIGH)
    print("Pump ON")

def pump_off():
    GPIO.output(PUMP_PIN, GPIO.LOW)
    print("Pump OFF")

def inflate(duration=INFLATE_TIME):
    print(f"Filling for 8 seconds")
    pump_on()
    time.sleep(duration)
    pump_off()
    print("Full.")

def deflate(duration=DEFLATE_TIME):
    print(f"Emptying for 8 seconds")
    pump_on()
    time.sleep(duration)
    pump_off()
    print("Empty.")

def cleanup():
    GPIO.cleanup()
    print("GPIO cleanup done.")

#Main Execution
if __name__ == "__main__":
    try:
        inflate()
        time.sleep(10)
        deflate()
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        cleanup()
