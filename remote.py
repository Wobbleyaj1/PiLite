import RPi.GPIO as GPIO
import time
import os
import sys
sys.path.append(os.path.abspath("rpi_ir/config"))
from load_ir_file import parse_ir_to_dict, find_key

class IRRemote:
    def __init__(self, pin, ir_code_file):
        self.pin = pin
        self.ir_code_file = ir_code_file
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO pin as input with pull-down resistor
        self.ir_codes = self.load_ir_codes()

    def load_ir_codes(self):
        if os.path.exists(self.ir_code_file):
            with open(self.ir_code_file, "r") as f:
                ir_model_rd = f.read()
            return parse_ir_to_dict(ir_model_rd)
        else:
            print("IR code dictionary file not found.")
            return {}

    def read_ir_code(self):
        while True:
            ir_code = self.get_ir_code_from_gpio()
            if ir_code:
                key = find_key(self.ir_codes, ir_code)
                if key:
                    print(f"Button pressed: {key}")

    def get_ir_code_from_gpio(self):
        # Placeholder function to simulate reading an IR code from GPIO
        # Replace this with actual implementation to read and decode the IR signal
        time.sleep(1)  # Simulate waiting for an IR signal
        return "0xfd00ff"  # Simulate a received IR code

def main():
    ir_remote = IRRemote(pin=17, ir_code_file="rpi_ir/config/ir_code_ff.txt")
    print("Waiting for IR code...")
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()