#!/usr/bin/env python3
"""\
Trading Bot Config file
-- PLEAS EKEEP IT SECURE --
"""

__project__	= "Trading Bot - pybit"
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2024, musenko.com"
__license__	= "MIT"
__credits__	= ["Sergey Musenko"]
__date__	= "2024-01-10"
__version__	= "0.1"
__status__	= "dev"


# main config
sleep_time	= 15	# seconds
min_LIQ		= 30	# min % to liquidation (prc / liq)
min_PnL		= -8	# min PnL, in % of position val, negative means loss
min_Loss	= -10	# PnL loss to kill position, 0/False means ignore


# Bybit config -- PLEAS EKEEP IT SECURE! --
api_key		= 'key'
api_secret	= 'secret'


# notify via Telegram, bot: 
# Trading Monitor '@lightytrading_bot'
TMapiToken	= '' # '' means do not send
TMchatID	= '' # '' means DO NOT SEND


sign_buy	= '🟢'
sign_sell	= '🔴'
sign_alarm	= '⚠'
