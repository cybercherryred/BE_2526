import time
import board
import digitalio
import adafruit_mprls  # Example pressure sensor library; replace with yours
import busio
import csv

# --- Setup I2C for pressure sensor ---
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)  # adjust for your sensor

# --- Setup H-bridge pins ---
in1 = digitalio.DigitalInOut(board.D17)  # GPIO pin for pump direction
in1.direction = digitalio.Direction.OUTPUT

in2 = digitalio.DigitalInOut(board.D27)  # GPIO pin for pump direction
in2.direction = digitalio.Direction.OUTPUT

def pump_fill():
    """Pump water into chamber (descend)."""
    in1.value = True
    in2.value = False

def pump_empty():
    """Pump water out of chamber (ascend)."""
    in1.value = False
    in2.value = True

def pump_stop():
    """Stop pump."""
    in1.value = False
    in2.value = False

def read_depth():
    """Convert pressure sensor reading to depth (m)."""
    pressure_pa = sensor.pressure  # raw pressure in Pascals
    depth_m = pressure_pa / (1000 * 9.81)  # rough conversion: Pa → m water column
    return depth_m

# --- PID Controller ---
class PIDController:
    def __init__(self, Kp=1.0, Ki=0.0, Kd=0.0, tolerance=0.05):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.tolerance = tolerance
        self.integral = 0
        self.last_error = 0
        self.last_time = time.monotonic()

    def compute(self, target, current):
        error = target - current
        now = time.monotonic()
        dt = now - self.last_time if self.last_time else 0.1

        # PID terms
        self.integral += error * dt
        derivative = (error - self.last_error) / dt if dt > 0 else 0

        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)

        # Save state
        self.last_error = error
        self.last_time = now

        return output, error

def go_to_depth(target_depth, pid: PIDController, log_writer):
    """Use PID loop to reach target depth with logging."""
    print(f"Target depth: {target_depth} m")
    while True:
        depth = read_depth()
        output, error = pid.compute(target_depth, depth)

        # Log data
        log_writer.writerow({
            "time": time.time(),
            "target_depth": target_depth,
            "current_depth": depth,
            "error": error,
            "pid_output": output,
            "pump_action": "fill" if output > 0 else "empty" if output < 0 else "stop"
        })

        if abs(error) <= pid.tolerance:
            pump_stop()
            print(f"Holding at {depth:.2f} m")
            break

        if output > 0:
            pump_fill()
        else:
            pump_empty()

        time.sleep(0.5)  # loop interval

# --- Mission sequence ---
def mission():
    print("Starting mission...")

    pid = PIDController(Kp=1.2, Ki=0.1, Kd=0.05, tolerance=0.05)

    # Open CSV log file
    with open("mission_log.csv", mode="w", newline="") as logfile:
        fieldnames = ["time", "target_depth", "current_depth", "error", "pid_output", "pump_action"]
        log_writer = csv.DictWriter(logfile, fieldnames=fieldnames)
        log_writer.writeheader()

        # Descend to 0.4m
        go_to_depth(0.4, pid, log_writer)
        time.sleep(10)

        # Descend to 2.5m
        go_to_depth(2.5, pid, log_writer)
        time.sleep(10)

        # Ascend to near surface (e.g., 0.1m)
        go_to_depth(0.1, pid, log_writer)

    print("Mission complete. Log saved to mission_log.csv.")

if __name__ == "__main__":
    mission()