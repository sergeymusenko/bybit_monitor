#!/usr/bin/env python3
# Linux console ANSI sequences

__project__	= "ANSI ctrls"
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2024, musenko.com"
__license__	= "MIT"
__credits__	= ["Sergey Musenko"]
__date__	= "2024-03-12"
__version__	= "0.1"
__status__	= "prod"

__CTRLSEQS = dict(
	ICH = '\033[%s@',	# insert character(s)
	CUU = '\033[%sA',	# cusor up
	CUD = '\033[%sB',	# cursor down
	CUF = '\033[%sC',	# cursor foreward
	CUB = '\033[%sD',	# cursor backward
	CNL = '\033[%sE',	# cursor next line
	CPL = '\033[%sF',	# cursor preceding line
	CHA = '\033[%sG',	# cursor character absolute
	CUP = '\033[%sH',	# cursor position
	CHT = '\033[%sI',	# cursor forward tabulation
	ED  = '\033[%sJ',	# erase in display
	EL  = '\033[%sK',	# erase in line
	IL  = '\033[%sL',	# insert line(s)
	DL  = '\033[%sM',	# delete line(s)
	DCH = '\033[%sP',	# delete character(s)
	SU  = '\033[%sS',	# scroll up
	SD  = '\033[%sT',	# scroll down
	ECH = '\033[%sX',	# erase character(s)
	CBT = '\033[%sZ',	# cursor backward tabulation
	HPA = '\033[%s`',	# horizontal postion absolute
	VPA = '\033[%sd',	# vertical position absolute
	SGR = '\033[%sm',	# select graphic rendition
	SCP = '\033[s',  	# save cursor position
	RCP = '\033[u',  	# restore cursor position
	SCU = '\033[?25h',	# show cursor
	HCU = '\033[?25l',	# hide cursor
	EAS = '\033[?1049h',# enable alternate screen buffer
	DAS = '\033[?1049l',# disable alternate screen buffer
	RIS = '\033c',		# reset screen to initial state
)

def get_ANSIctrl(seq, n=0):
	if not seq in __CTRLSEQS: return ''
	if not '%s' in __CTRLSEQS[seq]: return __CTRLSEQS[seq]
	return __CTRLSEQS[seq] % n

def print_ANSIctrl(seq, n=0):
	print(get_ANSIctrl(seq, n), end='', flush=True)

if __name__ == '__main__':
	# print demo
	from time import sleep
	print_ANSIctrl('HCU')
	print('1234567890')
	sleep(1)
	# 1 line up and 5 char right
	print_ANSIctrl('CPL')
	print_ANSIctrl('CUF', 5)
	sleep(1)
	# clear to EOL
	print_ANSIctrl('EL')
	sleep(1)
	# demo done
	print_ANSIctrl('SCU')
	print()
	sleep(1)
	print_ANSIctrl('CUU', 3)
	print_ANSIctrl('DL', 3)
