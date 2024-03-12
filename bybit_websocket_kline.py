#!/usr/bin/env python3
# p1:	https://www.youtube.com/watch?v=8SY-G0Hk64Y
# p2:	https://www.youtube.com/watch?v=5oZvSWKGyFU
# docs:	https://bybit-exchange.github.io/docs/v5/websocket/public/ticker

from config_local import *
from termcolor import colored
from ansictrls import *
from time import sleep
from datetime import datetime, timedelta
from pybit.unified_trading import WebSocket

interval = 1
printBuffer = { # limit by Pybit: 10 symbols; but you can subscribe more if use more ticker_stream() calls
	"BTCUSDT":'',
	"ETHUSDT":'',
	"ATOMUSDT":'',
	"DYDXUSDT":'',
	"OPUSDT":'',
	"DOTUSDT":'',
	"1000PEPEUSDT":'',
}

# print several lines
def print_out(up=True):
	lines = len(printBuffer)
	if up and lines > 1: print_ANSIctrl('CPL', lines)
	i = 1
	for line in printBuffer:
		print(get_ANSIctrl('EL') + f"{i}. " + printBuffer[line])
		i += 1

color = None

def handle_message(message):
	global lastPriceSave, color
	start = int(message['data'][0]['start'])
	dt = datetime.fromtimestamp(int(start/1000))
	symbol = message['topic'].replace(f"kline.{interval}.", '')
	opn = float(message['data'][0]['open'])
	cls = float(message['data'][0]['close']) # final price?
	hig = float(message['data'][0]['high'])
	low = float(message['data'][0]['low'])
	vol = float(message['data'][0]['volume'])
	trn = float(message['data'][0]['turnover'])
	# print out
	delta = cls - opn
	color = 'red' if delta < 0 else "green" if delta > 0 else None
	sy = symbol.replace('1000', '').lstrip('0')
	printBuffer[symbol] = f"{dt} {colored(f'{sy:12}', color)} O:{opn:<8.02f} C:{cls:<8.02f} H:{hig:<8.02f} L:{low:<8.02f} V:{vol:<8.02f}"

# create websocket
try:
	ws = WebSocket(
		testnet = False,
		channel_type = "linear",
	)
except Exception:
	print('Connection failed')
	exit(0)

# publick/ticker
ws.kline_stream(
	interval = interval, # 1 3 5 15 30 60 120 240 360 720 D W M
    symbol = printBuffer.keys(),
    callback = handle_message
)

print_ANSIctrl('HCU')
print('kline_stream:')

print_out(False)

while True:
	try:
		sleep(0.5)
		print_out()
	except KeyboardInterrupt: # exit on Ctrl+C
		print("\rBye...")
		print_ANSIctrl('SCU')
		break
