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

symbol = 'DOGE'
interval = 1
klinesJson = f'{symbol}USDT_{interval}.json'
klineNames = ['startTime', 'openPrice', 'highPrice', 'lowPrice', 'closePrice', 'volume', 'turnover']
SMA1len = 8 # 30
SMA2len = 32 # 100


# fine print mouse coordinates
def format_coord(x, y):
	x = int(x)
	if x not in range(len(klines)):
		return ''
	return f"{klines['datetime'].iloc[int(x)]} : {y:8.06f}"


# check and mark SMA cross
def crossSMA(df, SMA1, SMA2):
	buy_signal = []
	sell_signal = []
	FLAG = 0
	FLAGcount = 0
	for i in range(len(df)):

		if df[SMA1][i] > df[SMA2][i]: # короткая пересекает длинную СНИЗУ ВВВЕРХ
			if FLAG != 1:
				buy_signal.append(df['closePrice'][i] if FLAGcount else np.nan)
				sell_signal.append(np.nan)
				FLAG = 1
				FLAGcount += 1
			else:
				buy_signal.append(np.nan)
				sell_signal.append(np.nan)

		elif df[SMA1][i] < df[SMA2][i]: # короткая пересекает длинную СВЕРХУ ВНИЗ
			if FLAG != -1:
				buy_signal.append(np.nan)
				sell_signal.append(df['closePrice'][i] if FLAGcount else np.nan)
				FLAG = -1
				FLAGcount += 1
			else:
				buy_signal.append(np.nan)
				sell_signal.append(np.nan)

		else:
				buy_signal.append(np.nan)
				sell_signal.append(np.nan)

	return(buy_signal, sell_signal)


# get preloaded klines JSON
try:
	klines = pd.read_json(klinesJson)
#	with open(klinesJson, "r", encoding='utf-8-sig') as infile: klines = pd.read_json(infile)
except Exception:
	print('Read JSON to Pandas failed')
	exit(0)
klines.columns = klineNames
klines['datetime'] = pd.to_datetime(klines['startTime'], unit='s') # .dt.time
# initial data ready

# base graph style: print(plt.style.available)
plt.style.use('dark_background') # 'seaborn-v0_8-darkgrid') #'fivethirtyeight')
for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']: 
	plt.rcParams[param] = '#212946'  # bluish dark grey
for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
	plt.rcParams[param] = '0.9'  # very light grey
plt.rcParams.update({"axes.grid" : True, "grid.color": "#444455"})
fig = plt.figure(figsize=(12, 8), label=f"{symbol}USDT")

# Symbol plot
plt.plot(klines['closePrice'], label=symbol, linewidth=1, color='#00ff55', alpha=0.5)
#plt.xticks(klines.index, klines['datetime'].values, rotation=45, fontsize=9)
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=60))
plt.xlabel('Date')
plt.ylabel('USDT')

# SMA1 calc and plot
klines[f"SMA{SMA1len}"] = klines['closePrice'].rolling(window=SMA1len).mean()
plt.plot(klines[f"SMA{SMA1len}"], label=f"SMA{SMA1len}", linewidth=1, color='#aa00ff')

# SMA2 calc and plot
klines[f"SMA{SMA2len}"] = klines['closePrice'].rolling(window=SMA2len).mean()
plt.plot(klines[f"SMA{SMA2len}"], label=f"SMA{SMA2len}", linewidth=1, color='#00ffff')

# calc cross SMA1/SMA2 ---------------------
tmp = crossSMA(klines, f"SMA{SMA1len}", f"SMA{SMA2len}")
klines['buy'] = tmp[0]
klines['sell'] = tmp[1]
plt.scatter(klines.index, klines['buy'], label="Buy", color='#00ff55', marker='^')
plt.scatter(klines.index, klines['sell'], label="Sell", color='#ff5500', marker='v')


plt.gca().format_coord = format_coord # show mouse coordinates
plt.legend(loc=('upper left'))
plt.tight_layout()
# all done
plt.get_current_fig_manager().full_screen_toggle()
plt.show()


#def onclick(event):
#	x = int(event.xdata)
#	y = event.ydata
#	print (f'x = {x}, y = {y}')
#	return [x, y]
#fig.canvas.mpl_connect('button_press_event', onclick)
