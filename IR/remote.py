import RPi.GPIO as GPIO
import time
import os
import pigpio
import sys
import multiprocessing

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from IR.ir_helper import parse_ir_to_dict, find_key, rx
from Mobile_Notifications.pushsafer import PushsaferNotification
from RGB_Strips.rgb_controller import RGBController

class IRRemote:
    """
    A class to represent an IR remote control.
    """

    def __init__(self, pin, ir_code_file, private_key, controller):
        """
        Initialize the IRRemote class.

        Args:
            pin (int): The GPIO pin number for the IR receiver.
            ir_code_file (str): The file path to the IR code dictionary.
            private_key (str): The private key for Pushsafer notifications.
            controller (RGBController): The shared RGBController instance.
        """
        self.pin = pin
        self.ir_code_file = ir_code_file
        self.controller = controller  # Use the shared RGBController instance
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO pin as input with pull-down resistor
        self.ir_codes = self.load_ir_codes()
        self.pi = pigpio.pi()
        self.ir_receiver = rx(self.pi, self.pin, self.ir_rx_callback, track=False, log=False)
        self.notifier = PushsaferNotification(private_key)  # Replace with your actual private key

    def load_ir_codes(self):
        """
        Load the IR codes from the specified file.

        Returns:
            dict: A dictionary mapping button names to their IR codes.
        """
        if not os.path.exists(self.ir_code_file):
            print("IR code dictionary file not found.")
            return {}
        
        with open(self.ir_code_file, "r") as f:
            ir_model_rd = f.read()
        return parse_ir_to_dict(ir_model_rd)

    def ir_rx_callback(self, ir_decoded, ir_hex, model, valid, track, log, config_folder):
        """
        Callback function to handle received IR signals.

        Args:
            ir_decoded (str): Decoded IR signal.
            ir_hex (str): Hexadecimal representation of the IR signal.
            model (str): IR remote model.
            log (bool): Whether to log the signal.
            config_folder (str): Path to the configuration folder.
        """
        if valid:
            key = find_key(self.ir_codes, ir_hex)
            if key:
                print(f"Button pressed: {key}")
                self.handle_ir_command(key)
            else:
                print("Unknown IR code received.")

    def handle_ir_command(self, key):
        """
        Handle the IR command based on the button key.

        Args:
            key (str): The button key corresponding to the IR command.
        """
        commands = {
            '0': self.controller.clear_strip,
            '1': lambda: self.controller.activate_static_color(),
            '2': lambda: self.controller.activate_rainbow(),
            '3': lambda: self.controller.activate_theater_chase(),
            # '4': self.command_4,
            # '5': self.command_5,
            # '6': self.command_6,
            # '7': self.command_7,
            # '8': self.command_8,
            # '9': self.command_9,
            '-': lambda: self.controller.set_max_brightness(-15),
            '+': lambda: self.controller.set_max_brightness(15),
            '<': lambda: self.controller.adjust_speed(10),
            '>': lambda: self.controller.adjust_speed(-10),
            'CH+': lambda: self.controller.cycle_next_color(),
            'CH-': lambda: self.controller.cycle_previous_color(),
            # 'CH': self.command_channel,
            # 'EQ': self.command_eq,
            '>||': lambda: self.notifier.send_notification(
                message="Play/Pause button was pressed.",
                title="IR Remote Notification",
                icon="1",
                sound="2",
                vibration="1",
                picture=""
            ),
        }

        command = commands.get(key)
        if command:
            command()
        else:
            print(f"Unknown command for key: {key}")

    def read_ir_code(self):
        """
        Print a message indicating that the system is waiting for an IR signal and keep the script running.
        """
        print("Waiting for IR code...")
        while True:
            time.sleep(1)  # Keep the script running to receive IR signals

def main():
    """
    Main function to create an IRRemote instance and start reading IR codes.
    """
    controller = RGBController()  # Create a shared RGBController instance
    ir_remote = IRRemote(pin=17, ir_code_file="config/ir_code_ff.txt", private_key="your_private_key_here", controller=controller)
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()