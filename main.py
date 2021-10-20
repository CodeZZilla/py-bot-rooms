import os
import string
import random
import telebot
import json
import api
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import re
from time import sleep

bot = telebot.TeleBot('')
sticker_start = 'CAACAgUAAxkBAAP-X0qNH1rpyoDqT7odr43p9nZntwkAAm8DAALpCsgDr86-2QK6XXQbBA'

messages = json.load(open('static/MessagesConfig.json', encoding='utf-8'))
cities = json.load(open('static/cities.json', encoding='utf-8'))
count_users = 0


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    if api.checkUser(message):
        bot.send_sticker(chat_id, sticker_start)
        send_message_with_keyboard(chat_id, "З поверненням, " + message.from_user.first_name, "city", cities, 1)
    else:
        print(api.createUser(message))
        bot.send_message(chat_id, 'Привіт, ' + message.from_user.first_name + ' ' + message.from_user.last_name + '!')
        bot.send_message(chat_id, messages[0]["text"])
        send_message_with_keyboard(chat_id, messages[1]["text"], "city", cities, 1)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # print(call.message.id)
    if call.message:
        chat_id = call.message.chat.id
        key = str(call.data).split(':')[0]
        value = str(call.data).split(':')[1]
        if key == "city":
            user = api.updateCityForUser(chat_id, value)
            send_message_with_keyboard(chat_id,
                                       "Ти з нами вперше - тому тобі надано 2 дні тестової підписки \n З чим тобі допомогти?",
                                       "service", cities, 1)


def send_message_with_keyboard(id_telegram, text, call_back_start, array_text, col):
    inline_keyboard = InlineKeyboardMarkup()
    for i in range(len(array_text)):
        data = call_back_start + ":" + array_text[i]["id"]
        button = InlineKeyboardButton(text=array_text[i]["name"], callback_data=data)
        inline_keyboard.row(button)
    bot.send_message(id_telegram, text, parse_mode="Markdown", reply_markup=inline_keyboard)


print('Listening....')
bot.polling()
