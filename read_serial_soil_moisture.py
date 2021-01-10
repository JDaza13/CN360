#!/usr/bin/env python3
import serial
import re

soil_moisture_value = 'soil moisture unavailable'

DRY_THRESHOLD = 0
WET_THRESHOLD = 0

def parse_soil_moisture(serial_val):
    return str((int(serial_val) - DRY_THRESHOLD) / (WET_THRESHOLD - DRY_THRESHOLD))

if __name__ == '__main__':
    serial_com = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    serial_com.flush()
    while True:
        if serial_com.in_waiting > 0:
            line = serial_com.readline().rstrip()
            line_value = re.findall('\d+', str(line))
            if line_value and len(line_value) > 0:
            	print(parse_soil_moisture(line_value[0]))