from IR.remote import IRRemote
from Mobile_Notifications.pushsafer import PushsaferNotification
import signal
import sys
from startup import create_and_activate_venv, start_pigpiod, load_environment_variables, cleanup

### Demo 1: IR Remote Control ###
# This demo shows how to create an IRRemote instance and start reading IR codes.

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
    def command_0():
        notifier = PushsaferNotification(private_key=secret_key)
        notifier.send_notification(
            message="You Left Your Lights On",  # The message text
            title="PiLite",                     # The title of the message
            icon="24",                          # The icon number
            sound="10",                         # The sound number
            vibration="1",                      # The vibration number
            picture=""                          # The picture data URL (optional)
        )
        print("Command 0 executed and notification sent")

    commands = {
        '0': command_0,
        '1': lambda: print("Command 1 executed"),
        '2': lambda: print("Command 2 executed"),
        '3': lambda: print("Command 3 executed"),
        '4': lambda: print("Command 4 executed"),
        '5': lambda: print("Command 5 executed"),
        '6': lambda: print("Command 6 executed"),
        '7': lambda: print("Command 7 executed"),
        '8': lambda: print("Command 8 executed"),
        '9': lambda: print("Command 9 executed"),
        '-': lambda: print("Command - executed"),
        '+': lambda: print("Command + executed"),
        'EQ': lambda: print("Command EQ executed"),
        '<': lambda: print("Command < executed"),
        '>': lambda: print("Command > executed"),
        '>||': lambda: print("Command >|| executed"),
        'CH+': lambda: print("Command CH+ executed"),
        'CH': lambda: print("Command CH executed"),
        'CH-': lambda: print("Command CH- executed")
    }

    ir_remote = IRRemote(pin=17, ir_code_file="/home/pi/PiLite/config/ir_code_ff.txt", private_key=secret_key, commands=commands)
    if not ir_remote.pi.connected:
        print("Failed to connect to pigpiod. Exiting.")
        sys.exit(1)
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()