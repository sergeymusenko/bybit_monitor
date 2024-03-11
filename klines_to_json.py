#!/usr/bin/env python3
# Bybit: get klines and store to json file
# kline headers: 'startTime','openPrice','highPrice','lowPrice','closePrice','volume','turnover'
# docs: https://bybit-exchange.github.io/docs/v5/intro

import datetime as dt
import json
from pybit.unified_trading import HTTP
console_CEOL = '\033[2K'

symbol = 'DOGEUSDT'
startDate = '2024-03-11 00:00:00'
interval = 1 # 1,3,5,15,30,60,120,240,360,720,D,M,W
getNlines = 1440 # number of lines of type 'interval'

linesLimit = 1000 # no more then 1000, API limit: [1, 1000]
start = int(dt.datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S').timestamp())

print(f"{symbol}: {start=}, {getNlines=}, {linesLimit=}")


session = HTTP()

klistBuffer = []
print('loading', end='', flush=True)
while getNlines > 0:
	print('.', end='', flush=True)
	klist = session.get_kline(
		category='linear',
		symbol=symbol,
		start=start * 1000,
		interval=interval,
		limit=min(linesLimit, getNlines)
	).get('result', None).get('list', None)
	if not klist:
		break
	# from old to new
	klist.reverse()
	#	replace timestamp with date time
	for i in range(len(klist)):
		klist[i][0] = str(dt.datetime.fromtimestamp(int(klist[i][0])/1000))
	start += linesLimit * interval * 60
	klistBuffer += klist
	getNlines -= linesLimit


print(f"\r{console_CEOL}Done, klines number: {len(klistBuffer)}")

jsonObj = json.dumps(klistBuffer).replace("], [","],\n[")
filename = f'{symbol}_klines.json'
with open(filename, "w") as outfile:
	outfile.write(jsonObj)
	print(f"Saved to file: {filename}")
