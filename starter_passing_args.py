from subprocess import run
from time import sleep

file_path = 'receive_ars.py'
run_args = ' 7ukg-59up-s1ya-4wdz-dvt0'

RESTART_WAIT_SECONDS = 3

def start_script():
    try:
        run('python3 ' + file_path + run_args, shell=True, check=True) 
    except Exception as ex:
        print('Child script crashed')

start_script()