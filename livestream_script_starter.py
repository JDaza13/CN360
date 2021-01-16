import sys
from subprocess import run
from time import sleep

file_path = 'streamyt_main.py'

RESTART_WAIT_SECONDS = 3
run_arg = ''

def get_arg_from_cla(argv):
	global run_arg
	if len(argv) > 1:
		run_arg = str(argv[1])

def start_script():

	get_arg_from_cla(sys.argv)
	print('Starting scritp with argv: ' + run_arg)

    try:
        run('python3 ' + file_path + ' ' + run_arg, shell=True, check=True) 
    except Exception as ex:
        print('Child script crashed')
        handle_crash()

def handle_crash():
    sleep(RESTART_WAIT_SECONDS)
    start_script()

start_script()