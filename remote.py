import serial
import time

class HX1838Remote:
    def __init__(self, port="/dev/ttyAMA0", baudrate=2400):
        self.ser = serial.Serial(port, baudrate)
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def _read_signal(self):
        while True:
            data = self.ser.read(1)
            if self.callback:
                self.callback(ord(data))

    def start(self):
        try:
            self._read_signal()
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        self.ser.close()

# Example usage
if __name__ == "__main__":
    def print_signal(signal):
        print(f"Received signal: {signal}")

    remote = HX1838Remote()
    remote.set_callback(print_signal)
    remote.start()