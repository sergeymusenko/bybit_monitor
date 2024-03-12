#!/usr/bin/env python3
# Bybit: get klines and store to json file
# kline headers: 'startTime','openPrice','highPrice','lowPrice','closePrice','volume','turnover'
# docs: https://bybit-exchange.github.io/docs/v5/intro

import datetime as dt
from time import sleep
import json
from ansictrls import *
from pybit.unified_trading import HTTP

symbol = 'DOGEUSDT'
interval = 1 # 1,3,5,15,30,60,120,240,360,720,D,M,W
getLastHours = 3 * 24 # get last N hours
linesLimit = 1000 # data frame size, no more then 1000! API limit: [1, 1000]

# prepare
intervalSec = interval * 60
getNlines = int(getLastHours * 3600 / intervalSec) # number of lines of type 'interval'
now = intervalSec * int(dt.datetime.now().timestamp() / intervalSec) # 'interval' start
start = now - getLastHours * 3600

if __name__ == '__main__':
	print(f"{symbol}: {start=}, {now=}, {getNlines=}, {linesLimit=}")

	# get data by frames
	session = HTTP()
	klineBuffer = []
	print('loading', end='', flush=True)
	frames = 0
	while getNlines > 0:
		print('.', end='', flush=True)
		# get data frame
		kline = session.get_kline(
			category='linear',
			symbol=symbol,
			start=start * 1000, # ms needed
			interval=interval,
			limit=min(linesLimit, getNlines)
		).get('result', None).get('list', None)
		if not kline:
			break
		# sort from old to new
		kline.reverse()
		#	replace timestamp with date time
		for i in range(len(kline)):
			kline[i][0] = str(dt.datetime.fromtimestamp(int(kline[i][0])/1000))
		klineBuffer += kline
		# next frame
		start += linesLimit * intervalSec
		getNlines -= linesLimit
		frames += 1
		sleep(0.1)

	print(f"\r{get_ANSIctrl('EL')}Done, kline number: {len(klineBuffer)}, {frames=}")

	# save to file
	jsonObj = json.dumps(klineBuffer).replace("], [","],\n[")
	filename = f'{symbol}_kline.json'
	with open(filename, "w") as outfile:
		outfile.write(jsonObj)
		print(f"Saved to file: {filename}")
