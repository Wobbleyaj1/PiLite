import RPi.GPIO as GPIO
import time
import os
import pigpio
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from IR.ir_helper import parse_ir_to_dict, find_key, rx
from RGB_Strips.rgb_controller import RGBController
from Mobile_Notifications.pushsafer import PushsaferNotification

class IRRemote:
    """
    A class to represent an IR remote control.

    Attributes:
        pin (int): The GPIO pin number for the IR receiver.
        ir_code_file (str): The file path to the IR code dictionary.
        ir_codes (dict): The dictionary of IR codes.
        pi (pigpio.pi): The pigpio instance.
        ir_receiver (rx): The IR receiver instance.
    """

    def __init__(self, pin, ir_code_file, private_key):
        """
        Initialize the IRRemote class.

        Args:
            pin (int): The GPIO pin number for the IR receiver.
            ir_code_file (str): The file path to the IR code dictionary.
        """
        self.pin = pin
        self.ir_code_file = ir_code_file
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO pin as input with pull-down resistor
        self.ir_codes = self.load_ir_codes()
        self.pi = pigpio.pi()
        self.ir_receiver = rx(self.pi, self.pin, self.ir_rx_callback, track=False, log=False)
        self.notifier = PushsaferNotification(private_key)  # Replace with your actual private key

    def load_ir_codes(self):
        """
        Load the IR codes from the specified file.

        Returns:
            dict: A dictionary mapping button names to their IR codes.
        """
        if not os.path.exists(self.ir_code_file):
            print("IR code dictionary file not found.")
            return {}
        
        with open(self.ir_code_file, "r") as f:
            ir_model_rd = f.read()
        return parse_ir_to_dict(ir_model_rd)

    def ir_rx_callback(self, ir_decoded, ir_hex, model, valid, track, log, config_folder):
        """
        Callback function to handle received IR signals.

        Args:
            ir_decoded (str): Decoded IR signal.
            ir_hex (str): Hexadecimal representation of the IR signal.
            model (str): IR remote model.
            log (bool): Whether to log the signal.
            config_folder (str): Path to the configuration folder.S
        """
        if valid:
            key = find_key(self.ir_codes, ir_hex)
            if key:
                print(f"Button pressed: {key}")
                self.handle_ir_command(key)
            else:
                print("Unknown IR code received.")

    def handle_ir_command(self, key):
        """
        Handle the IR command based on the button key.

        Args:
            key (str): The button key corresponding to the IR command.
        """
        commands = {
            '0': self.command_0,
            '1': self.command_1,
            '2': self.command_2,
            '3': self.command_3,
            '4': self.command_4,
            '5': self.command_5,
            '6': self.command_6,
            '7': self.command_7,
            '8': self.command_8,
            '9': self.command_9,
            '-': self.command_minus,
            '+': self.command_plus,
            'EQ': self.command_eq,
            '<': self.command_left,
            '>': self.command_right,
            '>||': self.command_play_pause,
            'CH+': self.command_channel_up,
            'CH': self.command_channel,
            'CH-': self.command_channel_down
        }

        command = commands.get(key)
        if command:
            command()
        else:
            print(f"Unknown command for key: {key}")
    
    def command_0(self):
        pass

    def command_1(self):
        print("Command 1 executed")

    def command_2(self):
        print("Command 2 executed")

    def command_3(self):
        print("Command 3 executed")

    def command_4(self):
        print("Command 4 executed")

    def command_5(self):
        print("Command 5 executed")

    def command_6(self):
        print("Command 6 executed")

    def command_7(self):
        print("Command 7 executed")

    def command_8(self):
        print("Command 8 executed")

    def command_9(self):
        print("Command 9 executed")

    def command_minus(self):
        """
        Command -: Decrease brightness.
        """
        print("Command -: Decreasing brightness...")
        new_brightness = max(self.controller.brightness - 25, 0)
        self.controller.set_brightness(new_brightness)

    def command_plus(self):
        """
        Command +: Increase brightness.
        """
        print("Command +: Increasing brightness...")
        new_brightness = min(self.controller.brightness + 25, 255)
        self.controller.set_brightness(new_brightness)

    def command_eq(self):
        print("Command EQ executed")

    def command_left(self):
        """
        Command <: Decrease speed.
        """
        print("Command <: Decreasing speed...")
        self.controller.speed = self.controller.speed + 10
        print(f"Speed set to {self.controller.speed} ms.")

    def command_right(self):
        """
        Command >: Increase speed.
        """
        print("Command >: Increasing speed...")
        self.controller.speed = max(1, self.controller.speed - 10)
        print(f"Speed set to {self.controller.speed} ms.")


    def command_play_pause(self):
        self.notifier.send_notification(
            message="You Left Your Lights On",  # The message text
            title="PiLite",                     # The title of the message
            icon="24",                          # The icon number
            sound="10",                         # The sound number
            vibration="1",                      # The vibration number
            picture=""                          # The picture data URL (optional)
        )
        print("Command 0 executed and notification sent")

    def command_channel_up(self):
        """
        Command CH+: Cycle clockwise through the colors.
        """
        print("Command CH+: Cycling clockwise through colors...")
        colors, color_names = self.controller.get_color_options()
        self.controller.current_color_index = (self.controller.current_color_index + 1) % len(colors)
        self.controller.color_wipe(colors[self.controller.current_color_index])
        print(f"Color changed to {color_names[self.controller.current_color_index]}.")


    def command_channel(self):
        """
        Command CH: Cycle through patterns.
        """
        print("Command CH: Cycling through patterns...")
        patterns = ["static_color", "rainbow", "theater_chase"]
        current_index = patterns.index(self.controller.current_pattern) if self.controller.current_pattern in patterns else -1
        next_index = (current_index + 1) % len(patterns)
        self.controller.current_pattern = patterns[next_index]

        if self.controller.current_pattern == "static_color":
            print("Switching to Static Color...")
            self.controller.color_wipe(Color(255, 0, 0))  # Default to red
        elif self.controller.current_pattern == "rainbow":
            print("Switching to Rainbow...")
            threading.Thread(target=self.controller.rainbow, daemon=True).start()
        elif self.controller.current_pattern == "theater_chase":
            print("Switching to Theater Chase...")
            threading.Thread(target=self.controller.theater_chase, args=(Color(255, 255, 0),), daemon=True).start()


    def command_channel_down(self):
        """
        Command CH-: Cycle counterclockwise through the colors.
        """
        print("Command CH-: Cycling counterclockwise through colors...")
        colors, color_names = self.controller.get_color_options()
        self.controller.current_color_index = (self.controller.current_color_index - 1) % len(colors)
        self.controller.color_wipe(colors[self.controller.current_color_index])
        print(f"Color changed to {color_names[self.controller.current_color_index]}.")


    def read_ir_code(self):
        """
        Print a message indicating that the system is waiting for an IR signal and keep the script running.
        """
        print("Waiting for IR code...")
        while True:
            time.sleep(1)  # Keep the script running to receive IR signals

def main():
    """
    Main function to create an IRRemote instance and start reading IR codes.
    """
    ir_remote = IRRemote(pin=17, ir_code_file="config/ir_code_ff.txt")
    ir_remote.read_ir_code()

if __name__ == "__main__":
    main()