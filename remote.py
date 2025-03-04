import RPi.GPIO as GPIO
import time
import lirc

# Initialize the GPIO and lirc
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)  # Replace 17 with the GPIO pin you are using

sockid = lirc.init("myremote", blocking=False)

try:
    while True:
        code = lirc.nextcode()
        if code:
            print(f"Received code: {code}")
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    lirc.deinit()
    GPIO.cleanup()