#!/usr/bin/env python3
import time
from rpi_ws281x import PixelStrip, Color
import argparse

# LED strip configuration:
LED_COUNT = 60       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800kHz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # Set to '1' for GPIOs 13, 19, 41, 45, or 53


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def clearStrip(strip):
    """Turn off all LEDs."""
    colorWipe(strip, Color(0, 0, 0), 10)


# Menu-driven control
def main_menu(strip):
    while True:
        print("\nSelect an animation:")
        print("1. Color Wipe")
        print("2. Theater Chase")
        print("3. Rainbow")
        print("4. Rainbow Cycle")
        print("5. Theater Chase Rainbow")
        print("6. Clear LEDs")
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            r = int(input("Enter red value (0-255): "))
            g = int(input("Enter green value (0-255): "))
            b = int(input("Enter blue value (0-255): "))
            wait_ms = int(input("Enter delay in ms (e.g., 50): "))
            colorWipe(strip, Color(r, g, b), wait_ms)
        elif choice == "2":
            r = int(input("Enter red value (0-255): "))
            g = int(input("Enter green value (0-255): "))
            b = int(input("Enter blue value (0-255): "))
            wait_ms = int(input("Enter delay in ms (e.g., 50): "))
            iterations = int(input("Enter number of iterations (e.g., 10): "))
            theaterChase(strip, Color(r, g, b), wait_ms, iterations)
        elif choice == "3":
            wait_ms = int(input("Enter delay in ms (e.g., 20): "))
            iterations = int(input("Enter number of iterations (e.g., 1): "))
            rainbow(strip, wait_ms, iterations)
        elif choice == "4":
            wait_ms = int(input("Enter delay in ms (e.g., 20): "))
            iterations = int(input("Enter number of iterations (e.g., 5): "))
            rainbowCycle(strip, wait_ms, iterations)
        elif choice == "5":
            wait_ms = int(input("Enter delay in ms (e.g., 50): "))
            theaterChaseRainbow(strip, wait_ms)
        elif choice == "6":
            clearStrip(strip)
        elif choice == "0":
            print("Exiting...")
            clearStrip(strip)
            break
        else:
            print("Invalid choice. Please try again.")


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Initialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        main_menu(strip)
    except KeyboardInterrupt:
        if args.clear:
            clearStrip(strip)