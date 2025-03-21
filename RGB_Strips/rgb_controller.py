from rpi_ws281x import PixelStrip, Color
import time
import threading

class RGBController:
    def __init__(self, led_count=60, led_pin=18, led_freq_hz=800000, led_dma=10, led_brightness=255, led_invert=False, led_channel=0):
        self.strip = PixelStrip(led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness, led_channel)
        self.strip.begin()
        self.current_pattern = None
        self.max_brightness = led_brightness
        self.brightness = led_brightness
        self.speed = 50
        self.current_color_index = 0
        self.pattern_thread = None
        self.last_change_time = time.time()  # Track the last change time
        self.activate_static_color()

    def update_last_change_time(self):
        """Update the last change time to the current time."""
        self.last_change_time = time.time()

    def stop_current_pattern(self):
        """
        Stop the currently running pattern by resetting the current_pattern
        and waiting for the thread to exit.
        """
        self.current_pattern = None
        if self.pattern_thread and self.pattern_thread.is_alive():
            self.pattern_thread.join()
        self.pattern_thread = None

    def clear_strip(self):
        self.last_change_time = None
        self.stop_current_pattern()
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()
        print("LEDs cleared.")

    def set_max_brightness(self, delta):
        self.max_brightness = max(0, min(255, self.max_brightness + delta))
        self.strip.setBrightness(self.max_brightness)
        self.strip.show()
        self.update_last_change_time()  # Update last change time

    def adjust_brightness(self, delta):
        self.brightness = max(0, min(self.max_brightness, self.brightness + delta))
        self.strip.setBrightness(self.brightness)
        self.strip.show()
        if self.brightness == 0:
            self.last_change_time = None 
        else:
            self.update_last_change_time()  # Update last change time

    def adjust_speed(self, delta):
        self.speed = max(1, self.speed + delta)
        self.update_last_change_time()  # Update last change time

    def activate_static_color(self):
        self.clear_strip()
        self.current_pattern = "static_color"
        colors, color_names = self.get_color_options()
        self.color_wipe(colors[self.current_color_index])
        self.update_last_change_time()  # Update last change time
        print(f"Static Color activated: {color_names[self.current_color_index]}.")

    def activate_rainbow(self):
        self.clear_strip()
        self.current_pattern = "rainbow"
        threading.Thread(target=self.rainbow, daemon=True).start()
        self.update_last_change_time()  # Update last change time
        print("Rainbow pattern activated.")

    def activate_theater_chase(self):
        self.clear_strip()
        self.current_pattern = "theater_chase"
        colors, color_names = self.get_color_options()
        threading.Thread(
            target=self.theater_chase, args=(colors[self.current_color_index],), daemon=True
        ).start()
        self.update_last_change_time()  # Update last change time
        print(f"Theater Chase pattern activated with color: {color_names[self.current_color_index]}.")

    def cycle_next_color(self):
        colors, color_names = self.get_color_options()
        self.current_color_index = (self.current_color_index + 1) % len(colors)
        self.color_wipe(colors[self.current_color_index])
        self.update_last_change_time()  # Update last change time
        print(f"Color changed to {color_names[self.current_color_index]}.")

    def cycle_previous_color(self):
        colors, color_names = self.get_color_options()
        self.current_color_index = (self.current_color_index - 1) % len(colors)
        self.color_wipe(colors[self.current_color_index])
        self.update_last_change_time()  # Update last change time
        print(f"Color changed to {color_names[self.current_color_index]}.")

    def color_wipe(self, color):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def rainbow(self):
        while self.current_pattern == "rainbow":
            for j in range(256):
                if self.current_pattern != "rainbow":  # Check if the pattern has changed
                    break
                for i in range(self.strip.numPixels()):
                    if self.current_pattern != "rainbow":  # Check again inside the inner loop
                        break
                    self.strip.setPixelColor(i, self.wheel((i + j) & 255))
                self.strip.show()
                time.sleep(self.speed / 1000.0)
            if self.current_pattern != "rainbow":  # Exit the outer loop if the pattern changes
                break

    def theater_chase(self, color):
        while self.current_pattern == "theater_chase":
            for q in range(3):
                if self.current_pattern != "theater_chase":  # Check if the pattern has changed
                    break
                for i in range(0, self.strip.numPixels(), 3):
                    if self.current_pattern != "theater_chase":  # Check again inside the inner loop
                        break
                    self.strip.setPixelColor(i + q, color)
                self.strip.show()
                time.sleep(self.speed / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    if self.current_pattern != "theater_chase":  # Check again inside the cleanup loop
                        break
                    self.strip.setPixelColor(i + q, 0)
            if self.current_pattern != "theater_chase":  # Exit the outer loop if the pattern changes
                break

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
            Color(255, 255, 255),  # White
            Color(255, 0, 0),  # Red
            Color(0, 255, 0),  # Green
            Color(0, 0, 255),  # Blue
            Color(255, 255, 0),  # Yellow
            Color(0, 255, 255),  # Cyan
            Color(255, 0, 255),  # Magenta
        ]
        color_names = ["White", "Red", "Green", "Blue", "Yellow", "Cyan", "Magenta"]
        return colors, color_names