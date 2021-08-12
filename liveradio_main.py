import os, os.path
import sys

import subprocess
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

STREAM_SOURCES = ' -stream_loop -1 -re -i video/base_radio_file.mp4 -stream_loop -1 -re -f concat -i audio_input_list.txt '
STREAM_CONFIG = ' -map 0:v -map 1:a -c:v libx264 -vf format=yuv420p -b:v 2M -bufsize 4M -maxrate 2M -g 50 -c:a aac -b:a 128k -flags +global_header '

H_SIZE = 1920
V_SIZE = 1080
FRAME_RATE = 25
BITRATE = 4500000

# python3 liveradio_script_starter.py [YT_KEY]
# ffmpeg -stream_loop -1 -re -i video/base_radio_file.mp4 -loglevel warning -c:v libx264 -b:v 2M -c:a copy -strict -2 -flags +global_header -bsf:a aac_adtstoasc -bufsize 2100k -f flv ' + YOUTUBE_URL + YT_KEY
# ffmpeg -stream_loop -1 -re -i video/first_loop_test.mp4 -stream_loop -1 -re -f concat -i audio_input_list.txt -map 0:v -map 1:a -c:v libx264 -vf format=yuv420p -b:v 2M -bufsize 4M -maxrate 2M -g 50 -c:a aac -b:a 128k -flags +global_header -f flv rtmp://x.rtmp.youtube.com/live2/
# ffmpeg -stream_loop -1 -re -i video/base_radio_file.mp4 -stream_loop -1 -re -f concat -i audio_input_list.txt -map 0:v -map 1:a -c:v libx264 -vf format=yuv420p -b:v 2M -bufsize 4M -maxrate 2M -g 50 -c:a aac -b:a 128k -flags +global_header -f flv rtmp://x.rtmp.youtube.com/live2/

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
    
    stream_cmd = 'ffmpeg' + STREAM_SOURCES + STREAM_CONFIG + YOUTUBE_URL + YT_KEY
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
        stream_pipe.stdin.close()
        stream_pipe.wait()
        logger.warning('Live radio safely shut down')
main_stream()
