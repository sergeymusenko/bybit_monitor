#!/usr/bin/env python3
"""\
monitor-profit.py - P&L of all Positions and Spot Limit Orders
docs: https://bybit-exchange.github.io/docs/v5/intro

pip install pybit
pip install getch

error time to time:
Added 2.5 seconds to recv_window. 2 retries remain.
2024-02-07 20:03:15 - pybit._http_manager - ERROR - invalid request, please check your
server timestamp or recv_window param.
req_timestamp[1707328989637],server_timestamp[1707328995183],recv_window[5000]
(ErrCode: 10002).

"""

__project__	= "Trading Bot"
__part__	= 'P&L at Bybit' # of Futures and Spot Orders
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
from datetime import datetime
from termcolor import colored
from pybit.unified_trading import HTTP
from simple_telegram import *

check_spot	= True

# get my secret LOCAL_CONFIG:
import socket
if socket.gethostname() == 'sereno':
	from config_local import *


def side_colored(side): return colored(f"{side:4}", 'red' if side == 'Sell' else 'green')

def pnl_colored(pnl, l, d): return colored(f"{pnl:<{l}.{d}f}", 'light_red' if pnl < 0 else 'green')


alarms_lowest = {}

def main():
	global alarms_lowest
	time_mark = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	spotords = False
	spot_profit = 0
	positions = False
	pos_profit = 0

	print(f'{"  loading...":40}\r', end='', flush=True)
	try:
		session = HTTP(api_key=api_key, api_secret=api_secret)
	except Exception:
		print('\nSorry, HTTP session error')

	# get spot orders
	if check_spot:
		try:
			spotords = session.get_open_orders(category='spot', settleCoin="USDT" )
		except Exception:
			print('Sorry, Spot read error, retry after sleep')
			send_to_telegram(TMapiToken, TMchatID, 'Connection lost', print_exception=False)
			return

	# GET PSITIONS, category: spot, linear, inverse, option
	try:
		positions = session.get_positions(category="linear", settleCoin="USDT") # , symbol="XAIUSDT"
	except Exception:
		print('Sorry, Futures read error, retry after sleep')
#		send_to_telegram(TMapiToken, TMchatID, 'Connection lost', print_exception=False)
		return

	# start printout
	os.system('clear')
	print(f'🔥 {time_mark} {__part__}')

	# SPOT orders
	if spotords and spotords['result']['list']:
		print('SPOT:')
		coin_cur_pice = {}
		coin_orders = {}
		for spot in spotords['result']['list']:
			# 'createdTime': '1705942060763', 'updatedTime': '1705942060765',
			ordid = str(spot['orderId'])
			side = side_colored(spot['side'])
			sign = sign_sell if spot['side'] == 'Sell' else sign_buy
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
			pnl = pnl_colored(pnl, 7, 3)

			if symbol not in coin_orders:
				coin_orders[symbol] = []
			coin_orders[symbol].append([
				price,
				f"\t{sign} {symbol:10} P&L: {pnl} QTY: {round(qty,4):<8} PRC: {round(price,4):<8} USDT: {round(val,4):<10}TYP: {otype}"
			])

		# print out sorted
		for symbol in coin_orders:
			coin_orders[symbol].sort(reverse=True, key=lambda x: x[0])
			for order in coin_orders[symbol]:
				print(order[1])
		print(f"TOTAL SPOT P&L: {pnl_colored(spot_profit, 8, 3)}\n")

	# positions
	if positions and positions['result']['list']:
		alarms = []
		print('FUTURES:')
		coin_orders = []
		for pos in positions['result']['list']:
			seq = str(pos['seq'])
			side = side_colored(pos['side'])
			sign = sign_sell if pos['side'] == 'Sell' else sign_buy
			symbol = pos['symbol']
			val = float(pos['positionValue'] or 0)
			mark = float(pos['markPrice'] or 0)
			pnl = float(pos['unrealisedPnl'] or 0)
			pos_profit += pnl
			mark_alarmed = ''
			pnl_alarm = min_PnL * val / 100
			if pnl < pnl_alarm:
				if symbol not in alarms_lowest:
					alarms_lowest[symbol] = pnl_alarm # first time
				if pnl < alarms_lowest[symbol]: # new minimum found! notify again
					alarms_lowest[symbol] = pnl
					alarms.append(f'{sign} {symbol} PnL: {pnl}')
					mark_alarmed = f'{sign_alarm} '
			PnL = pnl_colored(pnl, 7, 3)
			rpnl = float(pos['cumRealisedPnl'] or 0)
			tp = float(pos['takeProfit'] or 0)
			sl = float(pos['stopLoss'] or 0)
			liq = float(pos['liqPrice'] or 0)
			created = int(pos['createdTime'])

			coin_orders.append([
				pnl,
				f"{side} {symbol:12} PnL: {mark_alarmed}{PnL} VAL: {round(val, 2):<8} PRC: {round(mark, 2):<6} TP: {round(tp, 2):<8} SL: {round(sl, 2):<8} LIQ: {round(liq, 2)}"
			])

		# print out sorted, losers first
		coin_orders.sort(key=lambda x: x[0])
		i = 1
		for order in coin_orders:
			print(f"{str(i)+'.':<3}{order[1]}")
			i += 1
		print(f"TOTAL FUTURES P&L: {pnl_colored(pos_profit, 8, 3)}\n")

		if alarms: # send Telegram message
			message = f'{sign_alarm} <b>Bybit Futures Alarm:</b>'
			i = 1
			for al in alarms:
				message += f"\n{i}. {al}"
				i += 1
#			send_to_telegram(TMapiToken, TMchatID, message)

	# spot+positions total
	if spot_profit !=0 and pos_profi != 0:
		total = spot_profit + pos_profit
		print(f"TOTAL P&L: {pnl_colored(total, 4)}\n")
	elif spot_profit == 0 and pos_profit == 0:
		print('nothing...')


if __name__ == '__main__':
	# send_to_telegram(TMapiToken, TMchatID, 'start')

	while True:
		main()
		sys.stdout.flush()
		try:
			s = sleep_time
			while s>0:
				print(f'  Sleep {s} sec... \r', end='')
				key = input_timeout() # it makes sleep 1s
				if key == 10: # reload now
					break
				elif key == 27: # exit
					raise KeyboardInterrupt
				s -= 1
		except KeyboardInterrupt: # exit on Ctrl+C
			print(f"\r{'Bye...':20}")
			break

# that's all folks!
