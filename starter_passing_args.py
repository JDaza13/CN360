from subprocess import run
from time import sleep

import sys

file_path = 'receive_args.py'
run_arg = ''

def get_arg_from_cla(argv):
	global run_arg
	if len(argv) > 1:
		run_arg = str(argv[1])

def start_script():

	get_arg_from_cla(sys.argv)

	try:
		run('python3 ' + file_path + ' ' + run_arg, shell=True, check=True) 
    except Exception as ex:
        print('Child script crashed')

start_script()