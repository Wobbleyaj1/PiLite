from IR.remote import IRRemote
from dotenv import load_dotenv
import os
import signal
import sys
import subprocess
import time

# Create and activate virtual environment
venv_path = "/home/pi/PiLite/venv"
if not os.path.exists(venv_path):
    os.system(f'python3 -m venv {venv_path}')
subprocess.run([f'{venv_path}/bin/pip', 'install', '-r', 'requirements.txt'])

# Start pigpiod if not already running
def start_pigpiod():
    result = subprocess.run(['pgrep', 'pigpiod'], capture_output=True, text=True)
    if result.returncode != 0:
        subprocess.run(['sudo', 'pigpiod'])
        time.sleep(2)  # Add a delay to ensure pigpiod has time to start
    else:
        print("pigpiod is already running")

start_pigpiod()
load_dotenv()

secret_key = os.getenv('SECRET_KEY')

def cleanup():
    """
    Cleanup function to stop pigpiod and perform other necessary cleanup.
    """
    subprocess.run(['sudo', 'killall', 'pigpiod'])
    print("Cleanup completed.")

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