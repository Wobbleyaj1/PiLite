import time
import os
from Mobile_Notifications.pushsafer import PushsaferNotification
from IR.remote_test import IRRemote

# Constants
IR_PIN = 17  # GPIO pin for IR receiver
NOTIFICATION_THRESHOLD = 180  # 3 minutes in seconds
PRIVATE_KEY = "YOUR_PRIVATE_KEY"  # Replace with your actual private key

# Variables
last_ir_command_time = 0
trunk_open_time = 0
notification_sent = False

def initialize_system():
    global ir_remote, notifier
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ir_code_file = os.path.join(base_dir, "config", "ir_code_ff.txt")
    ir_remote = IRRemote(pin=IR_PIN, ir_code_file=ir_code_file)
    notifier = PushsaferNotification(private_key=PRIVATE_KEY)
    print("System initialized")

def check_ir_input():
    global last_ir_command_time
    # This function will be called by the IRRemote class when an IR signal is received
    last_ir_command_time = time.time()
    print("IR command received")
    # Handle IR command (e.g., update LED settings)
    # ...

def handle_notifications():
    global trunk_open_time, notification_sent
    current_time = time.time()
    if trunk_open_time > 0 and (current_time - trunk_open_time) > NOTIFICATION_THRESHOLD:
        if not notification_sent:
            notifier.send_notification(
                message="Trunk has been open for more than 3 minutes!",
                title="PiLite",
                icon="24",
                sound="10",
                vibration="1",
                picture=""
            )
            notification_sent = True
            print("Notification sent")

def main():
    initialize_system()
    try:
        while True:
            check_ir_input()
            handle_notifications()
            time.sleep(1)  # Adjust the sleep time as needed
    except KeyboardInterrupt:
        ir_remote.pi.stop()  # Clean up pigpio resources

if __name__ == "__main__":
    main()