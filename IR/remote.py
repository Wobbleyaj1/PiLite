import time
import RPi.GPIO as GPIO
import pigpio
from IR.ir_helper import parse_ir_to_dict, find_key, rx

class IRRemote:
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
        self.ir_receiver = rx(self.pi, self.pin, self.ir_rx_callback, config_folder="config")
        self.last_button = None


    def load_ir_codes(self):
        with open(self.ir_code_file, 'r') as file:
            codes = parse_ir_to_dict(file.read())
        return codes

    def ir_rx_callback(self, code):
        button = find_key(self.ir_codes, code)
        if button:
            self.last_button = button
        else:
            self.last_button = None
            print("Unknown IR code received.")

    def get_last_button(self):
        print("Last button pressed: ", self.last_button)
        while True:
            time.sleep(1)  # Keep the script running to receive IR signals

def main():
    """
    Main function to create an IRRemote instance and start reading IR codes.
    """
    ir_remote = IRRemote(pin=17, ir_code_file="config/ir_code_ff.txt")
    ir_remote.get_last_button()

if __name__ == "__main__":
    main()