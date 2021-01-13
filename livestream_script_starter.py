from subprocess import run
from time import sleep

file_path = 'streamyt_main.py'

RESTART_WAIT_SECONDS = 3

def start_script():
    try:
        run('python3 ' + file_path, shell=True, check=True) 
    except Exception as ex:
        print('Child script crashed')
        handle_crash()

def handle_crash():
    sleep(RESTART_WAIT_SECONDS)
    start_script()

start_script()