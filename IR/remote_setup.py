#!/usr/bin/env python3
# Monitor, capture and decode InfraRed signal (of an IR remote controller) 
# Version:  v1.0
# Author: Nikola Jovanovic
# Date: 13.09.2020.
# Repo: https://github.com/etfovac/rpi_ir
# SW: Python 3.7.3
# HW: Pi Model 3B  V1.2, IR kit: Rx sensor module HX1838, Tx = IR remote(s)
import sys
import os
from load_ir_file import parse_ir_to_dict, find_key
import datetime
import signal
import pigpio
import infrared as infrared

IR_PIN = 17 # Board=11, BCM=17

def main():
    
    def interrupt_signal_handler(signum, frame):
        print('Interrupt signal ' + str(signum) +
                      ' on line ' + str(frame.f_lineno) +
                      ' in ' + frame.f_code.co_filename)
        pi.stop()
        sys.exit(0)

    def ir_rx_callback(ir_decoded, ir_hex, model, valid, track, log, config_folder):
        if valid:
            filepath = os.path.join(config_folder, "ir_code_" + str(model) + ".txt")
            key = input("Enter the button name for the captured IR code (or type 'skip' to skip): ")
            if key.lower() != "skip":
                if model in ir_dict:
                    btn_dict = ir_dict[model]
                else:
                    btn_dict = {}
                btn_dict[key] = {ir_decoded, ir_hex}
                ir_dict[model] = btn_dict
                os.makedirs(config_folder, exist_ok=True)  # Ensure the directory exists
                with open(filepath, "w") as f:
                    f.write(str(ir_dict[model]))
                print(f"Button '{key}' saved successfully.")
        idle()
 
    def idle():
        print("\nWaiting for IR signal... (Press Ctrl+C to exit)\n")
    
    # Setup tracking and logging
    config_folder = "./config/"
    track = True
    log = True
    ir_dict = {}
    
    # Setup IR Receiver Callback
    pi = pigpio.pi()
    ir_rec = infrared.rx(pi, IR_PIN, ir_rx_callback, track, log, config_folder) #timeout=5ms, see infrared.py
    print("IR Receiver setup complete. Ready to capture IR signals.")
    idle()
    
    # Setup Terminal interrupt signal SIGINT for Ctrl+C
    signal.signal(signal.SIGINT, interrupt_signal_handler)
    signal.pause()
    
# main END
       
if __name__ == "__main__":
    main()