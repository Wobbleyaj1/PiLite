import RPi.GPIO as GPIO
import time

class HCSR04:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        
        GPIO.output(self.trigger_pin, GPIO.LOW)
        time.sleep(2)
    
    def get_distance(self):
        # Send a 10us pulse to trigger the sensor
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, GPIO.LOW)
        
        # Wait for the echo to start
        while GPIO.input(self.echo_pin) == 0:
            pulse_start = time.time()
        
        # Wait for the echo to end
        while GPIO.input(self.echo_pin) == 1:
            pulse_end = time.time()
        
        # Calculate the duration of the pulse
        pulse_duration = pulse_end - pulse_start
        
        # Calculate the distance (speed of sound is 34300 cm/s)
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        
        return distance
    
    def cleanup(self):
        GPIO.cleanup()

# Example usage:
if __name__ == "__main__":
    sensor = HCSR04(trigger_pin=23, echo_pin=24)
    try:
        while True:
            distance = sensor.get_distance()
            print(f"Distance: {distance} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")
        sensor.cleanup()