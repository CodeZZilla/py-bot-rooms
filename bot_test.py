import telebot
import time
import json
import api
import keyboards
import utils
import status
import generator_telegraph
from threading import Thread
import schedule
from telebot.util import async_dec
from telebot.types import InputMediaPhoto, LabeledPrice, ShippingOption, ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

tokens = json.load(open('tokens.json', encoding='utf-8'))
TELEGRAM_TOKEN = tokens['TELEGRAM_TOKEN']
tranzzo_token = tokens['TRANZZO_TOKEN']

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    if api.check_user(message):
        user = api.get_user(chat_id)
        bot.send_message(chat_id, 'asdassadasdasd')
    else:
        api.create_user(message)
        keyboards.language_keyboard(bot, chat_id)


print('Listening....')
count_restarts = 0
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as error:
        count_restarts = count_restarts + 1
        print(f'count_restarts = {count_restarts} ({error})')
        time.sleep(1)