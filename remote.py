import RPi.GPIO as GPIO
import time

class IRRemote:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUDDOWN)  # Set GPIO pin as input with pull-down resistor

    def read_ir_code(self):
        while True:
            if GPIO.input(self.pin) == GPIO.HIGH:
                ir_code = []
                while GPIO.input(self.pin) == GPIO.HIGH:
                    pass  # Wait for the signal to go low
                start_time = time.time()
                while len(ir_code) < 32:  # Assuming a 32-bit IR code
                    if GPIO.input(self.pin) == GPIO.HIGH:
                        ir_code.append(time.time() - start_time)
                        while GPIO.input(self.pin) == GPIO.HIGH:
                            pass  # Wait for the signal to go low again
                        start_time = time.time()
                return ir_code

def main():
    ir_remote = IRRemote(pin=17)
    print("Waiting for IR code...")
    ir_code = ir_remote.read_ir_code()
    print("Received IR code:", ir_code)

if __name__ == "__main__":
    main()