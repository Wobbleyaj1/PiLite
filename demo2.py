#!/usr/bin/env python3
from RGB_Strips.rgb_controller import RGBController
from IR.remote import IRRemote
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

# Create instances of RGBController and IRRemote
controller = RGBController()
ir_remote = IRRemote(pin=17, ir_code_file="/home/pi/PiLite/config/ir_code_ff.txt", private_key=secret_key)

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    """
    Signal handler for SIGINT (Ctrl+C).
    Cleans up resources for both RGBController and IRRemote.
    """
    print("\nExiting... Cleaning up resources.")
    controller.clear_strip()  # Clear the LEDs
    cleanup()  # Cleanup for IRRemote and other resources
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    """
    Main function to run both the RGBController menu and IRRemote functionality.
    """
    if not ir_remote.pi.connected:
        print("Failed to connect to pigpiod. Exiting.")
        sys.exit(1)

    # Run IRRemote in a separate thread
    import threading
    ir_thread = threading.Thread(target=ir_remote.read_ir_code, daemon=True)
    ir_thread.start()

    # Run the RGBController menu
    try:
        controller.run_menu()
    except KeyboardInterrupt:
        # Signal handler will handle cleanup
        pass

if __name__ == "__main__":
    main()