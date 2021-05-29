import os, os.path
import sys

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

YOUTUBE_URL = 'rtmp://x.rtmp.youtube.com/live2/'
YT_KEY = ''

H_SIZE = 1920
V_SIZE = 1080
FRAME_RATE = 25
BITRATE = 4500000

TEMP_DEVICE_ID = '28-01193a3ed4e7'
TEMP_DEVICE_PATH = '/sys/bus/w1/devices/'+TEMP_DEVICE_ID+'/w1_slave'
TEMP_READ_FREQ_SEC = 300

SCREENSHOT_FODLER_PATH = 'screenshots/'
SCREENSHOT_BASE_FILE_PATH = SCREENSHOT_FODLER_PATH + 'cn360_screenshot_'
SCREENSHOT_FREQ_SEC = 150
SCREENSHOT_LOW_THRESHOLD_HOUR = 6
SCREENSHOT_HIGH_THRESHOLD_HOUR = 19

SOIL_MOIST_SERIAL_NAME = '/dev/ttyUSB0'
SOIL_MOIST_BAUD_RATE = 9600
DRY_THRESHOLD = 465
WET_THRESHOLD = 210

GENERAL_START_DATE = dt.datetime.strptime('14/01/21 13:00:00', '%d/%m/%y %H:%M:%S')

plain_temp_val = ''
temp_val = 'temperature unavailable'
plain_soil_moist_val = ''
soil_moisture_value = 'soil moisture unavailable'

def get_key_from_cla(argv):
    global YT_KEY
    if len(argv) > 1:
        YT_KEY = str(argv[1])

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

def config_screenshots():
    if not os.path.exists(SCREENSHOT_FODLER_PATH):
        os.makedirs(SCREENSHOT_FODLER_PATH)

def parse_soil_moisture(serial_val):
    inverted_percentage = 100 * (int(serial_val)-WET_THRESHOLD) / (DRY_THRESHOLD-WET_THRESHOLD)
    return '{:.2f}'.format(100-inverted_percentage)

def get_temp(dev_file):
    global temp_val
    global plain_temp_val
    f = open(dev_file,"r")
    contents = f.readlines()
    f.close()
    index = contents[-1].find("t=")
    if index != -1 :
        temperature = contents[-1][index+2:]
        cels =float(temperature)/1000
        plain_temp_val = str(cels)
        temp_val = str(cels) + ' celsius '

config_logs()
config_screenshots()

def main_stream():


    logger.warning('Starting stream at: ' + dt.datetime.now().strftime('%H:%M:%S'))
    get_key_from_cla(sys.argv)
    days_number = 0
    sensor_data_line = ''

    global soil_moisture_value
    global plain_soil_moist_val

    light_control_state = 'off'
    serial_com = serial.Serial(SOIL_MOIST_SERIAL_NAME, SOIL_MOIST_BAUD_RATE, timeout=10)

    stream_cmd = 'ffmpeg -re -ar 44100 -ac 2 -loglevel warning -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -thread_queue_size 64 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE_URL + YT_KEY
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
        screenshot_checkpoint = read_checkpoint
        while True:
            time_now = dt.datetime.now()
            days_number = (time_now - GENERAL_START_DATE).days
            #read sensors
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
                        plain_soil_moist_val = parse_soil_moisture(line_value[0])
                        soil_moisture_value = parse_soil_moisture(line_value[0]) + ' %  soil moist'
                sensor_data_line = plain_temp_val + ',' + str(line) + ',' + str(line_value) + ',' + plain_soil_moist_val + ',' + time_now.strftime('%Y-%m-%d %H:%M:%S')
                logger.warning('New line on sensor data')
                logger.warning(sensor_data_line)
            #take screenshots
            annotation_text = ' CN360 - Day ' + str(days_number) + ' \n ' + time_now.strftime('%Y-%m-%d %H:%M:%S') + ' \n ' + temp_val + ' \n ' + soil_moisture_value + ' '
            if (time_now.hour >= SCREENSHOT_LOW_THRESHOLD_HOUR and time_now.hour < SCREENSHOT_HIGH_THRESHOLD_HOUR) and (time_now - screenshot_checkpoint).seconds > SCREENSHOT_FREQ_SEC:
                logger.warning('Taking screenshot...')
                filename_str = SCREENSHOT_BASE_FILE_PATH + time_now.strftime('%Y%m%d%H%M') + '.jpg'
                camera.annotate_text = ''
                camera.wait_recording(2)
                camera.capture(filename_str, use_video_port=True)
                camera.wait_recording(2)
                screenshot_checkpoint = dt.datetime.now()
                logger.warning('Screenshot taken: ' + filename_str)
                camera.annotate_text = annotation_text
                if light_control_state == 'on':
                    light_control_state = 'off'
                if light_control_state == 'off':
                    light_control_state = 'on'
                #light control
                serial_com.write(light_control_state + '\n');
            camera.annotate_text = annotation_text
            camera.wait_recording(1)
    except Exception as ex:
        logger.warning(ex)
        logger.warning('Exception caught!')
        camera.stop_recording()
        raise Exception('Stream crashed')
    finally:
        camera.close()
        stream_pipe.stdin.close()
        stream_pipe.wait()
        logger.warning('Camera safely shut down')
main_stream()
