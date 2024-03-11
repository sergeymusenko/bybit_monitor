#!/usr/bin/env python3
# p1:	https://www.youtube.com/watch?v=8SY-G0Hk64Y
# p2:	https://www.youtube.com/watch?v=5oZvSWKGyFU
# docs:	https://bybit-exchange.github.io/docs/v5/websocket/public/ticker

from config_local import *
from termcolor import colored
from time import sleep
from datetime import datetime, timedelta
from pybit.unified_trading import WebSocket
console_CEOL = '\033[2K'
console_UP = '\033[2A'

printBuffer = { # limit by Pybit: 10 symbols; but you can subscribe more if use more ticker_stream() calls
	"BTCUSDT":'',
	"ETHUSDT":'',
	"ATOMUSDT":'',
	"DYDXUSDT":'',
	"OPUSDT":'',
	"DOTUSDT":'',
}

# print several lines
def print_out(up=True):
	lines = len(printBuffer)
	while up and lines > 0:
		print(console_UP)
		lines -= 1
	i = 1
	for line in printBuffer:
		print(f"{console_CEOL}{i}. " + printBuffer[line])
		i += 1

lastPriceSave = {}
color = None

def handle_message(message):
	global lastPriceSave, color
	ts = int(message['ts'])
	symbol = message['data']['symbol']
	lastPrice = float(message['data']['lastPrice'])
	markPrice = float(message['data']['markPrice'])
	openInterest = float(message['data']['openInterest'])
	fundingRate = float(message['data']['fundingRate'])
	nextFundingTime = float(message['data']['nextFundingTime'])
	openInterest = float(message['data']['openInterest'])
	# print out
	dt = datetime.fromtimestamp(int(ts/1000))
	price = f"{lastPrice:<10.4f}"
	if symbol in lastPriceSave:
		delta = lastPriceSave[symbol] - lastPrice
		color = 'red' if delta < 0 else "green" if delta > 0 else None
	lastPriceSave[symbol] = lastPrice
	funding = round(fundingRate * 100, 4)
	tofunding = timedelta(seconds = int((nextFundingTime - ts)/1000))
	printBuffer[symbol] = f"{symbol:10} PRC: {colored(price, color)}  OI: {openInterest:<12.2f}  ⚡ {funding:6.04f}% / {tofunding}"
	# print_out() # not here

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
ws.ticker_stream(
    symbol = printBuffer.keys(),
    callback = handle_message
)

print('ticker_stream:')
print_out(False)
while True:
	try:
		sleep(0.5)
		print_out()
	except KeyboardInterrupt: # exit on Ctrl+C
		print("\rBye...")
		break
