#!/usr/bin/env python3
"""\
monitor-profit.py - P&L of all Positions and Spot Limit Orders
docs: https://bybit-exchange.github.io/docs/v5/intro

pip install pybit
"""

__project__	= "Trading Bot"
__part__	= 'P&L of all Positions and Spot Limit Orders'
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


sleep_time = 30
session = False


def side_colored(side): return colored(f"{side:4}", 'red' if side == 'Sell' else 'green')

def pnl_colored(pnl): return colored(f"{pnl:<8}", 'red' if pnl < 0 else 'green')

def main():
	global session
	os.system('clear')
	print(f'🔥 {__part__}')

	if not session:
		print('Session init...')
		session = HTTP(api_key=api_key, api_secret=api_secret)

	# get SPOT orders
	spotords = session.get_open_orders(category='spot', settleCoin="USDT" )
	if spotords['result']['list']:
		print('SPOT:')
		coin_cur_pice = {}
		coin_orders = {}
		spot_profit = 0
		for spot in spotords['result']['list']:
			# 'createdTime': '1705942060763', 'updatedTime': '1705942060765',
			ordid = str(spot['orderId'])
			side = side_colored(spot['side'])
			symbol = spot['symbol']
			otype = spot['orderType']
			price = float(spot['price'] or 0)
			qty = float(spot['qty'] or 0)
			val = price * qty
			# current price
			if symbol not in coin_cur_pice: # load once per symbol
				ticker = session.get_tickers(category='spot', symbol=symbol)
				coin_cur_pice[symbol] = float(ticker['result']['list'][0]['lastPrice'])
			cur_price = coin_cur_pice[symbol]
			reverse = -1 if spot['side'] == 'Sell' else 1
			pnl = reverse * (cur_price * qty - val)
			spot_profit += pnl
			pnl = pnl_colored(round(pnl, 4))
			if symbol not in coin_orders:
				coin_orders[symbol] = []
			coin_orders[symbol].append([
				price,
				f"\t{side:4}: {symbol:10} P&L: {pnl:<10} QTY: {round(qty,4):<8} PRC: {round(price,4):<8} USDT: {round(val,4):<10}TYP: {otype}"
			])
		# print out
		for symbol in coin_orders:
			coin_orders[symbol].sort(reverse=True, key=lambda x: x[0])
			for order in coin_orders[symbol]:
				print(order[1])
		print(f"\tTOTAL SPOT P&L: {pnl_colored(round(spot_profit, 4))}")

	# GET PSITIONS, category: spot, linear, inverse, option
	pos_profit = 0
	positions = session.get_positions(category="linear", settleCoin="USDT") # , symbol="XAIUSDT"
	if positions['result']['list']:
		print('FUTURES:')
		for pos in positions['result']['list']:
			seq = str(pos['seq'])
			side = side_colored(pos['side'])
			symbol = pos['symbol']
			val = float(pos['positionValue'] or 0)
			mark = float(pos['markPrice'] or 0)
			pnl = float(pos['unrealisedPnl'] or 0)
			pos_profit += pnl
			pnl = pnl_colored(round(pnl, 4))
			rpnl = float(pos['cumRealisedPnl'] or 0)
			tp = float(pos['takeProfit'] or 0)
			sl = float(pos['stopLoss'] or 0)
			liq = float(pos['liqPrice'] or 0)
			# created = int(pos['createdTime'])
			print(f"\t{side}: {symbol:10} PnL: {pnl} TP: {round(tp,2):<6} SL: {round(sl,2):<6} LIQ: {round(liq,4)} PRC: {round(mark,2):<6} USDT: {round(val,4):<8}")
		print(f"\tTOTAL FUTURES P&L: {pnl_colored(round(pos_profit, 4))}")

	print(f"\nTOTAL P&L: {pnl_colored(round(spot_profit + pos_profit, 4))}")


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
