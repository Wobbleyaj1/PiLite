#!/usr/bin/env python3
from RGB_Strips.rgb_controller import RGBController
import time
import signal
import sys
from startup import create_and_activate_venv, start_pigpiod, load_environment_variables, cleanup

# Create and activate virtual environment
venv_path = "/home/pi/PiLite/venv"
create_and_activate_venv(venv_path)

# Create an instance of RGBController
controller = RGBController()

# Run the demo
if __name__ == '__main__':
    try:
        controller.run_menu()
    except KeyboardInterrupt:
        controller.clear_strip()