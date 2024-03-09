#!/usr/bin/env python3
"""\
monitor-profit.py - P&L at Bybit
docs: https://bybit-exchange.github.io/docs/v5/intro
works with Cross-Margin

pip install pybit

server time error:
	pybit._http_manager - ERROR - invalid request, please check your server timestamp or recv_window param.
	req_timestamp[1707815756893],server_timestamp[1707815762060],recv_window[5000] (ErrCode: 10002).
"""

__project__	= "Trading Bot"
__part__	= 'PnL @ Bybit' # Futures only
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
	from config_local import *


def side_colored(side): return colored(f"{side:4}", 'red' if side == 'Sell' else 'green')

def tp_colored(tp, l=7, d=2): return colored(f"{tp:<{l}.0{d}f}", 'cyan' if tp > 0 else None)

def pnl_colored(pnl, l=7, d=3, alarm=False): return colored(f"{pnl:<{l}.0{d}f}", 'light_red' if pnl < 0 else 'green', attrs=(['blink'] if alarm else None))

def liq_colored(liq, l=6, d=2, alarm=False): return colored(f"{liq:<{l}.0{d}f}", None if not liq else ('light_red' if alarm else 'yellow'), attrs=(['blink'] if alarm else None))



pnl_avg = {}
pnl_avg_len = 5 # collect avg for {n} last pnl values
alarms_lowest = {}

def main():
	global alarms_lowest, pnl_avg, pnl_avg_len, min_PnL, min_LIQ
	time_mark = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	print(f'{"  loading...":40}\r', end='', flush=True)

	# GET PSITIONS (category: spot, linear, inverse, option)
	try:
		session = HTTP(api_key=api_key, api_secret=api_secret)
		depo = session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0] # , coin="BTC"
		positions = session.get_positions(category="linear", settleCoin="USDT") # , symbol="XAIUSDT"
	except Exception:
		print('Sorry, read error, retry after sleep')
#		send_to_telegram(TMapiToken, TMchatID, 'Connection lost, retry after sleep', print_exception=False)
		return

	# start printout
	os.system('clear')
	mark_alert = '. Alert if PnL'+colored(f"<{min_PnL}%", 'light_red') if min_PnL<0 else ""
	mark_loss = '. Kill if PnL'+colored(f"<{min_Loss}%", 'light_red') if min_Loss<0 else ""
	print(f'{time_mark} {__part__}{mark_alert}{mark_loss}.')

	# deposit margin
	atype = depo['accountType']
	# wallet = float(depo['totalWalletBalance'])
	marginbalance = float(depo['totalMarginBalance'])
	#marginmaintenance = 100 * (float(depo['totalMaintenanceMargin']) / marginbalance)
	marginini = float(depo['totalInitialMargin'])
	margininipcnt = round(100 * marginini / marginbalance, 2)
	margininipcntclr = 'light_red' if margininipcnt >= 50 else 'yellow' if margininipcnt >= 30 else 'cyan' if margininipcnt >= 10 else 'green'
	marginavl = f"{round(marginbalance - marginini, 2):.02f}"
	print(f"Margin: {round(marginbalance, 2):.02f}, Available: {colored(marginavl, margininipcntclr)}, Used: {colored(str(margininipcnt) + '%', margininipcntclr)}. All in USDT.")

	pos_profit = 0
	alarms_list = []
	close_list = []
	position_orders = []

	# proceed positions
	if positions and positions['result']['list']:
		for pos in positions['result']['list']:
			symbol = pos['symbol']
			side = pos['side']
			sidemark = side_colored(side)
			sign = sign_sell if side == 'Sell' else sign_buy
			symbolside = symbol + side
			val = float(pos['positionValue'] or 0)
			prc = float(pos['markPrice'] or 0)
			lvrg = float(pos['leverage'] or 0) # leverage = плечо
			pnl = float(pos['unrealisedPnl'] or 0)
			liq = float(pos['liqPrice'] or 0)
			created = int(pos['createdTime'])
			posIdx = pos['positionIdx'] # needed to close pos on loss
			pos_profit += pnl

			# mark pnl change side, use avg per previos values
			pnl_direction = colored('-', 'light_blue')
			if symbolside in pnl_avg:
				symbolside_pnl_avg = statistics.fmean(pnl_avg[symbolside])
				if pnl != symbolside_pnl_avg:
					pnl_direction = colored('↗', 'green') if pnl > symbolside_pnl_avg  else colored('↘', 'light_red') # ↑↓
			else:
				pnl_avg[symbolside] = [] # init avg collection list
			if len(pnl_avg[symbolside]) >= pnl_avg_len: # keep {n} last elements in list
				pnl_avg[symbolside].pop(0) # remove oldest element
			pnl_avg[symbolside].append(pnl) # save pnl as last element

			# alarms, gather to `alarms` list then use it later to send Telegram message
			liq_alarm = liq > 0 and abs(prc - liq)/max(prc, liq) < (min_LIQ/100) # liquidation alarm, use min_LIQ config
			if liq_alarm:
				alarms_list.append(f'{sign} {symbol} {min_LIQ}% to LIQUIDATION')

			pnl_alarm = min_PnL * val / 100 # pnl alarm, use min_PnL config
			if pnl < pnl_alarm:
				if symbolside not in alarms_lowest:
					alarms_lowest[symbolside] = pnl_alarm # first time
				if pnl < alarms_lowest[symbolside]: # new minimum found! notify again
					alarms_lowest[symbolside] = pnl
					alarms_list.append(f'{sign} {symbol} PnL: {pnl}')

			kill_loss = min_Loss * val / 100 # pnl alarm, use min_PnL config
			if min_Loss < 0 and pnl < kill_loss:
				close_list.append([symbol, side, posIdx, pnl])

			PnL = pnl_colored(pnl, 8, 3, pnl < pnl_alarm)
			rpnl = float(pos['cumRealisedPnl'] or 0)
			liq = liq_colored(round(liq, 2), alarm=liq_alarm)
			tp = tp_colored(round(float(pos['takeProfit'] or 0), 2))
			sl = liq_colored(round(float(pos['stopLoss'] or 0), 2))

			# gather positions here then sort by pnl and printout
			position_orders.append([
				pnl,
				f"{sidemark} {symbol.replace('1000', '').lstrip('0'):12} PnL: {pnl_direction} {PnL} VAL: {round(val, 2):<8.02f} PRC: {round(prc, 2):<7.02f} LIQ: {liq} TP: {tp} SL: {sl}"
			])

		# print out sorted, loosers first
		position_orders.sort(key=lambda x: x[0])
		i = 1
		for order in position_orders:
			print(f"{str(i):>2}. {order[1]}")
			i += 1
		print(f"TOTAL P&L: {pnl_colored(pos_profit, 8, 3)}")

		# send alarms to Telegram
		if alarms_list:
			message = f'{sign_alarm} <b>Bybit Futures Alarm:</b>'
			i = 1
			for al in alarms_list:
				message += f"\n{i}. {al}"
				i += 1
			send_to_telegram(TMapiToken, TMchatID, message)

		# close loss positions and send to Telegram
		if min_Loss < 0 and close_list:
			message = "Close LOSS positions:"
			print(f"\n{message}")
			i = 1
			for pos in close_list:
				symbol, posside, positionIdx, pnl = pos
				side = "Buy" if posside == 'Sell' else "Sell" # side contrary to position side
				print(f"{i:2}. {side_colored(side)} {symbol} with PnL {pnl_colored(pnl)}... ", end='')
				message += f"\n{i:2}. {side} {symbol} ... "
				try:
					################### kill position
					session.place_order(category="linear", symbol=symbol, side=side, positionIdx=positionIdx, orderType="Market", qty="0", reduceOnly=True)
					###################
					print(colored('closed', 'red'))
					message += "closed"
				except Exception as ex:
					print(f'ERROR {ex.status_code}, position NOT closed!')
					message += "ERROR!"
				i += 1
			send_to_telegram(TMapiToken, TMchatID, message)

	del session # unset, I do not know if it keeps connection or what ever
	print()


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
