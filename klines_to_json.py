#!/usr/bin/env python3
# Bybit: get klines and store to json file
# kline headers: 'startTime','openPrice','highPrice','lowPrice','closePrice','volume','turnover' + 'datetime'
# docs: https://bybit-exchange.github.io/docs/v5/intro

import datetime as dt
from time import sleep
import json
from ansictrls import *
import statistics
from pybit.unified_trading import HTTP

symbol = '1000PEPEUSDT'
interval = 1 # 1,3,5,15,30,60,120,240,360,720,D,M,W
getLastHours = 2 # get last N hours
linesLimit = 1000 # data frame size, no more then 1000! API limit: [1, 1000]

SMA1len = 30
SMA2len = 100
EMA1len = 9
EMA2len = 20 # use it for KC and ATR
BBlen   = 20 # length for Bollinger Bands

ATRlen = EMA2len
KClen = EMA2len

klineHeaders = [
	'startTime', # 0
	'openPrice', # 1
	'highPrice', # 2
	'lowPrice',  # 3
	'closePrice',# 4
	'volume',    # 5
	'turnover',  # 6 \- from API
	'datetime',  # 7 /- additions
	'SMA1',      # 8
	'SMA2',      # 9
	'EMA1',      # 10
	'EMA2',      # 11
	'ATR',       # 12
	'KC',        # 13 as [l,m,u]
	'BB',        # 14 as [l,m,u]
]

if __name__ == '__main__':
	# prepare
	intervalSec = interval * 60
	getNlines = int(getLastHours * 3600 / intervalSec) # number of lines of type 'interval'
	now = intervalSec * int(dt.datetime.now().timestamp() / intervalSec) # 'interval' start
	start = now - getLastHours * 3600

	print(f"{symbol}: {start=}, {now=}, {getNlines=}, {linesLimit=}")

	# get data by frames
	klineBuffer = []
	print('loading', end='', flush=True)
	frames = 0
	roundPrice = 0
	SMAbuf = [] # collect 1 buffer for all calculations, just get N last values
	SMAbufLen = max(SMA1len, SMA2len, EMA1len, EMA2len)
	EMA1prev = 0
	EMA2prev = 0
	EMA1k = 2 / (EMA1len + 1)
	EMA2k = 2 / (EMA2len + 1)
	closePricePrev = 0
	TRbuf = []
	session = HTTP()
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
		# replace timestamp with date time and str->float
		for kl in kline:
			cp = kl[4] # save closePrice as str value
			if '.' in cp:
				roundPrice = max(len(cp.split('.')[1]), roundPrice)
			# make source vals as float
			tmp = list(map(float, kl))
			tmp[0] = int(tmp[0]/1000) # timestamp is int
			# save datetime as string as [7]
			tmp.append(str(dt.datetime.fromtimestamp(tmp[0])))
			# save kline
			klineBuffer.append(tmp)
		del kline

		# next frame
		start += linesLimit * intervalSec
		getNlines -= linesLimit
		frames += 1
		sleep(0.1)

	# klineBuffer is loaded, ADD INDICATORS!
	for i in range(len(klineBuffer)):
		tmp = klineBuffer[i]

		# current prices
		highPrice = tmp[2]
		lowPrice = tmp[3]
		closePrice = tmp[4]
		if not closePricePrev: closePricePrev = closePrice # 1st entry

		# collect SMA data
		if len(SMAbuf) >= SMAbufLen: # keep 'n' last elements in list
			SMAbuf.pop(0)
		SMAbuf.append(closePrice)

		# make SMA1
		xLen = min(len(SMAbuf), SMA1len)
		SMA1val = round(statistics.fmean(SMAbuf[-xLen:]), roundPrice)
		tmp.append(SMA1val)

		# make SMA2
		xLen = min(len(SMAbuf), SMA2len)
		SMA2val = round(statistics.fmean(SMAbuf[-xLen:]), roundPrice)
		tmp.append(SMA2val)

		# make EMA1
		if len(SMAbuf) < EMA1len:
			EMA1val = round(statistics.fmean(SMAbuf), roundPrice)
		else:
			EMA1val = closePrice * EMA1k + EMA1prev * (1 - EMA1k)
		EMA1prev = EMA1val
		tmp.append(round(EMA1val, roundPrice))

		# make EMA2
		if len(SMAbuf) < EMA2len:
			EMA2val = round(statistics.fmean(SMAbuf), roundPrice)
		else:
			EMA2val = closePrice * EMA2k + EMA2prev * (1 - EMA2k)
		EMA2prev = EMA2val
		tmp.append(round(EMA2val, roundPrice))

		# make ATR
		TR = max(abs(highPrice - lowPrice), abs(highPrice - closePricePrev), abs(lowPrice - closePricePrev))
		if len(TRbuf) >= ATRlen:
			TRbuf.pop(0)
		TRbuf.append(TR)
		ATRval = statistics.fmean(TRbuf)
		closePricePrev = closePrice
		tmp.append(round(ATRval, roundPrice))

		# make Keltner Channel
		kcMiddle = round(EMA2val, roundPrice)
		kcLower = round(EMA2val - 2 * ATRval, roundPrice)
		kcUpper = round(EMA2val + 2 * ATRval, roundPrice)
		tmp.append([kcLower, kcMiddle, kcUpper])

		# make Bollinger Bands
		if len(SMAbuf) <= 2:
			tmp.append([closePrice, closePrice, closePrice])
		else:
			xLen = min(len(SMAbuf), BBlen)
			bbSMAmiddle = round(statistics.fmean(SMAbuf[-xLen:]), roundPrice)
			bbStdDev = 2 * statistics.stdev(SMAbuf[-xLen:])
			bbSMAlower = round(bbSMAmiddle - bbStdDev, roundPrice)
			bbSMAupper = round(bbSMAmiddle + bbStdDev, roundPrice)
			tmp.append([bbSMAlower, bbSMAmiddle, bbSMAupper])

		# save indicators
		tmp.append('NL')
		klineBuffer[i] = tmp

	print(f"\r{get_ANSIctrl('EL')}Done, kline number: {len(klineBuffer)}, {frames=}")

	# save to file
	jsonObj = json.dumps(klineBuffer).replace(', "NL"], ',"],\n").replace(', "NL"]',"]")
	filename = f'{symbol}_kline.json'
	with open(filename, "w") as outfile:
		outfile.write(jsonObj)
		print(f"Saved to file: {filename}")
