#!/usr/bin/env python3
from RGB_Strips.rgb_controller import RGBController
from IR.remote import IRRemote
from Ultrasonic_Sensor.ultrasonic import HCSR04
import time
import signal
import sys
from startup import create_and_activate_venv, start_pigpiod, load_environment_variables, cleanup

# Create and activate virtual environment
venv_path = "/home/pi/PiLite/venv"
create_and_activate_venv(venv_path)

# Start pigpiod if not already running
start_pigpiod()

# Load environment variables
secret_key = load_environment_variables()

# Create a single instance of RGBController
controller = RGBController()

# Create an instance of IRRemote and pass the shared RGBController instance
ir_remote = IRRemote(pin=17, ir_code_file="/home/pi/PiLite/config/ir_code_ff.txt", private_key=secret_key, controller=controller)

# Create an instance of the ultrasonic sensor
ultrasonic_sensor = HCSR04(trigger_pin=23, echo_pin=24)

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    """
    Signal handler for SIGINT (Ctrl+C).
    Cleans up resources for both RGBController and IRRemote.
    """
    print("\nExiting... Cleaning up resources.")
    controller.clear_strip()  # Clear the LEDs
    ultrasonic_sensor.cleanup()  # Cleanup GPIO for ultrasonic sensor
    cleanup()  # Cleanup for pigpiod and other resources
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    """
    Main function to handle both IRRemote and ultrasonic sensor functionality in a single loop.
    """
    if not ir_remote.pi.connected:
        print("Failed to connect to pigpiod. Exiting.")
        sys.exit(1)

    try:
        while True:
            # Handle IR remote functionality
            ir_remote.read_ir_code()

            # Handle ultrasonic sensor functionality
            try:
                distance = ultrasonic_sensor.get_distance()
                if distance <= 10:
                    brightness = 0  # 0% of maximum brightness
                elif distance >= 100:
                    brightness = controller.max_brightness  # 100% of maximum brightness
                else:
                    # Scale brightness linearly between 10cm and 100cm
                    brightness = int((distance - 10) / 90 * controller.max_brightness)

                controller.adjust_brightness(brightness - controller.brightness)
                print(f"Distance: {distance:.2f} cm, Brightness: {brightness}")
            except RuntimeError as e:
                print(f"Error reading distance: {e}")

            # Add a small delay to prevent excessive CPU usage
            time.sleep(0.1)

    except KeyboardInterrupt:
        # Signal handler will handle cleanup
        pass

if __name__ == "__main__":
    main()