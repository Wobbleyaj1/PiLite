#!/usr/bin/env python3
import time
from rpi_ws281x import PixelStrip, Color
import argparse
import threading


class RGBController:
    def __init__(self, led_count=60, led_pin=18, led_freq_hz=800000, led_dma=10, led_brightness=255, led_invert=False, led_channel=0):
        """Initialize the RGBController with LED strip configuration."""
        self.led_count = led_count
        self.led_pin = led_pin
        self.led_freq_hz = led_freq_hz
        self.led_dma = led_dma
        self.led_brightness = led_brightness
        self.led_invert = led_invert
        self.led_channel = led_channel

        # Create NeoPixel object with appropriate configuration.
        self.strip = PixelStrip(self.led_count, self.led_pin, self.led_freq_hz, self.led_dma, self.led_invert, self.led_brightness, self.led_channel)
        self.strip.begin()  # Initialize the library (must be called once before other functions).

        # State variables
        self.is_on = True
        self.current_pattern = None
        self.speed = 50  # Default speed in ms
        self.brightness = self.led_brightness

    def toggle_power(self):
        """Toggle the power state of the LED strip."""
        self.is_on = not self.is_on
        if self.is_on:
            print("LEDs turned ON.")
        else:
            print("LEDs turned OFF.")
            self.clear_strip()

    def set_brightness(self, brightness):
        """Set the brightness of the strip."""
        self.brightness = max(0, min(255, brightness))  # Clamp brightness between 0 and 255
        self.strip.setBrightness(self.brightness)
        self.strip.show()
        print(f"Brightness set to {self.brightness}.")

    def color_wipe(self, color):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def rainbow(self, wait_ms=20):
        """Draw rainbow that fades across all pixels at once."""
        while self.current_pattern == "rainbow" and self.is_on:
            for j in range(256):  # One full cycle of the rainbow
                if self.current_pattern != "rainbow" or not self.is_on:
                    return  # Exit if the pattern is changed or LEDs are turned off
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, self.wheel((i + j) & 255))
                self.strip.show()
                time.sleep(self.speed / 1000.0)  # Dynamically use the updated self.speed

    def theater_chase(self, color):
        """Movie theater light style chaser animation."""
        while self.current_pattern == "theater_chase" and self.is_on:
            for q in range(3):  # Three phases of the chase
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, color)  # Light up every third LED
                self.strip.show()
                time.sleep(self.speed / 1000.0)  # Dynamically use the updated self.speed
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)  # Turn off the LEDs in this phase

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def clear_strip(self):
        """Turn off all LEDs."""
        self.color_wipe(Color(0, 0, 0))
        print("LEDs cleared.")

    def get_color_options(self):
        """Return a list of color options and their names."""
        colors = [
            Color(255, 0, 0),  # Red
            Color(0, 255, 0),  # Green
            Color(0, 0, 255),  # Blue
            Color(255, 255, 0),  # Yellow
            Color(0, 255, 255),  # Cyan
            Color(255, 0, 255),  # Magenta
            Color(255, 255, 255),  # White
            Color(128, 128, 128),  # Gray
            Color(255, 165, 0),  # Orange
            Color(75, 0, 130),  # Indigo
        ]
        color_names = ["Red", "Green", "Blue", "Yellow", "Cyan", "Magenta", "White", "Gray", "Orange", "Indigo"]
        return colors, color_names

    def run_menu(self):
        """Menu-driven control for the RGB strip with pattern-specific options."""
        while True:
            print("\nMain Menu:")
            print("1. Static Color")
            print("2. Rainbow")
            print("3. Theater Chase")
            print("0. Exit")
            pattern_choice = input("Select a pattern: ")

            if pattern_choice == "1":
                if self.is_on:
                    self.current_pattern = "static_color"
                    self.color_wipe(Color(255, 0, 0))  # Default to red
                    print("Static Color activated.")
                    self.static_color_menu()
                else:
                    print("Turn on the LEDs first.")
            elif pattern_choice == "2":
                if self.is_on:
                    self.current_pattern = "rainbow"
                    print("Rainbow  activated.")
                    self.rainbow_menu()
                else:
                    print("Turn on the LEDs first.")
            elif pattern_choice == "3":
                if self.is_on:
                    self.current_pattern = "theater_chase"
                    print("Theater Chase activated.")
                    self.theater_chase_menu()
                else:
                    print("Turn on the LEDs first.")
            elif pattern_choice == "0":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def static_color_menu(self):
        """Menu for Static Color options."""
        colors, color_names = self.get_color_options()
        current_color_index = 0

        while self.current_pattern == "static_color":
            print("\nStatic Color Menu:")
            print("\nStatic Color Menu:")
            print("1. Cycle to Next Color")
            print("2. Adjust Brightness")
            print("0. Back to Main Menu")
            choice = input("Enter your choice: ")

            if choice == "1":
                # Cycle to the next color
                current_color_index = (current_color_index + 1) % len(colors)
                self.color_wipe(colors[current_color_index])
                print(f"Color changed to {color_names[current_color_index]}.")
            elif choice == "2":
                new_brightness = int(input("Enter new brightness (0-255): "))
                self.set_brightness(new_brightness)
            elif choice == "0":
                self.clear_strip()  # Clear LEDs when returning to the main menu
                self.current_pattern = None
            else:
                print("Invalid choice. Please try again.")

    def rainbow_menu(self):
        """Menu for Rainbow options."""
        # Set a default speed if not already set
        if not hasattr(self, 'speed') or self.speed is None:
            self.speed = 50  # Default speed in ms

        # Start the rainbow animation in a separate thread
        rainbow_thread = threading.Thread(target=self.rainbow, args=(self.speed,))
        rainbow_thread.daemon = True  # Ensure the thread exits when the main program exits
        rainbow_thread.start()

        while self.current_pattern == "rainbow":
            print("\nRainbow Menu:")
            print("1. Adjust Speed")
            print("2. Adjust Brightness")
            print("0. Back to Main Menu")
            choice = input("Enter your choice: ")

            if choice == "1":
                new_speed = int(input("Enter new speed in ms (e.g., 10 for faster, 100 for slower): "))
                self.speed = max(1, new_speed)
                print(f"Speed set to {self.speed} ms.")
            elif choice == "2":
                new_brightness = int(input("Enter new brightness (0-255): "))
                self.set_brightness(new_brightness)
            elif choice == "0":
                self.clear_strip()  # Clear LEDs when returning to the main menu
                self.current_pattern = None
            else:
                print("Invalid choice. Please try again.")

    def theater_chase_menu(self):
        """Menu for Theater Chase options."""
        # Expanded color options
        colors, color_names = self.get_color_options()
        current_color_index = 0

        # Start the theater chase animation in a separate thread
        theater_chase_thread = threading.Thread(target=self.theater_chase, args=(colors[current_color_index],))
        theater_chase_thread.daemon = True  # Ensure the thread exits when the main program exits
        theater_chase_thread.start()

        while self.current_pattern == "theater_chase":
            print("\nTheater Chase Menu:")
            print("1. Cycle to Next Color")
            print("2. Adjust Speed")
            print("3. Adjust Brightness")
            print("0. Back to Main Menu")
            choice = input("Enter your choice: ")

            if choice == "1":
                # Cycle to the next color
                current_color_index = (current_color_index + 1) % len(colors)
                self.current_pattern = None  # Stop the current thread
                self.clear_strip()
                theater_chase_thread.join()  # Wait for the thread to finish
                theater_chase_thread = threading.Thread(target=self.theater_chase, args=(colors[current_color_index],))
                theater_chase_thread.daemon = True
                theater_chase_thread.start()
                print(f"Color changed to {color_names[current_color_index]}.")
            elif choice == "2":
                new_speed = int(input("Enter new speed in ms (e.g., 10 for faster, 100 for slower): "))
                self.speed = max(1, new_speed)
                print(f"Speed set to {self.speed} ms.")
            elif choice == "3":
                new_brightness = int(input("Enter new brightness (0-255): "))
                self.set_brightness(new_brightness)
            elif choice == "0":
                self.clear_strip()  # Clear LEDs when returning to the main menu
                self.current_pattern = None
                theater_chase_thread.join()  # Wait for the thread to finish
            else:
                print("Invalid choice. Please try again.")

# Main program logic
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create an instance of RGBController
    controller = RGBController()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        controller.run_menu()
    except KeyboardInterrupt:
        if args.clear:
            controller.clear_strip()