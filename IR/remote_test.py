import RPi.GPIO as GPIO
import time
import os
import sys
import pigpio
from load_ir_file import parse_ir_to_dict, find_key
from infrared import rx

class IRRemote:
    def __init__(self, pin, ir_code_file):
        self.pin = pin
        self.ir_code_file = ir_code_file
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO pin as input with pull-down resistor
        self.ir_codes = self.load_ir_codes()
        self.pi = pigpio.pi()
        self.ir_receiver = rx(self.pi, self.pin, self.ir_rx_callback, track=False, log=False)

    def load_ir_codes(self):
        if os.path.exists(self.ir_code_file):
            with open(self.ir_code_file, "r") as f:
                ir_model_rd = f.read()
            return parse_ir_to_dict(ir_model_rd)
        else:
            print("IR code dictionary file not found.")
            return {}

    def ir_rx_callback(self, ir_decoded, ir_hex, model, valid, track, log, config_folder):
        if valid:
            key = find_key(self.ir_codes, ir_hex)
            if key:
                print(f"Button pressed: {key}")

    def read_ir_code(self):
        print("Waiting for IR code...")
        while True:
            time.sleep(1)  # Keep the script running to receive IR signals

def main():
    ir_remote = IRRemote(pin=17, ir_code_file="config/ir_code_ff.txt")
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()