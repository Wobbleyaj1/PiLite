from IR.remote import IRRemote
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

def signal_handler(sig, frame):
    """
    Signal handler for SIGINT (Ctrl+C).
    """
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    """
    Main function to create an IRRemote instance and start reading IR codes.
    """
    ir_remote = IRRemote(pin=17, ir_code_file="/home/pi/PiLite/config/ir_code_ff.txt", private_key=secret_key)
    if not ir_remote.pi.connected:
        print("Failed to connect to pigpiod. Exiting.")
        sys.exit(1)
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()