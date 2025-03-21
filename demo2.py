#!/usr/bin/env python3
from RGB_Strips.rgb_controller import RGBController
from IR.remote import IRRemote
from Ultrasonic_Sensor.ultrasonic import HCSR04
import time
import signal
import sys
from startup import create_and_activate_venv, start_pigpiod, load_environment_variables, cleanup
from Mobile_Notifications.pushsafer import PushsaferNotification  # Import PushsaferNotification class
import os  # Import os for system commands

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

# Initialize PushsaferNotification with your private key
pushsafer_notifier = PushsaferNotification(private_key=secret_key)  # Replace with your Pushsafer private key

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
            try:
                distance = ultrasonic_sensor.get_distance()

                # Check for inactivity (10 minutes = 600 seconds)
                if controller.last_change_time is not None and time.time() - controller.last_change_time > 30:

                    # Send a notification using Pushsafer
                    pushsafer_notifier.send_notification(
                        message="Trunk was left open.",
                        title="PiLite Alert",
                        icon="24",  # Example icon number
                        sound="10",  # Example sound number
                        vibration="1",  # Example vibration setting
                        picture=""  # Optional: Add a picture URL or leave empty
                    )

                    controller.clear_strip()
                    continue

                print(f"last_change_time: {controller.last_change_time}")
                if controller.last_change_time is None and distance > 10:
                    controller.activate_static_color()
                    continue

                # Adjust brightness dynamically based on distance
                if distance <= 5:
                    target_brightness = 0  # 0% of maximum brightness
                elif distance >= 100:
                    target_brightness = controller.max_brightness  # 100% of maximum brightness
                else:
                    # Scale brightness linearly between 10cm and 100cm
                    target_brightness = int((distance - 10) / 90 * controller.max_brightness)

                # Gradually adjust brightness to the target value
                step = 1 if target_brightness > controller.brightness else -1
                for brightness in range(controller.brightness, target_brightness, step):
                    controller.adjust_brightness(step)
                    time.sleep(0.01)
            except RuntimeError as e:
                print(f"Error reading distance: {e}")
            # Add a small delay to prevent excessive CPU usage
            time.sleep(0.1)

    except KeyboardInterrupt:
        # Signal handler will handle cleanup
        pass

if __name__ == "__main__":
    main()