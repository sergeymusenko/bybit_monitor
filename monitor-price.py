#!/usr/bin/env python3
"""\
monitor-coinprice.py - Price monitor Coin/USDT
docs: https://bybit-exchange.github.io/docs/v5/intro

pip install pybit
pip install getch
"""

__project__	= "Trading Bot"
__part__	= 'Price monitor Coin/USDT'
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2024, musenko.com"
__license__	= "MIT"
__credits__	= ["Sergey Musenko"]
__date__	= "2024-01-18"
__version__	= "0.1"
__status__	= "dev"

from config import *
from functions import *
import os, sys
import time
from getch import getch
from datetime import datetime
from termcolor import colored
from pybit.unified_trading import HTTP

# get my secret LOCAL_CONFIG:
import socket
if socket.gethostname() == 'sereno':
	from config_local import *

sleep_time = 60
session = False

precision = 1 # % close, notify if so

checklist = {
	'ATOMUSDT': [[8.5, 6.5],	'invest x10, 10-20%dep'],
	'FLOWUSDT': [[0.69, 0.45],	'invest x40, 2%dep'], # Disney, Pixar, NBA, Bibnance,
	'NEARUSDT': [[2.27, 1.06],	'invest x11'],
	'DOTUSDT':	[[5.5, 3.8],	'invest x8'],
#	'TKOUSDT':	[[0.3],			'invest x30'], # binance
	'INJUSDT':	[[33.32],		'get short'],
#	'INJUSDT':	[[15, 9, 4],	'invest'],
#	'TIAUSDT': [[19.02],	'close TIA'],
#	'LTCUSDT': [[69],		'get long'],
#	'TWTUSDT': [[0.9, 0.63, 0.34], 'invest... may be'],
#	'OPUSDT':  [[3.2],		'get long'],
#	'ARBUSDT': [[2.1],		'get long'],
#	'BEAMUSDT':[[0.0178],	'get long'],
#	'SUIUSDT': [[1.25],		'get long'],
#	'BTCUSDT': [[52300, 41700, 37400, 34400, 33100 ], 'invest'],
}
''' Petrenko:
	FLM		BLUR	ING		BNB
	XVS		FLR		HIGH	BONK
	BEAM	SOL		FXS		KEY
	XVS		ATOM	DOT		ARB
	AI		HOT		AXS
'''

def main():
	global session
	time_mark = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	os.system('clear')
	print(f'🔥 {time_mark} {__part__}')

	print(' loading...\r', end='')
	session = HTTP(api_key=api_key, api_secret=api_secret)

	coin_cur_pice = {}
	for symbol in checklist:
		checkprice = checklist[symbol][0]
		note = checklist[symbol][1]
		if symbol not in coin_cur_pice: # load once per symbol
			try:
				ticker = session.get_tickers(category='spot', symbol=symbol)
			except Exception as e:
				print(f"\nError getting ticker: {str(e)}\n")
				continue
			coin_cur_pice[symbol] = float(ticker['result']['list'][0]['lastPrice'])
		cur_price = coin_cur_pice[symbol]
		print(f"🪙 {symbol:10} {cur_price:<10} ☕ {note}")
		for check in checkprice:
			close = ''
			if check and abs(check - cur_price) / cur_price <= precision / 100:
				close = colored(f'🔴 it is {precision}% close', 'green')
				# send notification...
			else:
				still = round(100 * (check - cur_price) / cur_price, 1)
				close = f"{still:+}% left"
			print(f"\t   to {check:<10} {close}")


if __name__ == '__main__':
	while True:
		main()
		sys.stdout.flush()
		try:
			s = sleep_time
			while s>0:
				print(f'  Sleep {s} sec... \r', end='')
				key = input_timeout()
				if key == 10: # reload now
					break
				elif key == 27: # exit
					raise KeyboardInterrupt()
				s -= 1
		except KeyboardInterrupt: # exit on Ctrl+C
			print(f"\r{'Bye...':20}")
			break

# that's all folks!
