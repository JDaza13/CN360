#!/usr/bin/python

import sys

YT_KEY = ''

def get_key_from_cla(argv):
	global YT_KEY
	if len(argv) > 1:
		YT_KEY = str(argv[2])

get_key_from_cla(sys.argv)
print('Key: ' + YT_KEY)