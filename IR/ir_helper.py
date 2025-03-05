#!/usr/bin/env python3
# Monitor, capture and decode InfraRed signal (of an IR remote controller) 
# Version:  v1.0
# Author: Nikola Jovanovic, Jesse Nipper
# Date: 13.09.2020, 03.04.2025
# Repo: https://github.com/etfovac/rpi_ir, https://github.com/Wobbleyaj1/PiLite.git
# SW: Python 3.7.3
# HW: Pi Model 3B  V1.2, IR kit: Rx sensor module HX1838, Tx = IR remote(s)

import pigpio

# IR Format Definitions
header = {'NEC': [9000, 4500], 'Yamaha': [9067, 4393]}
stop = {'NEC': 40000, 'Yamaha': 39597}
bit0 = {'NEC': [562.5, 562.5], 'Yamaha': [642, 1600]}
bit1 = {'NEC': [562.5, 1687.5], 'Yamaha': [642, 470]}
repeat = {'NEC': [9000, 2250, 562.5], 'Yamaha': [9065, 2139]}
tolerance = {'down': 0.9, 'up': 1.1, 'no': 1}
ir_remote = 'NEC'
ir_format = {
    'header': header[ir_remote],
    'bit0': bit0[ir_remote],
    'bit1': bit1[ir_remote],
    'stop': stop[ir_remote],
    'repeat': repeat[ir_remote],
    'data_len': 32
}

# Load IR File
def parse_ir_to_dict(ir_model_rd):
    """
    Parse the IR model read data into a dictionary.

    Args:
        ir_model_rd (str): The raw IR model read data.

    Returns:
        dict: A dictionary mapping button names to their IR codes.
    """
    ir_model_rd = ir_model_rd.replace("{", "")
    ir_model_rd = ir_model_rd.replace("'", "")
    ir_model_rd = ir_model_rd.replace(" ", "")
    ir_model_rd = ir_model_rd.split("},")
    ir_model_rd = [item.replace("}", "") for item in ir_model_rd]
    ir_model_rd = [item.split(":") for item in ir_model_rd]
    ir_model_rd = [[y.split(",") for y in x] for x in ir_model_rd]
    btn_dict = {}
    for item in ir_model_rd:
        if len(item) < 2 or len(item[0]) < 1 or len(item[1]) < 2:
            print(f"Skipping invalid item: {item}")
            continue
        try:
            btn_dict[item[0][0]] = {item[1][0], item[1][1]}
        except IndexError as e:
            print(f"Error processing item: {item}")
            print(f"Exception: {e}")
    return btn_dict

def find_key(btn_dict, value):
    """
    Find the key in the dictionary that corresponds to the given value.

    Args:
        btn_dict (dict): The dictionary mapping button names to IR codes.
        value (str): The IR code to find.

    Returns:
        str: The button name corresponding to the given IR code, or None if not found.
    """
    index = 0
    for x in btn_dict.values():
        for y in x:
            if y == value:
                return list(btn_dict.keys())[index]
        index += 1

# Infrared Receiver Class
class rx:
    def __init__(self, pi, gpio, external_callback, track, log, config_folder="../config", timeout=5):
        """
        Initialize the IR receiver.

        Args:
            pi (pigpio.pi): The pigpio instance.
            gpio (int): The GPIO pin number.
            external_callback (function): The callback function to handle received IR signals.
            track (bool): Whether to track the signal.
            log (bool): Whether to log the signal.
            config_folder (str): Path to the configuration folder.
            timeout (int): The watchdog timeout in milliseconds.
        """
        self.pi = pi
        self.gpio = gpio
        self.watchdog_timeout = timeout
        self.callback = external_callback
        self.track = track
        self.log = log
        self.config_folder = config_folder
        self.edges = 0
        self.rec_started = False
        pi.set_pull_up_down(gpio, pigpio.PUD_OFF)
        pi.set_mode(gpio, pigpio.INPUT)
        self.cb = pi.callback(gpio, pigpio.EITHER_EDGE, self.rx_callback)
        self.d1a = []
        self.d2a = []
        self.threshold01 = sum(ir_format['bit1']) * tolerance['down']
        self.valid_code = False
        self.ir_hex = 0

    def rx_callback(self, gpio, level, tick):
        """
        Callback function to handle GPIO edge events.

        Args:
            gpio (int): The GPIO pin number.
            level (int): The GPIO level (0 or 1).
            tick (int): The time of the event in microseconds.
        """
        if level != pigpio.TIMEOUT:
            if not self.rec_started:
                self.rec_started = True
                self.pi.set_watchdog(self.gpio, self.watchdog_timeout)
                self.ir_decoded = ""
                self.edges = 1
                self.d1a = []
                self.d2a = []
                self.t1 = None
                self.t2 = None
                self.t3 = tick
            else:
                self.edges += 1
                self.t1 = self.t2
                self.t2 = self.t3
                self.t3 = tick
                if self.edges == 2:
                    if pigpio.tickDiff(self.t2, self.t3) > ir_format['header'][1] * tolerance['down']:
                        self.edges -= 1
                if self.edges % 2 == 1 and self.edges > 1:
                    d1 = pigpio.tickDiff(self.t1, self.t2)
                    d2 = pigpio.tickDiff(self.t2, self.t3)
                    val = "1" if (d1 + d2) > self.threshold01 else "0"
                    self.d1a.append({d2, d1})
                    self.d2a.append(int(val))
                    self.ir_decoded += val
        else:
            if self.rec_started:
                self.rec_started = False
                self.pi.set_watchdog(self.gpio, 0)
            if self.edges > 2 * ir_format['data_len']:
                self.ir_hex = hex(int(self.ir_decoded, 2))
                self.valid_code = self.validity_check()
                self.callback(self.ir_decoded, self.ir_hex, self.ir_hex[2:4], self.valid_code, self.track, self.log, self.config_folder)

    def validity_check(self):
        """
        Check the validity of the received IR code.

        Returns:
            bool: True if the IR code is valid, False otherwise.
        """
        cond1 = len(self.ir_decoded) == ir_format['data_len']
        hex_head = self.ir_hex[0:2]
        cond2 = int(hex_head + self.ir_hex[4], 16) + int(hex_head + self.ir_hex[6], 16) == 15
        cond3 = int(hex_head + self.ir_hex[5], 16) + int(hex_head + self.ir_hex[7], 16) == 15
        valid = cond1 and cond2 and cond3
        return valid