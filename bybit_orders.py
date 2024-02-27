#!/usr/bin/env python3
#
# 1. Set Leverage
# 2. Place Position Order
# 3. Set TP/SL for Position
# 4. Clear TP/SL for Position
# 5. Close Position
# 6. Get POSITIONS
# 7. Get POSITION ORDERS (Limit, TP, SL)

from config_local import *
from termcolor import colored
from pybit.unified_trading import HTTP


session = HTTP(api_key=api_key, api_secret=api_secret)


# 1. Set Leverage ====================================================================
if False:
	symbol = "1000PEPEUSDT"
	leverage = 10
	try:
		res = session.set_leverage(
			category="linear",
			symbol=symbol,
			buyLeverage=str(leverage),
			sellLeverage=str(leverage),
		)
		print(res)
	except Exception as ex:
		if ex.status_code == 110043:
			print(f'{symbol} set leverage {leverage}: leverage not modified')
		else:
			print(ex)
	exit(0)


# 2. Place Order Position ============================================================
if False:
	symbol = "1000PEPEUSDT" # min 100 1000PEPE, > $0.3
	try:
		res = session.place_order(
			category="linear",
			symbol=symbol,
			side="Sell",
			positionIdx=2, # 0: one way, 1: hedge-Buy, 2: hedge-Sell
			qty="100", # Perps/Futures/Option always use base coin as unit
#			marketUnit='quoteCoin', # for QTY in USDT
			orderType="Market",
#			orderType="Limit",
#			price="0.002",
#			takeProfit="0.0028",
#			stopLoss="0.0024",
#			orderLinkId="lighty-futures-test-002",
		)
		print(res)
	except Exception as ex:
		print(ex)
	exit(0)


# 3. Set TP/SL for Position ==========================================================
if False:
	symbol = "1000PEPEUSDT" # min 100 1000PEPE, > $0.3
	try:
		res = session.set_trading_stop(
			category="linear",
			symbol=symbol,
			positionIdx=2, # 0: one way, 1: hedge-Buy, 2: hedge-Sell
			takeProfit="0.0022",
			stopLoss="0.0025248",
		)
		print(res)
	except Exception as ex:
		if ex.status_code == 34040:
			print(f'{symbol} position not modified')
		else:
			print(ex)
	exit(0)


# 4. Clear TP/SL for Position ========================================================
if False:
	symbol = "1000PEPEUSDT" # min 100 1000PEPE, > $0.3
	try:
		res = session.set_trading_stop(
			category="linear",
			symbol=symbol,
			positionIdx=2, # 0: one way, 1: hedge-Buy, 2: hedge-Sell
			takeProfit="0",
			stopLoss="0",
		)
		print(res)
	except Exception as ex:
		if ex.status_code == 34040:
			print(f'{symbol} position not modified')
		else:
			print(ex)
	exit(0)


# 5. Close Position ==================================================================
# "side" must be in OPPOSITE to current position
# "positionIdx" must be SAME as current position
if False:
	symbol = "1000PEPEUSDT" # min 100 1000PEPE, > $0.3
	try:
		res = session.place_order(
			category="linear",
			symbol=symbol,
			side="Buy",
			positionIdx=2, # 0: one way, 1: hedge-Buy, 2: hedge-Sell
			orderType="Market",
			qty="0",
			reduceOnly=True,
		)
		print(res)
	except Exception as ex:
		if ex.status_code == 110017:
			print(f'{symbol} position not found')
		else:
			print(ex)
	exit(0)


# 6. Get POSITIONS (category: spot, linear, inverse, option) =========================
try:
	print(colored('\nget_positions:', 'light_yellow'))
	positions = session.get_positions(category="linear", settleCoin="USDT") # , symbol="XAIUSDT"
	i = 1
	for ordr in positions['result']['list']:
		print(f"  {i:2}. {ordr['side']:4} {ordr['symbol']:8}, PnL: {float(ordr['unrealisedPnl']):<7.02f} VAL: {float(ordr['positionValue']):<7.02f} PRC: {float(ordr['markPrice']):<7.02f}")
		i += 1
except Exception:
	print('Sorry, get_positions error')
'''
session.get_positions: {
'list': [{
	'symbol': 'DYDXUSDT',
	'side': 'Buy',
	'size': '1.1',
	'positionValue': '3.8709',
	'leverage': '10',
	'avgPrice': '3.519',
	'markPrice': '3.488',
	'liqPrice': '',
	'takeProfit': '',
	'stopLoss': '',
	'unrealisedPnl': '-0.0341',
	'cumRealisedPnl': '-38.5944848',
	'positionMM': '0.0406251',
	'positionIM': '0.3890061',
	'createdTime': '1701376414159',
	'updatedTime': '1709042419948',
	'seq': 84054581654,
	'autoAddMargin': 0,'riskId': 611,'riskLimitValue': '200000','isReduceOnly': False,'tpslMode': 'Full','trailingStop': '0','adlRankIndicator': 2,'positionIdx': 1,'bustPrice': '','positionBalance': '0','leverageSysUpdatedTime': '','positionStatus': 'Normal','mmrSysUpdatedTime': '','tradeMode': 0
}]
'''


# 7. Get POSITION ORDERS (Limit, TP, SL) =============================================
try:
	print(colored('\nget_open_orders:', 'light_yellow'))
	ords2print = []
	positionords = session.get_open_orders(category="linear", settleCoin="USDT")
	for ordr in positionords['result']['list']:
		prc = float(ordr['triggerPrice'] if ordr['triggerPrice'] else ordr['price'])
		ords2print.append([
			ordr['symbol'] + str(prc),
			f"{ordr['side']:4} {ordr['symbol']:8} {ordr['orderType']:6} {ordr['createType'].replace('CreateBy', ''):12} QTY: {ordr['qty']:<7} PRC: {prc:<7.02f}",
			ordr['symbol']
		])
	ords2print.sort(key=lambda x: x[0], reverse=True)
	i = 1
	cursymb = ''
	for ordr in ords2print:
		if cursymb and cursymb != ordr[2]: print()
		print(f"  {i:2}.", ordr[1])
		i += 1
		cursymb = ordr[2]
except Exception:
	print('Sorry, get_open_orders error')
'''
'list': [{
	'orderType': 'Limit',
	'symbol': 'AAVEUSDT',
	'side': 'Buy',
	'qty': '0.58',
	'price': '103.15',
	'lastPriceOnCreated': '103.37',
	'createType': 'CreateByUser',
	'closeOnTrigger': False,
	'triggerPrice': '',
	'triggerDirection': 0,
	'orderStatus': 'New',
	'createdTime': '1709044834245',
	'updatedTime': '1709046742412',
	'orderId': '82297a1f-3079-47fb-bc21-8067d6e10e42',
	'leavesQty': '0.58',
	'leavesValue': '59.827',
	'orderLinkId': '','slLimitPrice': '0','cancelType': 'UNKNOWN','avgPrice': '','stopOrderType': '','takeProfit': '','cumExecValue': '0','tpslMode': '','smpType': 'None','blockTradeId': '','isLeverage': '','rejectReason': 'EC_NoError','orderIv': '','tpTriggerBy': '','positionIdx': 1,'timeInForce': 'GTC','smpGroup': 0,'tpLimitPrice': '0','cumExecFee': '0','slTriggerBy': '','placeType': '','cumExecQty': '0','reduceOnly': False,'stopLoss': '','marketUnit': '','smpOrderId': '','triggerBy': ''
}, {
	'orderType': 'Market',
	'symbol': 'AAVEUSDT',
	'side': 'Sell',
	'qty': '0.28',
	'createType': 'CreateByTakeProfit',
	'closeOnTrigger': True,
	'triggerPrice': '110',
	'triggerDirection': 1,
	'orderStatus': 'Untriggered',
	'lastPriceOnCreated': '104.63',
	'createdTime': '1709044810283',
	'updatedTime': '1709044810283',
	'orderId': '82a3bb7a-a27d-473e-9f82-1832874463f7',
	'leavesQty': '0.28',
	'leavesValue': '0',
	'avgPrice': '','cancelType': 'UNKNOWN','placeType': '','cumExecFee': '0','cumExecQty': '0','cumExecValue': '0','isLeverage': '','marketUnit': '','orderIv': '','orderLinkId': '','positionIdx': 1,'timeInForce': 'IOC','price': '0','reduceOnly': True,'rejectReason': 'EC_NoError','slLimitPrice': '0','slTriggerBy': '','smpGroup': 0,'smpOrderId': '','smpType': 'None','stopLoss': '','stopOrderType': 'TakeProfit','takeProfit': '','tpLimitPrice': '0','tpslMode': 'Full','tpTriggerBy': '','triggerBy': 'LastPrice','blockTradeId': '',
]
'''

# that's all folks!
