#!/usr/bin/env python3
import serial
import re

if __name__ == '__main__':
    serial_com = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    serial_com.flush()
    while True:
        if serial_com.in_waiting > 0:
            line = serial_com.readline().rstrip()
            line_value = re.findall('\d+', str(line))
            if line_value and len(line_value) > 0:
            	print(line_value[0])