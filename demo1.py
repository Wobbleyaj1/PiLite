from IR.remote import IRRemote
from dotenv import load_dotenv
import os
import signal
import sys

# Create and activate virtual environment
venv_path = "/home/pi/PiLite/venv"
if not os.path.exists(venv_path):
    os.system(f'python3 -m venv {venv_path}')
os.system(f'{venv_path}/bin/pip install -r requirements.txt')
os.system('sudo pigpiod')
load_dotenv()

secret_key = os.getenv('SECRET_KEY')

def cleanup():
    """
    Cleanup function to stop pigpiod and perform other necessary cleanup.
    """
    os.system('sudo killall pigpiod')
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
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()