#!/usr/bin/env python3

import signal
from getch import getch

def input_timeout(timeout=1):
	# note, pure Esc will return with delay
	pre_esc = ''
	try:
		signal.alarm(timeout) # set alarm
		try:
			key = ord(getch())
			if key == 27: # posix sequence?
				pre_esc = 'Esc'
				key = ord(getch())
				while key in [91, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 79]: # [arrows, ?, ?, win, shift, alt, ?, ctrl, ?, ?, ?, ?, fn ]
					# really bad in recognize... see `readchar` module
					pre_esc = key
					key = ord(getch())
		except OverflowError:
			key = 0
		signal.alarm(0) # clear alarm
	except KeyboardInterrupt:
		exit(0)
	except InputTimedOut:
		pass
	if key == 0 and pre_esc: # pure Esc key
		key = 27
	return key

def round_floor(val, decimals=0):
	deciamls = min(decimals, 10)
	factor = 1 / (10** decimals)
	return (val // factor) * factor

#class InputTimedOut(Exception): pass
def inputTimeOutHandler(signum, frame): pass # raise InputTimedOut
signal.signal(signal.SIGALRM, inputTimeOutHandler)

if __name__ == '__main__':
	while 1:
		print('You have 1 second to type in your stuff...')
		s = input_timeout()
		print(repr(s))
