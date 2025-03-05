import RPi.GPIO as GPIO
import time
import os
import pigpio
from IR.ir_helper import parse_ir_to_dict, find_key, rx

class IRRemote:
    """
    A class to represent an IR remote control.

    Attributes:
        pin (int): The GPIO pin number for the IR receiver.
        ir_code_file (str): The file path to the IR code dictionary.
        ir_codes (dict): The dictionary of IR codes.
        pi (pigpio.pi): The pigpio instance.
        ir_receiver (rx): The IR receiver instance.
    """

    def __init__(self, pin, ir_code_file):
        """
        Initialize the IRRemote class.

        Args:
            pin (int): The GPIO pin number for the IR receiver.
            ir_code_file (str): The file path to the IR code dictionary.
        """
        self.pin = pin
        self.ir_code_file = ir_code_file
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO pin as input with pull-down resistor
        self.ir_codes = self.load_ir_codes()
        self.pi = pigpio.pi()
        self.ir_receiver = rx(self.pi, self.pin, self.ir_rx_callback, track=False, log=False)

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
            valid (bool): Whether the IR signal is valid.
            track (bool): Whether to track the signal.
            log (bool): Whether to log the signal.
            config_folder (str): Path to the configuration folder.
        """
        if valid:
            key = find_key(self.ir_codes, ir_hex)
            if key:
                print(f"Button pressed: {key}")

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
    ir_remote = IRRemote(pin=17, ir_code_file="config/ir_code_ff.txt")
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()