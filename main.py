#!/usr/bin/env python3
"""\
Set of Trading Monitor Bots based using Pybit for Bybit Exchange
docs: https://bybit-exchange.github.io/docs/v5/intro

pip install pybit
"""

__project__	= "Trading Bot"
__part__	= 'Description'
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2024, musenko.com"
__license__	= "GPL"
__credits__	= ["Sergey Musenko"]
__date__	= "2024-01-18"
__version__	= "0.1"
__status__	= "dev"

from termcolor import colored

if __name__ == '__main__':
	print(f'''\
{colored("Set of Trading Monitor Bots based on Pybit for Bybit Exchange:", "light_yellow")}
\t- {colored("monitor-overview", "cyan")} - Account Balance and all Positions/Orders
\t- {colored("monitor-price", "cyan")}    - Price monitor Coin/USDT
\t- {colored("monitor-profit", "cyan")}   - P&L of all Positions and Spot Limit Orders
{colored("All bots could send Telegram notifications", "dark_grey")}\
''')

# that's all folks!

# MORE Pybit ---
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