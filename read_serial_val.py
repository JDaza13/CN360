#!/usr/bin/env python3
import serial
import re

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.flush()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().rstrip()
            line_value = re.findall('\d+', str(line))
            if line_value and len(line_value) > 0:
            	print(line_value[0])