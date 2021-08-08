import os, os.path
import sys

import subprocess
import picamera
import concurrent.futures
import re

import time
import datetime as dt

import logging

logger = None

BRAND_LABEL_NAME = 'CN360_Radio'
LOGS_FOLDER_PATH = 'logs/'
LOGS_FILE_PATH = LOGS_FOLDER_PATH + 'cn360_liveradio.log'

YOUTUBE_URL = 'rtmp://x.rtmp.youtube.com/live2/'
YT_KEY = ''

H_SIZE = 1920
V_SIZE = 1080
FRAME_RATE = 25
BITRATE = 4500000

GENERAL_START_DATE = dt.datetime.strptime('14/01/21 13:00:00', '%d/%m/%y %H:%M:%S')


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

config_logs()

def main_stream():

    logger.warning('Starting stream at: ' + dt.datetime.now().strftime('%H:%M:%S'))
    get_key_from_cla(sys.argv)
    
    stream_cmd = 'ffmpeg -re -ar 44100 -ac 2 -loglevel warning -acodec pcm_s16le -f s16le -i video/base_radio_file.mp4 -f h264 -thread_queue_size 64 -i - -vcodec copy -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE_URL + YT_KEY
    stream_pipe = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE)
   
    try:
        now = time.strftime("%Y-%m-%d-%H:%M:%S")
        while True:
            time_now = dt.datetime.now()
            
    except Exception as ex:
        logger.warning(ex)
        logger.warning('Exception caught!')
        raise Exception('Stream crashed')
    finally:
        camera.close()
        stream_pipe.stdin.close()
        stream_pipe.wait()
        logger.warning('Live radio safely shut down')
main_stream()
