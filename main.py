#!/usr/bin/env python3
"""\
Trading Monitor Bot on Pybit
docs: https://bybit-exchange.github.io/docs/v5/intro

pip install pybit
"""

__project__	= "Trading Bot"
__part__	= 'Check Balance and Active Positions'
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2023, musenko.com"
__license__	= "GPL"
__credits__	= ["Sergey Musenko"]
__date__	= "2023-12-26"
__version__	= "0.1"
__status__	= "dev"

from config import *
import os, sys
import time
from datetime import datetime
from termcolor import colored
from pybit.unified_trading import HTTP

sleep_time = 30
session = False


def side_colored(side): return colored(f"{side:4}", 'red' if side == 'Sell' else 'green')

def pnl_colored(pnl): return colored(f"{pnl:<8}", 'red' if pnl < 0 else 'green')

def main():
	global session
	os.system('clear')
	print('🔥 Trading Monitor Bot on Pybit')

	if not session:
		print('init session...')
		session = HTTP(api_key=api_key, api_secret=api_secret)

	# get balance... not all...
	session = HTTP(api_key=api_key, api_secret=api_secret)
	# accountType: UNIFIED (trade spot/linear/options), CONTRACT(trade inverse), Classic account: CONTRACT, SPOT
	wallet_balance = session.get_wallet_balance(accountType="UNIFIED") # , coin="BTC"
	for wlist in wallet_balance['result']['list']:
		atype = wlist['accountType']
		wallet = float(wlist['totalWalletBalance'])
		marginbalance = float(wlist['totalMarginBalance'])
		margininitial = 100 * ( float(wlist['totalInitialMargin']) / marginbalance )
		marginmaintenance = 100 * ( float(wlist['totalMaintenanceMargin']) / marginbalance )
		print(f"{atype} USDT: {round(wallet, 8)}")
		print(f"\tMRGN: {round(marginbalance, 2)}\n\t  НМ: {round(margininitial, 2)}%\n\t  МП: {round(marginmaintenance, 2)}%")
		for cbalance in wlist['coin']:
			coin = cbalance['coin']
			qty = float(cbalance['walletBalance'])
			usd = float(cbalance['usdValue'])
			locked = float(cbalance['locked'])
			if usd >= 0.01:
				print(f"\t\t{coin+':':<6} {qty:<12} LCK: {round(locked,8)}")

	# get SPOT orders
	spotords = session.get_open_orders(category="spot", settleCoin="USDT" )
	if spotords['result']['list']:
		print('SPOT:')
	for spot in spotords['result']['list']:
		ordid = str(spot['orderId'])
		side = side_colored(spot['side'])
		symbol = spot['symbol']
		otype = spot['orderType']
		price = float(spot['price'] or 0)
		qty = float(spot['qty'] or 0)
		val = price * qty
		# cretype = spot['createType']
		print(f"\t{side:4}: {symbol:10} USDT: {round(val,4):<10} QTY: {round(qty,4):<8} PRC: {round(price,4):<8} TYP: {otype}")

	# get POSITION orders
	positionords_arr = {}
	positionords = session.get_open_orders(category="linear", settleCoin="USDT" )
	for pos in positionords['result']['list']:
		ordid = str(pos['orderId'])
		side = side_colored(pos['side'])
		symbol = pos['symbol']
		otype = pos['orderType']
		price = float(pos['price'] or 0)
		sotype = pos['stopOrderType'] or otype
		triggerPrice = float(pos['triggerPrice'] or price)
		qty = float(pos['qty'] or 0)
		val = triggerPrice * qty
		# cretype = pos['createType']
		# lastPriceOnCreated = float(pos['lastPriceOnCreated'] or 0)
		# created = int(pos['createdTime'])
		# print(f"{side:4}:{symbol:10} USDT:{round(val,4):<8} QTY:{round(qty,4):<8} PRC:{round(triggerPrice,4):<8} TYP:{sotype}")
		if symbol not in positionords_arr:
			positionords_arr[symbol] = []
		positionords_arr[symbol].append(f"{side +':':5} {symbol:10} USDT: {round(val,4):<8} QTY: {round(qty,4):<8} PRC: {round(triggerPrice,4):<8} TYP: {sotype}")
	# GET PSITIONS, category: spot, linear, inverse, option
	positions = session.get_positions(category="linear", settleCoin="USDT") # , symbol="XAIUSDT"
	if positions['result']['list']:
		print('FUTURES:')
	for pos in positions['result']['list']:
		seq = str(pos['seq'])
		side = side_colored(pos['side'])
		symbol = pos['symbol']
		val = float(pos['positionValue'] or 0)
		mark = float(pos['markPrice'] or 0)
		pnl = pnl_colored(round(float(pos['unrealisedPnl'] or 0), 4))
		rpnl = float(pos['cumRealisedPnl'] or 0)
		tp = float(pos['takeProfit'] or 0)
		sl = float(pos['stopLoss'] or 0)
		liq = float(pos['liqPrice'] or 0)
		# created = int(pos['createdTime'])
		print(f"\t{side}: {symbol:10} USDT: {round(val,4):<8} PnL: {pnl} TP: {round(tp,2):<6} SL: {round(sl,2):<6} PRC: {round(mark,2):<6} LIQ: {round(liq,4)}")
		if symbol in positionords_arr:
			posorders = positionords_arr.pop(symbol)
			for po in posorders:
				print(f"\t\t{po}")
			print()
	if positionords_arr: # not all being printed
		print('FUTURES to open:')
		for symbol in positionords_arr:
			posorders = positionords_arr[symbol]
			for po in posorders:
				print(f"\t{po}")


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

# MORE ---
''' get kline
	session = HTTP()
	kline = session.get_kline(
		symbol="BTCUSDT",
		interval=15,
		limit=10
	) # list: [tstamp*1000, open, high, low, close, vol, turnover]
	for xline in kline['result']['list']:
		dt = datetime.fromtimestamp(int(xline[0])/1000)
		print(dt, xline[1:])
'''

''' get Server Time
	session = HTTP()
	server_time = session.get_server_time()
	timestamp = server_time['time'] / 1000
	dt = datetime.fromtimestamp(timestamp)
	print(f"{timestamp}: {dt}")
'''