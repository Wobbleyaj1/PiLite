# PiLite

## Software Flow Algorithm

### 1. System Initialization
- Start the Raspberry Pi system.
- Initialize GPIO pins for the ultrasonic sensor, IR receiver, and LED strip.
- Establish communication with the notification module (e.g., Bluetooth, WiFi, or SMS API).
- Set default values for LED brightness and notification thresholds.

### 2. Input Handling

#### IR Remote Input:
- Check for signals from the IR receiver.
- If a brightness or color command is received, update the LED strip settings.

#### Ultrasonic Sensor Input:
- Continuously measure the distance to the trunk door.
- If the distance is within a predefined "trunk closed" threshold, turn off the LEDs.
- If the distance is above the threshold, adjust brightness accordingly.

### 3. LED Control Logic
- If IR remote command is received:
  - Set manual brightness and color (override ultrasonic input).
- Else, use the ultrasonic sensor to dynamically adjust brightness.

### 4. Notification Logic
- If the trunk remains open for more than 3 minutes, trigger a mobile alert.
- Ensure that duplicate notifications are not sent repeatedly.