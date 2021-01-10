import os, os.path

import subprocess 
import picamera
import concurrent.futures

import serial
import re

import time
import datetime as dt

import logging

logger = None

BRAND_LABEL_NAME = 'CN360'
LOGS_FOLDER_PATH = 'logs/'
LOGS_FILE_PATH = LOGS_FOLDER_PATH + 'cn360_test.log' 

YOUTUBE= 'rtmp://x.rtmp.youtube.com/live2/'
KEY= '7ukg-59up-s1ya-4wdz-dvt0'

H_SIZE = 1920
V_SIZE = 1080
FRAME_RATE = 25
BITRATE = 4500000

TEMP_DEVICE_ID = '28-01193a3ed4e7'
TEMP_DEVICE_PATH = '/sys/bus/w1/devices/'+TEMP_DEVICE_ID+'/w1_slave'
TEMP_READ_FREQ_SEC = 300

SOIL_MOIST_SERIAL_NAME = '/dev/ttyUSB0'
SOIL_MOIST_BAUD_RATE = 9600
DRY_THRESHOLD = 465
WET_THRESHOLD = 210

GENERAL_START_DATE = dt.datetime.strptime('24/09/20 00:00:01', '%d/%m/%y %H:%M:%S')

temp_val = 'temperature unavailable'
soil_moisture_value = 'soil moisture unavailable'

def config_logs():
    global logger
    if not os.path.exists(LOGS_FOLDER_PATH):
        os.makedirs(LOGS_FOLDER_PATH)

    logger = logging.getLogger(BRAND_LABEL_NAME)
    logger.setLevel(logging.WARN)
    fh = logging.FileHandler(LOGS_FILE_PATH)
    fh.setLevel(logging.WARN)
    logger.addHandler(fh)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def parse_soil_moisture(serial_val):
    inverted_percentage = 100 * (int(serial_val)-WET_THRESHOLD) / (DRY_THRESHOLD-WET_THRESHOLD)   
    return '{:.2f}'.format(100-inverted_percentage)

def get_temp(dev_file):
    global temp_val    
    f = open(dev_file,"r")
    contents = f.readlines()
    f.close()
    index = contents[-1].find("t=")
    if index != -1 :
        temperature = contents[-1][index+2:]
        cels =float(temperature)/1000
        temp_val = str(cels) + ' celsius '

config_logs()

def main_stream():

    logger.warning('Starting stream at: ' + dt.datetime.now().strftime('%H:%M:%S'))
    days_number = 0

    global soil_moisture_value
    serial_com = serial.Serial(SOIL_MOIST_SERIAL_NAME, SOIL_MOIST_BAUD_RATE, timeout=10)

    stream_cmd = 'ffmpeg -re -ar 44100 -ac 2 -loglevel warning -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -thread_queue_size 64 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE + KEY 
    stream_pipe = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE)
    camera = picamera.PiCamera(resolution=(H_SIZE, V_SIZE), framerate=FRAME_RATE)
    camera.annotate_background = picamera.Color('black')

    try: 
        now = time.strftime("%Y-%m-%d-%H:%M:%S")
        camera.framerate = FRAME_RATE 
        camera.vflip = True 
        camera.hflip = True
        camera.start_preview(fullscreen=False, window = (800, 20, 640, 480))
        camera.start_recording(stream_pipe.stdin, format='h264', bitrate = BITRATE)
        read_checkpoint = dt.datetime.now()
        while True:
            time_now = dt.datetime.now()
            if (time_now - read_checkpoint).seconds > TEMP_READ_FREQ_SEC:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(get_temp, TEMP_DEVICE_PATH)

                read_checkpoint = dt.datetime.now()
                #read serial value
                serial_com.flush()
                if serial_com.in_waiting > 0:
                    line = serial_com.readline().rstrip()
                    line_value = re.findall('\d+', str(line))
                    if line_value and len(line_value) > 0:
                        soil_moisture_value = print(parse_soil_moisture(line_value[0]) + ' %  soil moist')

            days_number = (time_now - GENERAL_START_DATE).days
            camera.annotate_text = ' CN360 - Day ' + str(days_number) + ' \n ' + time_now.strftime('%Y-%m-%d %H:%M:%S') + ' \n ' + temp_val + ' \n ' + soil_moisture_value + ' '
            camera.wait_recording(1)
    except Exception as ex:
        logger.warning(ex)
        logger.warning('Exception caught, rebooting stream...')
        camera.stop_recording()
    finally:
        camera.close() 
        stream_pipe.stdin.close() 
        stream_pipe.wait()
        logger.warning('Camera safely shut down')
        logger.warning('About to attempt stream restart...')
        main_stream()
main_stream()
