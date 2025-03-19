#!/usr/bin/env python3
from RGB_Strips.rgb_controller import RGBController
import time

# Create an instance of RGBController
controller = RGBController()

# Run the demo
if __name__ == '__main__':
    try:
        controller.run_menu()
    except KeyboardInterrupt:
        controller.clear_strip()