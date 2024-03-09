#!/usr/bin/env python3
# Sysit Example: Create Postiton with TP/SL/TS
# docs: https://bybit-exchange.github.io/docs/v5/intro


from config_local import *
from termcolor import colored
from pybit.unified_trading import HTTP


symbol = "1000PEPEUSDT"
#####################
side       = 1		# 1=Buy, -1=Sell
posAmount  = 50		# full position amount
leverage   = 15		#
timeframe  = 1		# %% settings
#####################
marginMode = False	# 'ISOLATED_MARGIN'
limitPrice = False	# "0.0088602" # set False to use "Market" order
#####################

if timeframe == 1: # for 1 min timeframe:
	TPpercent = 2
	SLpercent = 1

elif timeframe == 5: # for 5 min timeframe:
	TPpercent = 4
	SLpercent = 1.2

elif timeframe == 15: # for 15 min timeframe:
	TPpercent = 9
	SLpercent = 3

else:
	print(f"Sorry, Timeframe '{timeframe}' not configured")
	exit(0)
#####################

color = 'light_green' if side > 0 else 'light_red'
side = 'Buy' if side > 0 else 'Sell'

print(colored(f'Bybit, Create Linear Order: {side} {symbol}', color))


# 0. connect Bybit
session = HTTP(api_key=api_key, api_secret=api_secret)


# 1. Set Margin mode ====================================================================
if marginMode:
	print(f'Set Margin mode: {marginMode}')
	try:
		res = session.set_margin_mode(
			setMarginMode = marginMode
		)
	except Exception as ex:
		print(ex)
		exit(0)


# 2. Set Leverage ====================================================================
print(f'Set Leverage: {leverage}')
try:
	res = session.set_leverage(
		category = "linear",
		symbol = symbol,
		buyLeverage = str(leverage),
		sellLeverage = str(leverage),
	)
except Exception as ex:
	if ex.status_code == 110043:
		print(f'\tleverage not modified')
	else:
		print(ex)
		exit(0)


# 3. Get Ticker Price ====================================================================
try:
	# get roundTo
	roundTo = 0 # round qty to
	instrument = session.get_instruments_info(
		category = "linear",
		symbol = symbol,
	)
	minOrderQty = instrument['result']['list'][0]['lotSizeFilter']['minOrderQty']
	if float(minOrderQty) < 1:
		roundTo = len(minOrderQty.replace('0.', ''))
	minQty = float(minOrderQty)

	# get current price
	priceRoundTo = 2
	if limitPrice:
		coinPrice = float(limitPrice)
	else:
		ticker = session.get_tickers(
			category = 'linear',
			symbol = symbol
		)
		coinPrice = ticker['result']['list'][0]['lastPrice']
		priceRoundTo = len(coinPrice.replace('0.', ''))
		coinPrice = float(coinPrice)

except Exception as e:
	print(f"\nError getting ticker {symbol}: {str(e)}\n")
	exit(0)

print(f"Get Instrument:\n\t{coinPrice=} (round={priceRoundTo})\n\t{minQty=}\n\tQTYround={roundTo}")


# 4. Create Order ====================================================================
if limitPrice:
	print(f'Create Order on Price={limitPrice}:')
else:
	print('Create Position on Market price:')

try:
	qty = int(posAmount / coinPrice) if roundTo <= 0 else round(posAmount / coinPrice, roundTo)
	if side == 'Buy':
		positionIdx = 1
		takeProfit = round(coinPrice * (1 + TPpercent/100), priceRoundTo)
		stopLoss = round(coinPrice * (1 - SLpercent/100), priceRoundTo)
		trailingActiv = round(coinPrice * (1 + TPpercent/100/2), priceRoundTo)
	else: # 'Sell'
		positionIdx = 2
		takeProfit = round(coinPrice * (1 - TPpercent/100), priceRoundTo)
		stopLoss = round(coinPrice * (1 + SLpercent/100), priceRoundTo)
		trailingActiv = round(coinPrice * (1 - TPpercent/100/2), priceRoundTo)
	trailingStop = round(abs(coinPrice - stopLoss), priceRoundTo)

	print(f"\t{symbol=}\n\t{side=}\n\t{qty=}\n\t{coinPrice=}\n\t{posAmount=}\n\t{takeProfit=}\n\t{stopLoss=}")
#	exit(0)
	res = session.place_order(
		category = "linear",
		symbol = symbol,
		orderType = "Limit" if limitPrice else "Market",
		price = str(limitPrice),
		side = side,
		positionIdx = positionIdx, # 0: one way, 1: hedge-Buy, 2: hedge-Sell
		qty = str(qty), # Perps/Futures/Option always use base coin as unit
		takeProfit = str(takeProfit),
		stopLoss = str(stopLoss),
	)
	if res['retCode'] != 0:
		print(res)

	# ...and set Trailing stop ==============================================================
	if limitPrice:
		exit(0) # TS not available for Limit order
	else:
		print(f"Set Trailing Stop:\n\tdistance={trailingStop:f}\n\tactiveate={trailingActiv}")
	res = session.set_trading_stop(
		category = "linear",
		symbol = symbol,
		positionIdx = positionIdx,
		trailingStop = str(trailingStop),
		activePrice = str(trailingActiv),
	)
	if res['retCode'] != 0:
		print(res)

except Exception as ex:
	print(ex)

# that's all folks!
