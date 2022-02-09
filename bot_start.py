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

TIME_SLEEP = 3

bot = telebot.TeleBot(TELEGRAM_TOKEN)

sticker_start = 'CAACAgUAAxkBAAP-X0qNH1rpyoDqT7odr43p9nZntwkAAm8DAALpCsgDr86-2QK6XXQbBA'

messages = json.load(open('./static/messages_v2.json', encoding='utf-8'))
cities = json.load(open('./static/cities.json', encoding='utf-8'))
services = json.load(open('./static/services.json', encoding='utf-8'))
rooms = json.load(open('./static/rooms.json', encoding='utf-8'))
regions = json.load(open('./static/regions.json', encoding='utf-8'))


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    if api.check_user(message):
        user = api.get_user(chat_id)
        bot.send_sticker(chat_id, sticker_start)
        bot.send_message(chat_id, messages['messages']['start_registered'][user['language']])
        keyboards.main_menu(bot, chat_id)
    else:
        api.create_user(message)
        keyboards.language_keyboard(bot, chat_id)


@bot.message_handler(commands=['language'])
def language_command(message):
    keyboards.language_keyboard(bot, message.chat.id)


@bot.message_handler(commands=['menu'])
def menu_command(message):
    keyboards.main_menu(bot, message.chat.id)


@bot.message_handler(commands=['help'])
def help_command(message):
    chat_id = message.chat.id
    user = api.get_user(chat_id)
    bot.send_message(chat_id, message['messages']['help'][user['language']])


@bot.message_handler(commands=['pay'])
def pay_command(message):
    chat_id = message.chat.id
    user = api.get_user(chat_id)
    bot.send_message(chat_id, message['messages']['help'][user['language']])


@bot.message_handler(content_types=['contact'])
def contact(message):
    chat_id = message.contact.user_id
    user = api.get_user(chat_id)
    if message.contact is not None:
        api.update_field_for_user(chat_id, message.contact.phone_number, "phoneNumber")
        bot.send_message(chat_id, messages['messages']['info'][user['language']])
        time.sleep(TIME_SLEEP)


@bot.message_handler(content_types=['text'], func=lambda message: True)
def send_text(message):
    chat_id = message.chat.id
    message_text = message.text
    user = api.get_user(chat_id)

    if message_text == '🇺🇦 UA' or message_text == '🇺🇸 EN':
        if message_text == '🇺🇦 UA':
            api.update_field_for_user(chat_id, 'ua', 'language')
        else:
            api.update_field_for_user(chat_id, 'en', 'language')

        user = api.get_user(chat_id)
        if user['phoneNumber'] is None:
            keyboards.phone_number(bot, chat_id)
        else:
            bot.send_message(chat_id, messages['messages']['done_change_language'][user['language']])
            keyboards.main_menu(bot, chat_id)
    elif message_text == messages['buttons']['main_menu'][user['language']]:
        keyboards.main_menu(bot, chat_id)
    elif message_text == messages['buttons']['menu_settings'][user['language']]:
        keyboards.menu_filters(bot, chat_id)
    elif message_text == messages['buttons']['menu_proposal'][user['language']]:
        utils.offer_message(bot, chat_id)





print('Listening....')
count_restarts = 0
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as error:
        count_restarts = count_restarts + 1
        print(f'count_restarts = {count_restarts} ({error})')
        time.sleep(1)
