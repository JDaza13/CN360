#!/usr/bin/env python3
import serial
import re

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.flush()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().rstrip
            line_value = str(line)
            print(line_value)