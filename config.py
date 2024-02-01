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


sleep_time = 60 # seconds
min_PnL = -5 # min PnL, in % of position val
check_spot = False

sign_buy  = '🟢'
sign_sell = '🔴'
sign_alarm = '⚠'


# Bybit config -- PLEAS EKEEP IT SECURE! --
api_key = 'key'
api_secret = 'secret'


# notify via Telegram, bot: 
TMapiToken = '' # '' means do not send
TMchatID = '' # '' means DO NOT SEND
