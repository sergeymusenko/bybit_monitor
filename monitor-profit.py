#!/usr/bin/env python3
"""\
monitor-profit.py - P&L at Bybit
docs: https://bybit-exchange.github.io/docs/v5/intro

pip install pybit

error time to time:
	Added 2.5 seconds to recv_window. 2 retries remain.
	2024-02-07 20:03:15 - pybit._http_manager - ERROR - invalid request, please check your
	server timestamp or recv_window param.
	req_timestamp[1707328989637],server_timestamp[1707328995183],recv_window[5000]
	(ErrCode: 10002).
"""

__project__	= "Trading Bot"
__part__	= 'P&L at Bybit' # Futures only
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2024, musenko.com"
__license__	= "MIT"
__credits__	= ["Sergey Musenko"]
__date__	= "2024-01-18"
__version__	= "0.2"
__status__	= "dev"

from config import *
from functions import *
import os, sys
import time
from datetime import datetime
from termcolor import colored
from pybit.unified_trading import HTTP
from simple_telegram import *
import statistics

# get my secret LOCAL_CONFIG:
import socket
if socket.gethostname() == 'sereno':
	from local_config import *


def side_colored(side): return colored(f"{side:4}", 'red' if side == 'Sell' else 'green')

def tp_colored(tp, l=6, d=2): return colored(f"{tp:<{l}.{d}f}", 'cyan' if tp > 0 else None)

def pnl_colored(pnl, l=7, d=3, alarm=False):
	return colored(f"{pnl:<{l}.{d}f}", 'light_red' if pnl < 0 else 'green', attrs=(['blink'] if alarm else None))

def liq_colored(liq, l=6, d=2, prc=0):
	global min_PnL
	_alarm = ['blink'] if prc > 0 and liq > 0 and (1 - prc/liq) < min_PnL/100 else None
	return colored(f"{liq:<{l}.{d}f}", ('light_red' if _alarm else 'yellow') if liq else None, attrs=_alarm)


pnl_avg = {}
pnl_avg_len = 5 # collect avg for {n} last pnl values
alarms_lowest = {}

def main():
	global alarms_lowest, pnl_avg, pnl_avg_len
	time_mark = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	positions = False
	pos_profit = 0

	print(f'{"  loading...":40}\r', end='', flush=True)
	try:
		session = HTTP(api_key=api_key, api_secret=api_secret)
	except Exception:
		print('\nSorry, HTTP session error')

	# GET PSITIONS, category: spot, linear, inverse, option
	try:
		positions = session.get_positions(category="linear", settleCoin="USDT") # , symbol="XAIUSDT"
	except Exception:
		print('Sorry, read error, retry after sleep')
		send_to_telegram(TMapiToken, TMchatID, 'Connection lost', print_exception=False)
		return

	# start printout
	os.system('clear')
	print(f'{time_mark} {__part__}, Min Profit: {min_PnL}%')

	# positions
	if positions and positions['result']['list']:
		alarms = []
		coin_orders = []
		for pos in positions['result']['list']:
			seq = str(pos['seq'])
			side = side_colored(pos['side'])
			sign = sign_sell if pos['side'] == 'Sell' else sign_buy
			symbol = pos['symbol']
			symbolside = pos['symbol'] + pos['side']
			val = float(pos['positionValue'] or 0)
			prc = float(pos['markPrice'] or 0)
			pnl = float(pos['unrealisedPnl'] or 0)
			liq = float(pos['liqPrice'] or 0)

			pnl_direction = colored('-', 'light_blue') # mark pnl change side
			if symbolside in pnl_avg:
				symbolside_pnl_avg = statistics.fmean(pnl_avg[symbolside])
				if pnl != symbolside_pnl_avg:
					pnl_direction = colored('↗', 'green') if pnl > symbolside_pnl_avg  else colored('↘', 'light_red') # ↑↓
			else:
				pnl_avg[symbolside] = [] # init avg collection list
			if len(pnl_avg[symbolside]) >= pnl_avg_len: # keep {n} last elements in list
				pnl_avg[symbolside].pop(0) # remove oldest element
			pnl_avg[symbolside].append(pnl) # save pnl as last element

			pos_profit += pnl
			mark_alarmed = False
			pnl_alarm = min_PnL * val / 100
			liq_alarm = False # 1 if liq > 0 and (1 - prc/liq) < min_PnL/100 else None ----------------
			if pnl < pnl_alarm or liq_alarm:
				if symbolside not in alarms_lowest:
					alarms_lowest[symbolside] = pnl_alarm # first time
				if pnl < alarms_lowest[symbolside]: # new minimum found! notify again
					alarms_lowest[symbolside] = pnl
					alarms.append(f'{sign} {symbol} PnL: {pnl}')
				mark_alarmed = True
			PnL = pnl_colored(pnl, 8, 3, mark_alarmed)
			rpnl = float(pos['cumRealisedPnl'] or 0)
			liq = liq_colored(round(liq, 2)) # , prc=prc) -----------------
			tp = tp_colored(round(float(pos['takeProfit'] or 0), 2))
			sl = liq_colored(round(float(pos['stopLoss'] or 0), 2))
			created = int(pos['createdTime'])

			coin_orders.append([
				pnl,
				f"{side} {symbol:12} PnL: {pnl_direction} {PnL} VAL: {round(val, 2):<8} PRC: {round(prc, 2):<6} LIQ: {liq} TP: {tp} SL: {sl}"
			])

		# print out sorted, losers first
		coin_orders.sort(key=lambda x: x[0])
		i = 1
		for order in coin_orders:
			print(f"{str(i):>2}. {order[1]}")
			i += 1
		print(f"TOTAL P&L: {pnl_colored(pos_profit, 8, 3)}\n")

		if alarms: # send Telegram message
			message = f'{sign_alarm} <b>Bybit Futures Alarm:</b>'
			i = 1
			for al in alarms:
				message += f"\n{i}. {al}"
				i += 1
			send_to_telegram(TMapiToken, TMchatID, message)


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
				if key == 10 or key == 32: # reload now
					break
				elif key == 27: # exit
					raise KeyboardInterrupt
				s -= 1
		except KeyboardInterrupt: # exit on Ctrl+C
			print(f"\r{'Bye...':20}")
			break

# that's all folks!
