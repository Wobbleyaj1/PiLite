#!/usr/bin/env python3

import atexit
import os
import signal
import sys
import time

from IR.remote import IRRemote
from Mobile_Notifications.pushsafer import PushsaferNotification
from RGB_Strips.rgb_controller import RGBController
from Ultrasonic_Sensor.ultrasonic import HCSR04
from startup import (
    cleanup,
    create_and_activate_venv,
    load_environment_variables,
    start_pigpiod,
)

# Initialize and activate the virtual environment
venv_path = "/home/pi/PiLite/venv"
create_and_activate_venv(venv_path)

# Ensure pigpiod is running
start_pigpiod()

# Load environment variables
secret_key = load_environment_variables()

# Initialize the RGB controller
controller = RGBController()

# Initialize the IR remote with the shared RGB controller
ir_remote = IRRemote(
    pin=17,
    ir_code_file="/home/pi/PiLite/config/ir_code_ff.txt",
    private_key=secret_key,
    controller=controller
)

# Initialize the ultrasonic sensor
ultrasonic_sensor = HCSR04(trigger_pin=23, echo_pin=24)

# Initialize the Pushsafer notification system
pushsafer_notifier = PushsaferNotification(private_key=secret_key)

def cleanup_resources():
    """
    Cleans up resources for the RGB controller, ultrasonic sensor, and pigpiod.
    """
    print("Cleaning up resources...")
    controller.clear_strip()
    ultrasonic_sensor.cleanup()
    cleanup()

# Register cleanup function to execute on program exit
atexit.register(cleanup_resources)

def signal_handler(sig, frame):
    """
    Handles SIGINT (Ctrl+C) for graceful shutdown.
    """
    print("\nExiting... Cleaning up resources.")
    sys.exit(0)

# Register signal handler for SIGINT
signal.signal(signal.SIGINT, signal_handler)

def main():
    """
    Main function to manage IR remote and ultrasonic sensor functionality.
    Dynamically adjusts LED brightness based on distance and sends notifications for inactivity.
    """
    if not ir_remote.pi.connected:
        print("Failed to connect to pigpiod. Exiting.")
        sys.exit(1)

    try:
        while True:
            try:
                # Measure distance using the ultrasonic sensor
                distance = ultrasonic_sensor.get_distance()

                # Check for inactivity and send a notification if needed
                if controller.last_change_time and time.time() - controller.last_change_time > 300:
                    pushsafer_notifier.send_trunk_open_notification()
                    
                    controller.clear_strip()
                    
                    print("Shutting down the Raspberry Pi...")
                    os.system("sudo shutdown -h now")
                    break

                # Determine target brightness based on distance
                target_brightness = ultrasonic_sensor.calculate_brightness(distance, controller.max_brightness)

                # Gradually adjust brightness to the target value
                controller.adjust_to_target_brightness(target_brightness)

            except RuntimeError as e:
                print(f"Error reading distance: {e}")

            # Prevent excessive CPU usage
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass  # Cleanup is handled by the signal handler

if __name__ == "__main__":
    main()