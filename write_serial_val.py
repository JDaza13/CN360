#!/usr/bin/env python3
import serial
import re

import time

if __name__ == '__main__':
    light_control_state = 'off'
    serial_com = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    serial_com.flush()
    while True:
        if light_control_state == 'on':
            light_control_state = 'off'
        if light_control_state == 'off':
            light_control_state = 'on'
        #light control
        serial_com.write((light_control_state + '\n').encode());
        time.sleep(5)