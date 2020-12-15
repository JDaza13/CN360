import subprocess 
import picamera
import concurrent.futures

import warnings
import time
import datetime as dt

import logging

logger = logging.getLogger('log_exaple')
logger.setLevel(logging.WARN)
fh = logging.FileHandler('cn360_test.log')
fh.setLevel(logging.WARN)
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

YOUTUBE= 'rtmp://x.rtmp.youtube.com/live2/'
KEY= '6e2h-q6wu-s0rf-qqfc-7ys9'

H_SIZE = 1920
V_SIZE = 1080
FRAME_RATE = 25
BITRATE = 4500000

TEMP_DEVICE_ID = '28-01193a3ed4e7'
TEMP_DEVICE_PATH = '/sys/bus/w1/devices/'+TEMP_DEVICE_ID+'/w1_slave'
TEMP_READ_FREQ_SEC = 10

temp_val = 'temperature not available'

def is_keyboard_interrupt(exception):
    return (type(exception) is KeyboardInterrupt
        or type(exception).__name__ == 'KeyboardInterruptException')

def get_temp(dev_file):
    global temp_val    
    f = open(dev_file,"r")
    contents = f.readlines()
    f.close()
    index = contents[-1].find("t=")
    if index != -1 :
        temperature = contents[-1][index+2:]
        cels =float(temperature)/1000
        temp_val = str(cels) + ' C - ' + dt.datetime.now().strftime('%H:%M:%S')

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
        camera.annotate_text = ' CN 360 \n ' + time_now.strftime('%Y-%m-%d %H:%M:%S') + ' \n ' + temp_val + ' '
        camera.wait_recording(1)
except Exception as ex:
    try:
        if is_keyboard_interrupt(ex):
            camera.close() 
            stream_pipe.stdin.close() 
            stream_pipe.wait()
            logger.warning('Camera safely shut down')
            raise ex
        else:
            logger.warning('Exception caught!')
            logger.warning(ex)
    except ValueError:
        logger.warning(ValueError)    
#raspivid -o - -t 0 -vf -hf -fps 30 -b 6000000 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://x.rtmp.youtube.com/live2/wg4f-bkfq-64at-245d-0h49
