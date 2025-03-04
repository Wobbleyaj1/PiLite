import RPi.GPIO as GPIO
import time
import lirc

# Initialize the GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)  # Replace 17 with the GPIO pin you are using

# Initialize lirc
lirc_client = lirc.Lirc("myremote", blocking=False)

try:
    while True:
        code = lirc_client.nextcode()
        if code:
            print(f"Received code: {code}")
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    lirc_client.deinit()
    GPIO.cleanup()