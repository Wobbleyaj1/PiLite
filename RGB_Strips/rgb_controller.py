from rpi_ws281x import PixelStrip, Color
import time
import threading

class RGBController:
    def __init__(self, led_count=60, led_pin=18, led_freq_hz=800000, led_dma=10, led_brightness=255, led_invert=False, led_channel=0):
        self.strip = PixelStrip(led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness, led_channel)
        self.strip.begin()
        self.current_pattern = None
        self.brightness = led_brightness
        self.speed = 50
        self.current_color_index = 0
        self.pattern_thread = None

    def clear_strip(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()
        print("LEDs cleared.")

    def adjust_brightness(self, delta):
        self.brightness = max(0, min(255, self.brightness + delta))
        self.strip.setBrightness(self.brightness)
        self.strip.show()
        print(f"Brightness adjusted to {self.brightness}.")

    def adjust_speed(self, delta):
        self.speed = max(1, self.speed + delta)
        print(f"Speed adjusted to {self.speed} ms.")

    def stop_current_pattern(self):
        """
        Stop the currently running pattern by resetting the current_pattern
        and waiting for the thread to exit.
        """
        self.current_pattern = None
        if self.pattern_thread and self.pattern_thread.is_alive():
            self.pattern_thread.join()
        self.pattern_thread = None

    def activate_static_color(self):
        self.stop_current_pattern()
        self.current_pattern = "static_color"
        self.color_wipe(Color(255, 255, 255))
        print("Static Color activated.")

    def activate_rainbow(self):
        self.stop_current_pattern()
        self.current_pattern = "rainbow"
        threading.Thread(target=self.rainbow, daemon=True).start()
        print("Rainbow pattern activated.")

    def activate_theater_chase(self):
        self.stop_current_pattern()
        self.current_pattern = "theater_chase"
        threading.Thread(target=self.theater_chase, args=(Color(255, 255, 0),), daemon=True).start()
        print("Theater Chase pattern activated.")

    def cycle_next_color(self):
        colors, color_names = self.get_color_options()
        self.current_color_index = (self.current_color_index + 1) % len(colors)
        self.color_wipe(colors[self.current_color_index])
        print(f"Color changed to {color_names[self.current_color_index]}.")

    def cycle_previous_color(self):
        colors, color_names = self.get_color_options()
        self.current_color_index = (self.current_color_index - 1) % len(colors)
        self.color_wipe(colors[self.current_color_index])
        print(f"Color changed to {color_names[self.current_color_index]}.")

    def color_wipe(self, color):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def rainbow(self):
        while self.current_pattern == "rainbow":
            for j in range(256):
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, self.wheel((i + j) & 255))
                self.strip.show()
                time.sleep(self.speed / 1000.0)

    def theater_chase(self, color):
        while self.current_pattern == "theater_chase":
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, color)
                self.strip.show()
                time.sleep(self.speed / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

    def wheel(self, pos):
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def get_color_options(self):
        colors = [
            Color(255, 0, 0),  # Red
            Color(0, 255, 0),  # Green
            Color(0, 0, 255),  # Blue
            Color(255, 255, 0),  # Yellow
            Color(0, 255, 255),  # Cyan
            Color(255, 0, 255),  # Magenta
            Color(255, 255, 255),  # White
        ]
        color_names = ["Red", "Green", "Blue", "Yellow", "Cyan", "Magenta", "White"]
        return colors, color_names