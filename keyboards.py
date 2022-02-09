import telebot
from telebot.util import async_dec

import api
import json
from telebot.types import KeyboardButton

messages = json.load(open('./static/messages_v2.json', encoding='utf-8'))
cities = json.load(open('./static/cities.json', encoding='utf-8'))


def language_keyboard(bot, chat_id):
    user = api.get_user(chat_id)
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🇺🇦 UA', '🇺🇸 EN')
    if not user['phoneNumber'] is None:
        keyboard.row(messages['buttons']['main_menu'][user['language']])
    bot.send_message(chat_id, messages['messages']['language_communication']['ua'], parse_mode="Markdown",
                     reply_markup=keyboard)


def phone_number(bot, chat_id):
    user = api.get_user(chat_id)
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row(KeyboardButton(text=messages['buttons']['phone_number'][user['language']], request_contact=True))
    bot.send_message(chat_id, messages['messages']['phone_number'][user['language']], parse_mode="Markdown",
                     reply_markup=keyboard)


def main_menu(bot, chat_id):
    user = api.get_user(chat_id)
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row(KeyboardButton(text=messages['buttons']['menu_saved'][user['language']]),
                 KeyboardButton(text=messages['buttons']['menu_new_offers'][user['language']]))
    keyboard.row(KeyboardButton(text=messages['buttons']['menu_settings'][user['language']]),
                 KeyboardButton(text=messages['buttons']['menu_info'][user['language']]))
    keyboard.row(KeyboardButton(text=messages['buttons']['menu_proposal'][user['language']]),
                 KeyboardButton(text=messages['buttons']['menu_subscription'][user['language']]))

    if api.is_admins(chat_id):
        keyboard.row(KeyboardButton(text=messages['buttons']['menu_statistics'][user['language']]))

    bot.send_message(chat_id, messages['messages']['main_menu'][user['language']], reply_markup=keyboard)


@async_dec()
def menu_filters(bot, chat_id):
    user = api.get_user(chat_id)
    city_user = ''
    for i in cities:
        if i['id'] == user['city']:
            city_user = i[user['language']]
    type_user = ''
    if user['type'] == 'продажа':
        type_user = "Купівля"
    elif user['type'] == 'аренда:комната':
        type_user = 'Оренда (Кімната)'
    elif user['type'] == 'аренда:квартира':
        type_user = 'Оренда (Квартира)'
    elif user['type'] == 'аренда':
        type_user = 'Оренда'
    prise = str(user['priceMin']) + ' - ' + str(user['priceMax'])
    rooms_user = str(user['rooms'])
    regions_user = str(user['region'])
    metros_user = str(user['metroNames'])

    text = f"{messages['messages']['filters_title'][user['language']]}" \
           f"{messages['messages']['filter_city'][user['language']]}{city_user}\n" \
           f"{messages['messages']['filter_type'][user['language']]}{type_user}\n" \
           f"{messages['messages']['filter_price'][user['language']]}{prise}\n" \
           f"{messages['messages']['filter_rooms'][user['language']]}{rooms_user}\n" \
           f"{messages['messages']['filter_regions'][user['language']]}{regions_user}\n" \
           f"{messages['messages']['filter_metro'][user['language']]}{metros_user}\n"

    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row(messages['buttons']['edit_filter'][user['language']])
    keyboard.row(messages['buttons']['main_menu'][user['language']])
    bot.send_message(chat_id, text, reply_markup=keyboard)

