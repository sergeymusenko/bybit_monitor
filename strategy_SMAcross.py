#!/usr/bin/env python3
# see: https://www.youtube.com/watch?v=W8rzwhcMS9Y
# Стратегия с 2 скользящими средними в Python | Algorithmic Trading
# pip install matplotlib

#import datetime as dt
#from time import sleep
#from ansictrls import *
#import statistics
#from pybit.unified_trading import HTTP

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

symbol = '1000PEPE'
klinesJson = f'{symbol}USDT_kline.json'
klineNames = ['startTime', 'openPrice', 'highPrice', 'lowPrice', 'closePrice', 'volume', 'turnover']

# get preloaded klines JSON
try:
	klines = pd.read_json(klinesJson)
#	with open(klinesJson, "r", encoding='utf-8-sig') as infile: klines = pd.read_json(infile)
except Exception:
	print('Read JSON to Pandas failed')
	exit(0)
klines.columns = klineNames
klines['datetime'] = pd.to_datetime(klines['startTime'], unit='s') # .dt.time
#print(klines)
# initial data ready

# base graph style
#print(plt.style.available)
plt.style.use('dark_background') # 'seaborn-v0_8-darkgrid') #'fivethirtyeight')
for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']: 
	plt.rcParams[param] = '#212946'  # bluish dark grey
for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
	plt.rcParams[param] = '0.9'  # very light grey
plt.rcParams.update({"axes.grid" : True, "grid.color": "#444455"})
fig = plt.figure(figsize=(12, 8))

# Symbol plot
plt.plot(klines['closePrice'], label=symbol, linewidth=1, color='#00aa00', alpha=0.5)
#plt.xticks(klines.index, klines['datetime'].values, rotation=45, fontsize=9)
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=60))
plt.xlabel('Date')
plt.ylabel('USDT')

# SMA30
SMA1len = 30
SMA1 = pd.DataFrame()
SMA1['close'] = klines['closePrice'].rolling(window=SMA1len).mean()
plt.plot(SMA1['close'], label=f"SMA{SMA1len}", linewidth=1, color='#aa00ff')

# SMA100
SMA2len = 100
SMA2 = pd.DataFrame()
SMA2['close'] = klines['closePrice'].rolling(window=SMA2len).mean()
plt.plot(SMA2['close'], label=f"SMA{SMA2len}", linewidth=1, color='#00ffff')

# cross SMA

# show mouse coordinates
plt.gca().format_coord = lambda x, y: f"{klines['datetime'].iloc[int(x)]} : {y:8.06f}"

plt.legend(loc=('upper left'))
# all done
plt.show()

#def onclick(event):
#	x = int(event.xdata)
#	y = event.ydata
#	print (f'x = {x}, y = {y}')
#	return [x, y]
#fig.canvas.mpl_connect('button_press_event', onclick)
