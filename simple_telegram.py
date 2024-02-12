#!/usr/bin/env python3
# by www.ShellHacks.com
'''\
simple_telegram.py - Super simple Telegram message sender

see: https://psujit775.medium.com/ihow-to-send-telegram-message-with-python-e826b94f1d9b
note: it does not support buttons!
'''

__project__	= "Lotteries Results Scrapper"
__part__	= 'Telegram notifier'
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__license__	= "MIT"
__copyright__= "© 2024, musenko.com"
__credits__	= ["Sergey Musenko"]
__date__	= "2024-01-15"
__version__	= "0.1"

__instructions__ = '''
Create a Telegram bot
1. Open the Telegram app on your smartphone or desktop.
2. Search for the "@BotFather" username in the search bar.
3. Click on the “Start” button to start a conversation with the BotFather.
4. Type "/newbot" and follow the prompts to create a new bot.
   The BotFather will give you an API key that you will use in the next step.
5. Type "/setuserpic"
6. Get chadID,open:
	https://api.telegram.org/bot<apiToken>/getUpdates
	and type spmething in a chat window
	see JSON, get "id:..."
* User must open the chat bot FIRST or he will never get a message
* To get group ID: https://t.me/username_to_id_bot
'''

import requests
import time

def send_to_telegram(apiToken, chatID, message='', mode='HTML', print_exception=True):
	if not apiToken or not chatID or not message:
		return False
	try:
		apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
		response = requests.post(apiURL, json={'chat_id':chatID, 'text':message, 'parse_mode':mode})
		return response
	except Exception as e:
		if print_exception:
			print(e)


if __name__ == '__main__':
	print(f'{__project__}. {__part__}')
	print(__instructions__)


'''
More instructions
Use a library to send image, document or video:

Install the python-telegram-bot library/ Open a terminal and enter the following command:
	pip install python-telegram-bot

Then
	import telegram
	apiToken = '...'
	chatID = '...'
	bot = telegram.Bot(token=apiToken)

	# Send a message:
	bot.send_message(chat_id=chatID, text='Hello, World!')

	# To send an Image:
	bot.send_photo(chat_id=chatID, photo=open('/path/to/photo.jpg', 'rb'))

	# To send an document:
	bot.send_document(chat_id=chatID, document=open('/path/to/document.pdf', 'rb'))

	# To send and video:
	bot.send_video(chat_id=chatID, video=open('/path/to/video.mp4', 'rb'))
'''