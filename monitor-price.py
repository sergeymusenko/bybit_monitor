#!/usr/bin/env python3
"""\
monitor-coinprice.py - Price monitor Coin/USDT
docs: https://bybit-exchange.github.io/docs/v5/intro

pip install pybit
"""

__project__	= "Trading Bot"
__part__	= 'Price monitor Coin/USDT'
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2024, musenko.com"
__license__	= "GPL"
__credits__	= ["Sergey Musenko"]
__date__	= "2024-01-18"
__version__	= "0.1"
__status__	= "dev"

from config import *
import os, sys
import time
from datetime import datetime
from termcolor import colored
from pybit.unified_trading import HTTP

# get my secret LOCAL_CONFIG:
import socket
if socket.gethostname() == 'sereno':
	from local_config import *

sleep_time = 60
session = False

precision = 1 # % close, notify if so

checklist = {
	'TIAUSDT': [ 19.02 ],
	'DOTUSDT': [ 7.75 ],
	'ETHUSDT': [ 3000 ],
	'LTCUSDT': [ 69 ],
	'OPUSDT': [ 3.2 ],
	'ARBUSDT': [ 2.1 ],
	'BEAMUSDT': [ 0.0178 ],
	'SUIUSDT':[ 1.25 ],
	'INJUSDT':[ 15, 9, 4 ],
}


def main():
	global session
	os.system('clear')
	print(f'🔥 {__part__}')

	if not session:
		print('Session init...')
		session = HTTP(api_key=api_key, api_secret=api_secret)

	coin_cur_pice = {}
	for symbol in checklist:
		if symbol not in coin_cur_pice: # load once per symbol
			ticker = session.get_tickers(category='spot', symbol=symbol)
			coin_cur_pice[symbol] = float(ticker['result']['list'][0]['lastPrice'])
		cur_price = coin_cur_pice[symbol]
		print(f"{symbol:10} PRC: {cur_price}")
		for check in checklist[symbol]:
			close = ''
			if check and abs(check - cur_price) / cur_price <= precision / 100:
				close = colored(f'it is {precision}% close', 'green')
				# send notification...
			else:
				still = round(100 * (check - cur_price) / cur_price, 1)
				close = f"still {still:+}% left"
			print(f"\tchecking: {check:<10} {close}")


if __name__ == '__main__':
	while True:
		main()
		print(f'\nSleep {sleep_time} sec...', end='')
		sys.stdout.flush()
		try:
			time.sleep(sleep_time)
		except KeyboardInterrupt:
			print(f"\r{'Bye...':20}")
			break

# that's all folks!
