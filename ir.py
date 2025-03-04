import pigpio
import time
from ir_rx import nec

class IRRemote:
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin
        self.pi = pigpio.pi()
        self.decoder = nec.Decoder(self.pi, self.gpio_pin, self.callback)

    def callback(self, code, repeat):
        if code != -1:
            print(f"Received IR code: {hex(code)}")

    def start(self):
        print("Starting IR remote decoder...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping IR remote decoder...")
        finally:
            self.decoder.cancel()
            self.pi.stop()

if __name__ == "__main__":
    ir_remote = IRRemote(gpio_pin=17)
    ir_remote.start()