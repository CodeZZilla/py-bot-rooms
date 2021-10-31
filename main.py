import telebot
import logging
import sys
import time
import datetime
import json
import api
import status
import generator_telegraph
from threading import Thread
import schedule
from telebot.util import async_dec
from telebot.types import InputMediaPhoto, LabeledPrice, ShippingOption
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(filename='file.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S %D.%M.%Y',
                    level=logging.DEBUG)

tokens = json.load(open('tokens.json', encoding='utf-8'))
TELEGRAM_TOKEN = tokens['TELEGRAM_TOKEN']
tranzzo_token = tokens['TRANZZO_TOKEN']

bot = telebot.TeleBot(TELEGRAM_TOKEN)

sticker_start = 'CAACAgUAAxkBAAP-X0qNH1rpyoDqT7odr43p9nZntwkAAm8DAALpCsgDr86-2QK6XXQbBA'
prise_png = open('./files/animation.gif', 'rb')

messages = json.load(open('static/messages.json', encoding='utf-8'))
cities = json.load(open('static/cities.json', encoding='utf-8'))
services = json.load(open('static/services.json', encoding='utf-8'))
rooms = json.load(open('static/rooms.json', encoding='utf-8'))
regions = json.load(open('static/regions.json', encoding='utf-8'))

TIME_SLEEP = 3
metro_colors = {
    'red': '🔴',
    'blue': '🔵',
    'green': '🟢'
}
# shipping_options = [
#     ShippingOption(id='7day', title='7 днів').add_price(LabeledPrice('7 днів', 19900)),
#     ShippingOption(id='14day', title='14 днів').add_price(LabeledPrice('14 днів', 29900)),
#     ShippingOption(id='30day', title='30 днів').add_price(LabeledPrice('30 днів', 49900))]
shipping_options = [
    ShippingOption(id='7day', title='7 днів').add_price(LabeledPrice('7 днів', 100)),
    ShippingOption(id='14day', title='14 днів').add_price(LabeledPrice('14 днів', 100)),
    ShippingOption(id='30day', title='30 днів').add_price(LabeledPrice('30 днів', 100))]


metros_all_static = []
regions_all_static = regions['Киев']['regions']
for item in regions_all_static:
    for metro in item['metros']:
        if not metros_all_static.__contains__(metro):
            metros_all_static.append(metro['id'])


def send_message_from_server():
    data = api.get_users_messages()
    telegram_ids = data['userTelegramId']
    if not data['userTelegramId'] is None and not data['messageText'] is None:
        file = open('get_users_messages')
        if not file.read() == str(data):
            file.close()
            for id_item in telegram_ids:
                try:
                    bot.send_message(int(id_item), data['messageText'])
                except Exception:
                    continue
            file_w = open("get_users_messages", "w")
            file_w.write(str(data))
            file_w.close()


schedule.every(10).seconds.do(send_message_from_server)


def async_send_message():
    while True:
        schedule.run_pending()
        time.sleep(1)


th = Thread(target=async_send_message)
th.start()


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    if api.check_user(message):
        user = api.get_user(chat_id)
        bot.send_sticker(chat_id, sticker_start)
        bot.send_message(chat_id, messages['start_registered'][user['language']])
    else:
        api.create_user(message)
        language_message(chat_id)


@bot.message_handler(commands=['language'])
def language_message(message):
    chat_id = message.chat.id
    language_message(chat_id)


@bot.message_handler(commands=['infosubscription'])
def info_message(message):
    chat_id = message.chat.id
    user = api.get_user(chat_id)
    bot.send_message(chat_id, f"{messages['info_user'][user['language']]}{user['nickname']}\n"
                              f"{messages['info_subscription'][user['language']]}{str(user['daysOfSubscription'])}\n"
                              f"{messages['info_creation_date'][user['language']]}{user['creationDate'].split('T')[0]}")


@bot.message_handler(commands=['pay'])
def info_message(message):
    chat_id = message.chat.id
    user = api.get_user(chat_id)
    pay_message(chat_id, user)


@bot.message_handler(commands=['filters'])
def filters_message(message):
    chat_id = message.chat.id
    user = api.get_user(chat_id)
    if not user['userStatus'] == status.UserStatus.YES_FILTERS.value:
        bot.send_message(chat_id, messages['filter_tag_error_msg'][user['language']])
        if user['userStatus'] == status.UserStatus.NO_FILTERS.value or \
                user['userStatus'] == status.UserStatus.STEP_TYPE.value:
            api.update_field_for_user(chat_id, status.UserStatus.STEP_TYPE.value, "userStatus")
            filter_type(chat_id, messages['start_filter'][user['language']], user['language'])
        elif user['userStatus'] == status.UserStatus.STEP_CITY.value:
            filter_city(chat_id, '', messages['filter_city'][user['language']], user['language'], True)
        elif user['userStatus'] == status.UserStatus.STEP_PRICE.value:
            filter_price(chat_id, '', user['language'], True)
        elif user['userStatus'] == status.UserStatus.STEP_ROOMS.value:
            if not user['type'] == 'аренда:комната':
                send_message_with_keyboard(chat_id, messages['count_rooms'][user['language']],
                                           "rooms", rooms, user['language'], True)
        elif user['userStatus'] == status.UserStatus.STEP_REGIONS.value:
            filter_regions(chat_id, '', user['language'], user['city'], False)
        elif user['userStatus'] == status.UserStatus.STEP_METRO.value:
            filter_metro(chat_id, '', api.get_user(chat_id), False)
    else:
        menu_filters(chat_id, user)


@bot.message_handler(commands=['apartments'])
def apartments_message(message):
    chat_id = message.chat.id
    user = api.get_user(chat_id)
    today_compilation_array = user['todayCompilation']
    if len(today_compilation_array) == 0:
        bot.send_message(chat_id, messages['msg_apartment_update_filters'][user['language']])
    else:
        bot.send_message(chat_id, messages['msg_after_filter'][user['language']])
        time.sleep(TIME_SLEEP)
        bot.send_message(chat_id, messages['msg_after_filter_2'][user['language']])
        time.sleep(TIME_SLEEP)
        if len(today_compilation_array) == 1:
            send_apartment(chat_id, api.find_apartment(today_compilation_array[0])[0],
                           today_compilation_array[0], today_compilation_array[0], user)
        else:
            send_apartment(chat_id, api.find_apartment(today_compilation_array[0])[0],
                           today_compilation_array[len(today_compilation_array) - 1], today_compilation_array[1], user)


@bot.message_handler(commands=['saved'])
def saved_message(message):
    chat_id = message.chat.id
    user = api.get_user(chat_id)
    saved_apartments_array = user['savedApartments']
    if len(saved_apartments_array) == 0:
        bot.send_message(chat_id, messages['msg_saved_none'][user['language']])
    elif len(saved_apartments_array) == 1:
        send_apartment(chat_id, api.find_apartment(saved_apartments_array[0])[0],
                       saved_apartments_array[0], saved_apartments_array[0], user, is_saved=True)
    else:
        send_apartment(chat_id, api.find_apartment(saved_apartments_array[0])[0],
                       saved_apartments_array[len(saved_apartments_array) - 1], saved_apartments_array[1], user,
                       is_saved=True)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        chat_id = call.message.chat.id
        split_array = str(call.data).split(':')
        key = split_array[0]
        value = split_array[1]
        user = api.get_user(chat_id)

        if key == "service":
            if value == "rent":
                filter_type_details(chat_id, call.message.id, user['language'])
            elif value == 'buy' or value == 'rent_room' or value == 'rent_apartment' or value == 'all':
                if value == 'buy':
                    value = "продажа"
                elif value == 'rent_room':
                    value = 'аренда:комната'
                elif value == 'rent_apartment':
                    value = 'аренда:квартира'
                if user['userStatus'] == status.UserStatus.EDIT_MENU.value:
                    if value == 'аренда:комната':
                        api.update_field_for_user(chat_id, None, 'rooms')
                    api.update_field_for_user(chat_id, value, "type")
                    api.update_field_for_user(chat_id, status.UserStatus.YES_FILTERS.value, "userStatus")
                    menu_filters(chat_id, api.get_user(chat_id), True, call.message.id)
                else:
                    if value == 'аренда:комната':
                        api.update_field_for_user(chat_id, None, 'rooms')
                        api.update_field_for_user(chat_id, value, "type")
                        api.update_field_for_user(chat_id, status.UserStatus.STEP_PRICE.value, 'userStatus')
                        filter_price(chat_id, call.message.id, user['language'], False)
                    else:
                        api.update_field_for_user(chat_id, value, "type")
                        api.update_field_for_user(chat_id, status.UserStatus.STEP_ROOMS.value, 'userStatus')
                        bot.delete_message(chat_id, call.message.id)
                        send_message_with_keyboard(chat_id, messages['count_rooms'][user['language']], "rooms", rooms,
                                                   user['language'], True, True)

                    # filter_city(chat_id, call.message.id, messages['filter_city'][user['language']], user['language'])
            elif value == 'back':
                filter_type(chat_id, messages['start_filter'][user['language']], user['language'], True,
                            call.message.id)
        elif key == "city":
            if value == 'Киев':
                if user['userStatus'] == status.UserStatus.EDIT_MENU.value:
                    api.update_field_for_user(chat_id, status.UserStatus.YES_FILTERS.value, "userStatus")
                    menu_filters(chat_id, api.get_user(chat_id), True, call.message.id)
                else:
                    api.update_field_for_user(chat_id, status.UserStatus.STEP_TYPE.value, "userStatus")
                    api.update_field_for_user(chat_id, value, "city")
                    filter_type(chat_id, messages['start_filter'][user['language']], user['language'], True,
                                call.message.id)
            else:
                filter_city(chat_id, call.message.id, messages['filter_city_error'][user['language']], user['language'])
        elif key == "rooms":
            reply_markup = call.message.reply_markup
            inline_keyboard = reply_markup.keyboard
            if value == 'save' or value == 'continue' or value == 'back':
                if value == 'back':
                    api.update_field_for_user(chat_id, status.UserStatus.STEP_TYPE.value, 'userStatus')
                    filter_type(chat_id, messages['start_filter'][user['language']], user['language'], True,
                                call.message.id)
                else:
                    selected_rooms = filter_multi_select_return_array(inline_keyboard)
                    if len(selected_rooms) == 1:
                        if selected_rooms[0] == '4+':
                            selected_rooms = [4, 5, 6, 7, 8, 9, 10]
                    elif len(selected_rooms) > 1:
                        if selected_rooms.__contains__('4+'):
                            selected_rooms = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                        else:
                            for room in selected_rooms:
                                if room == '4+':
                                    room = 4
                                else:
                                    room = int(room)
                    else:
                        selected_rooms = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

                    if user['userStatus'] == status.UserStatus.EDIT_MENU.value:
                        if user['type'] == 'аренда:комната':
                            api.update_field_for_user(chat_id, None, 'rooms')
                        else:
                            api.update_field_for_user(chat_id, selected_rooms, 'rooms')
                            api.update_field_for_user(chat_id, status.UserStatus.YES_FILTERS.value, 'userStatus')
                            menu_filters(chat_id, api.get_user(chat_id), True, call.message.id)
                    else:
                        api.update_field_for_user(chat_id, selected_rooms, 'rooms')
                        bot.delete_message(chat_id, call.message.id)
                        api.update_field_for_user(chat_id, status.UserStatus.STEP_PRICE.value, 'userStatus')
                        filter_price(chat_id, call.message.id, user['language'], False)
            else:
                bot.edit_message_reply_markup(chat_id, call.message.id,
                                              reply_markup=filter_multi_select(reply_markup, value))
        elif key == "start":
            inline_keyboard = InlineKeyboardMarkup()
            if value == 'next' and user['userStatus'] == status.UserStatus.NO_FILTERS.value:
                start_next_step(chat_id, call.message.id, inline_keyboard, user['language'])
            elif value == 'subscription' and user['userStatus'] == status.UserStatus.NO_FILTERS.value:
                inline_keyboard.row(
                    InlineKeyboardButton(text=messages['7days'][user['language']], callback_data='pay:7'))
                inline_keyboard.row(
                    InlineKeyboardButton(text=messages['14days'][user['language']], callback_data='pay:14'))
                inline_keyboard.row(
                    InlineKeyboardButton(text=messages['30days'][user['language']], callback_data='pay:30'))
                inline_keyboard.row(
                    InlineKeyboardButton(text=messages['btn_back'][user['language']], callback_data='start:back'))
                bot.edit_message_reply_markup(chat_id, call.message.id, reply_markup=inline_keyboard)
            elif value == 'back' and user['userStatus'] == status.UserStatus.NO_FILTERS.value:
                start_next_step(chat_id, call.message.id, inline_keyboard, user['language'])
            elif value == 'free' and user['userStatus'] == status.UserStatus.NO_FILTERS.value:
                bot.edit_message_reply_markup(chat_id, call.message.id)
                bot.send_message(chat_id, messages['info_free'][user['language']])
                time.sleep(TIME_SLEEP)
                api.update_field_for_user(chat_id, status.UserStatus.STEP_CITY.value, "userStatus")
                filter_city(chat_id, '', messages['filter_city'][user['language']], user['language'], True)
        elif key == "pay":
            amount = 100
            # amount = 0
            # if value == '7':
            #     amount = 19900
            # elif value == '14':
            #     amount = 29900
            # elif value == '30':
            #     amount = 49900
            prices = [LabeledPrice(label=messages['btn_pay_2'][user['language']], amount=amount)]
            bot.send_message(chat_id, 'Тест: 4242 4242 4242 4242, cvv та дата будьякі')
            bot.send_message(chat_id, messages['msg_pre_pay'][user['language']])
            bot.send_invoice(chat_id,
                             title=messages['buy_1'][user['language']] + value + messages['buy_2'][user['language']],
                             description='Want to visit your great-great-great-grandparents?'
                                         ' Make a fortune at the races?'
                                         ' Shake hands with Hammurabi and take a stroll in the Hanging Gardens?'
                                         ' Order our Working Time Machine today!',
                             provider_token=tranzzo_token,
                             currency='UAH',
                             prices=prices,
                             invoice_payload='telegram_id: ' + str(chat_id) + ' prise:' + str(amount))
        elif key == "language":
            if value == "ua":
                api.update_field_for_user(chat_id, 'ua', 'language')
            elif value == "en":
                api.update_field_for_user(chat_id, 'en', 'language')
            user = api.get_user(chat_id)
            if user['userStatus'] == status.UserStatus.NO_FILTERS.value:
                bot.delete_message(chat_id, call.message.id)
                bot.send_message(chat_id, messages['info'][user['language']])
                time.sleep(TIME_SLEEP)
                keyboard_start = InlineKeyboardMarkup()
                keyboard_start.add(
                    InlineKeyboardButton(text=messages['btn_start'][user['language']], callback_data='start:next'))
                bot.send_message(chat_id, messages['info2'][user['language']], parse_mode="Markdown",
                                 reply_markup=keyboard_start)

                # bot.send_message(chat_id, messages['info3'][user['language']], parse_mode="Markdown",
                #                  reply_markup=keyboard_start)
            else:
                bot.delete_message(chat_id, call.message.id)
                bot.send_message(chat_id, messages['msg_done_change_language'][user['language']])
        elif key == "region":
            reply_markup = call.message.reply_markup
            inline_keyboard = reply_markup.keyboard
            if value == 'save' or value == 'continue':
                selected_regions = filter_multi_select_return_array(inline_keyboard)
                if value == 'continue':
                    selected_regions = []
                    regions_all = regions[user['city']]['regions']
                    for item in regions_all:
                        selected_regions.append(item['id'])

                api.update_field_for_user(chat_id, selected_regions, 'region')
                if user['userStatus'] == status.UserStatus.EDIT_MENU.value:
                    api.update_field_for_user(chat_id, status.UserStatus.YES_FILTERS.value, 'userStatus')
                    menu_filters(chat_id, api.get_user(chat_id), True, call.message.id)
                else:
                    api.update_field_for_user(chat_id, status.UserStatus.STEP_METRO.value, 'userStatus')
                    filter_metro(chat_id, call.message.id, api.get_user(chat_id), True)

            else:
                bot.edit_message_reply_markup(chat_id, call.message.id,
                                              reply_markup=filter_multi_select(reply_markup, value))
        elif key == "metro":
            reply_markup = call.message.reply_markup
            inline_keyboard = reply_markup.keyboard
            if value == 'save' or value == 'continue':
                selected_metros = []
                if value == 'save':
                    selected_metros = filter_multi_select_return_array(inline_keyboard)
                elif value == 'continue':
                    selected_metros = metros_all_static
                api.update_field_for_user(chat_id, selected_metros, 'metroNames')
                api.update_field_for_user(chat_id, status.UserStatus.YES_FILTERS.value, 'userStatus')
                if user['userStatus'] == status.UserStatus.EDIT_MENU.value:
                    menu_filters(chat_id, api.get_user(chat_id), True, call.message.id)
                else:
                    bot.delete_message(chat_id, call.message.id)
                    apartments_message(call.message)
            else:
                bot.edit_message_reply_markup(chat_id, call.message.id,
                                              reply_markup=filter_multi_select(reply_markup, value))
        elif key == "edit":
            if value == "filters":
                filters_keyboard = InlineKeyboardMarkup()
                filters_keyboard.row(
                    InlineKeyboardButton(text=messages['btn_filter_edit_type'][user['language']],
                                         callback_data='edit:type'),
                    InlineKeyboardButton(text=messages['btn_filter_edit_city'][user['language']],
                                         callback_data='edit:city'))
                filters_keyboard.row(
                    InlineKeyboardButton(text=messages['btn_filter_edit_price'][user['language']],
                                         callback_data='edit:price'),
                    InlineKeyboardButton(text=messages['btn_filter_edit_rooms'][user['language']],
                                         callback_data='edit:rooms'))
                filters_keyboard.row(
                    InlineKeyboardButton(text=messages['btn_filter_edit_regions'][user['language']],
                                         callback_data='edit:regions'),
                    InlineKeyboardButton(text=messages['btn_filter_edit_metro'][user['language']],
                                         callback_data='edit:metro'))

                bot.edit_message_reply_markup(chat_id, call.message.id, reply_markup=filters_keyboard)
            elif value == 'type':
                api.update_field_for_user(chat_id, status.UserStatus.EDIT_MENU.value, "userStatus")
                filter_type(chat_id, messages['start_filter'][user['language']], user['language'], True,
                            call.message.id)
            elif value == 'city':
                api.update_field_for_user(chat_id, status.UserStatus.EDIT_MENU.value, "userStatus")
                filter_city(chat_id, call.message.id, messages['filter_city'][user['language']], user['language'])
            elif value == 'price':
                api.update_field_for_user(chat_id, status.UserStatus.EDIT_MENU.value, "userStatus")
                filter_price(chat_id, call.message.id, user['language'], False)
            elif value == 'rooms':
                api.update_field_for_user(chat_id, status.UserStatus.EDIT_MENU.value, "userStatus")
                send_message_with_keyboard(chat_id, messages['count_rooms'][user['language']], "rooms", rooms,
                                           user['language'], True)
            elif value == 'regions':
                api.update_field_for_user(chat_id, status.UserStatus.EDIT_MENU.value, "userStatus")
                filter_regions(chat_id, call.message.id, user['language'], user['city'], True)
            elif value == 'metro':
                api.update_field_for_user(chat_id, status.UserStatus.EDIT_MENU.value, "userStatus")
                filter_metro(chat_id, call.message.id, api.get_user(chat_id), True)
        elif key == "navigation" or key == "navigation_save":
            if not value == "save":
                array = []
                if key == "navigation":
                    array = user['todayCompilation']
                else:
                    array = user['savedApartments']

                if not len(array) == 0:
                    index_value = array.index(int(value))
                    next_index = 0
                    back_index = 0
                    if len(array) >= 2:
                        if index_value == 0:
                            next_index = 1
                            back_index = len(array) - 1
                        elif index_value == len(array) - 1:
                            next_index = 0
                            back_index = len(array) - 2
                        else:
                            next_index = index_value + 1
                            back_index = index_value - 1
                    elif len(array) == 1:
                        next_index = 0
                        back_index = 0
                    apartment_obj = api.find_apartment(value)[0]
                    if key == "navigation":
                        send_apartment(chat_id, apartment_obj, array[back_index],
                                       array[next_index], user, call.message.id, True,
                                       int(split_array[2]))
                    else:
                        send_apartment(chat_id, apartment_obj, array[back_index],
                                       array[next_index], user, call.message.id, True,
                                       int(split_array[2]), True)
                else:
                    for i in range(int(split_array[2]) + 1):
                        bot.delete_message(chat_id, call.message.id - i)
            else:
                saved_apartments_array = user['savedApartments']
                if key == "navigation":
                    if not saved_apartments_array.__contains__(int(split_array[2])):
                        saved_apartments_array.append(int(split_array[2]))
                else:
                    if saved_apartments_array.__contains__(int(split_array[2])):
                        saved_apartments_array.remove(int(split_array[2]))
                api.update_field_for_user(chat_id, saved_apartments_array, 'savedApartments')
                reply_markup = call.message.reply_markup
                keyboard = reply_markup.keyboard
                if not '✅ ' in keyboard[1][0].text:
                    keyboard[1][0].text = '✅ ' + keyboard[1][0].text
                    reply_markup.keyboard = keyboard
                    bot.edit_message_reply_markup(chat_id, call.message.id, reply_markup=reply_markup)


@async_dec()
def language_message(chat_id):
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton(text='🇺🇦 UA', callback_data='language:ua'))
    inline_keyboard.add(InlineKeyboardButton(text='🇺🇸 EN', callback_data='language:en'))
    bot.send_message(chat_id, '👋🏻 Обрати мову спілкування\nChoose your Language', parse_mode="Markdown",
                     reply_markup=inline_keyboard)


@async_dec()
def pay_message(id_telegram, user):
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.row(InlineKeyboardButton(text=messages['7days'][user['language']], callback_data='pay:7'))
    inline_keyboard.row(InlineKeyboardButton(text=messages['14days'][user['language']], callback_data='pay:14'))
    inline_keyboard.row(InlineKeyboardButton(text=messages['30days'][user['language']], callback_data='pay:30'))
    bot.send_message(id_telegram, messages['pay_info'][user['language']], reply_markup=inline_keyboard)


@async_dec()
def menu_filters(telegram_id, user, flag_msg=False, message_id=0):
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

    text = messages['filter_info_text_1'][user['language']] + messages['filter_info_text_2'][
        user['language']] + city_user + '\n' + messages['filter_info_text_3'][user['language']] + type_user + '\n' + \
           messages['filter_info_text_4'][user['language']] + prise + '\n' + messages['filter_info_text_5'][
               user['language']] + rooms_user + '\n' + messages['filter_info_text_6'][
               user['language']] + regions_user + '\n' + messages['filter_info_text_7'][
               user['language']] + metros_user

    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.row(
        InlineKeyboardButton(text=messages['edit_filter_btn'][user['language']], callback_data='edit:filters'))
    if flag_msg:
        bot.edit_message_text(text, telegram_id, message_id)
        bot.edit_message_reply_markup(telegram_id, message_id, reply_markup=inline_keyboard)
    else:
        bot.send_message(telegram_id, text, reply_markup=inline_keyboard)


def filter_multi_select_return_array(inline_keyboard):
    len_inline_keyboard = len(inline_keyboard)
    selected = []
    for i in range(len_inline_keyboard - 1):
        len_row = len(inline_keyboard[i])
        for j_row in range(len_row):
            if str(inline_keyboard[i][j_row].text).startswith('✅ '):
                selected.append(inline_keyboard[i][j_row].callback_data.split(':')[1])
    return selected


def filter_multi_select(reply_markup, value):
    keyboard = reply_markup.keyboard
    len_keyboard = len(keyboard)
    if not value == 'save' and not value == 'continue':
        for i in range(len_keyboard - 1):
            len_row = len(keyboard[i])
            for j_row in range(len_row):
                if str(keyboard[i][j_row].callback_data).split(':')[1] == value:
                    if not str(keyboard[i][j_row].text).startswith('✅ '):
                        keyboard[i][j_row].text = '✅ ' + keyboard[i][j_row].text
                    else:
                        keyboard[i][j_row].text = keyboard[i][j_row].text[2:]
        reply_markup.keyboard = keyboard
        return reply_markup


@async_dec()
def filter_type(id_telegram, text, language, reply=False, message_id=None):
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton(text=services[0][language], callback_data='service:' + services[0]['id']),
                        InlineKeyboardButton(text=services[1][language], callback_data='service:' + services[1]['id']))
    if reply:
        bot.edit_message_text(text, id_telegram, message_id)
        bot.edit_message_reply_markup(id_telegram, message_id, reply_markup=inline_keyboard)
    else:
        bot.send_message(id_telegram, text, parse_mode="Markdown", reply_markup=inline_keyboard)


@async_dec()
def filter_type_details(id_telegram, message_id, language):
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton(text=services[2][language], callback_data='service:' + services[2]['id']))
    inline_keyboard.add(InlineKeyboardButton(text=services[3][language], callback_data='service:' + services[3]['id']))
    inline_keyboard.add(InlineKeyboardButton(text=messages['btn_back'][language], callback_data='service:back'))
    bot.edit_message_text(messages['msg_type_detal'][language], id_telegram, message_id)
    bot.edit_message_reply_markup(id_telegram, message_id, reply_markup=inline_keyboard)


@async_dec()
def filter_city(id_telegram, message_id, text, language, new_msg=False):
    inline_keyboard = InlineKeyboardMarkup()
    for i in range(len(cities)):
        button = InlineKeyboardButton(text=cities[i][language], callback_data='city:' + cities[i]['id'])
        inline_keyboard.add(button)
    if not new_msg:
        bot.edit_message_text(text, id_telegram, message_id)
        bot.edit_message_reply_markup(id_telegram, message_id, reply_markup=inline_keyboard)
    else:
        bot.send_message(id_telegram, text, reply_markup=inline_keyboard)


def filter_price(id_telegram, message_id, language, new_message):
    # if not new_message:
    #     bot.delete_message(id_telegram, message_id)
    #     bot.send_animation(id_telegram, prise_png, None, messages['filter_price'][language])
    # else:
    bot.send_message(id_telegram, messages['filter_price'][language])
    bot.send_message(id_telegram, messages['filter_price_2'][language])
    # bot.send_animation(id_telegram, prise_png, None, messages['filter_price'][language])


@async_dec()
def filter_regions(id_telegram, message_id, language, city, edit_flag=False):
    inline_keyboard = InlineKeyboardMarkup()
    regions_array = regions[city]['regions']
    for i in range(0, len(regions_array), 2):
        if i + 1 > len(regions_array) - 1:
            inline_keyboard.row(
                InlineKeyboardButton(text=regions_array[i][language], callback_data='region:' + regions_array[i]['id']))
        else:
            inline_keyboard.row(
                InlineKeyboardButton(text=regions_array[i][language], callback_data='region:' + regions_array[i]['id']),
                InlineKeyboardButton(text=regions_array[i + 1][language],
                                     callback_data='region:' + regions_array[i + 1]['id']))
    inline_keyboard.row(
        InlineKeyboardButton(text=messages['btn_continue'][language], callback_data='region:continue'),
        InlineKeyboardButton(text=messages['btn_save'][language], callback_data='region:save'))
    if not edit_flag:
        bot.send_message(id_telegram, messages['filter_region_msg'][language], reply_markup=inline_keyboard)
    else:
        bot.edit_message_text(messages['filter_region_msg'][language], id_telegram, message_id)
        bot.edit_message_reply_markup(id_telegram, message_id, reply_markup=inline_keyboard)


@async_dec()
def filter_metro(id_telegram, message_id, user, edit_flag=False):
    inline_keyboard = InlineKeyboardMarkup()
    regions_all = regions[user['city']]['regions']
    metros_for_user = []
    for region in regions_all:
        if region['id'] in user['region']:
            for metro_item in region['metros']:
                if not metros_for_user.__contains__(metro_item):
                    metros_for_user.append(metro_item)
    for i in range(0, len(metros_for_user), 2):
        if i + 1 > len(metros_for_user) - 1:
            inline_keyboard.row(
                InlineKeyboardButton(
                    text=metros_for_user[i][user['language']] + ' ' + metro_colors[metros_for_user[i]['color']],
                    callback_data='metro:' + metros_for_user[i]['id']))
        else:
            inline_keyboard.row(
                InlineKeyboardButton(
                    text=metros_for_user[i][user['language']] + ' ' + metro_colors[metros_for_user[i]['color']],
                    callback_data='metro:' + metros_for_user[i]['id']),
                InlineKeyboardButton(
                    text=metros_for_user[i + 1][user['language']] + ' ' + metro_colors[metros_for_user[i + 1]['color']],
                    callback_data='metro:' + metros_for_user[i + 1]['id']))
    inline_keyboard.row(
        InlineKeyboardButton(text=messages['btn_continue'][user['language']], callback_data='metro:continue'),
        InlineKeyboardButton(text=messages['btn_save'][user['language']], callback_data='metro:save'))
    if not edit_flag:
        bot.send_message(id_telegram, messages['filter_metro_msg'][user['language']], reply_markup=inline_keyboard)
    else:
        bot.edit_message_text(messages['filter_metro_msg'][user['language']], id_telegram, message_id)
        bot.edit_message_reply_markup(id_telegram, message_id, reply_markup=inline_keyboard)


@async_dec()
def start_next_step(id_telegram, message_id, inline_keyboard, language):
    inline_keyboard.add(InlineKeyboardButton(text=messages['btn_pay_1'][language], callback_data='start:subscription'))
    inline_keyboard.add(InlineKeyboardButton(text=messages['btn_free'][language], callback_data='start:free'))
    bot.edit_message_reply_markup(id_telegram, message_id, reply_markup=inline_keyboard)


@bot.message_handler(content_types=['text'], func=lambda message: True)
def send_text(message):
    telegram_id = message.chat.id
    message_text = message.text
    user = api.get_user(telegram_id)

    if user['userStatus'] == status.UserStatus.STEP_PRICE.value or \
            user['userStatus'] == status.UserStatus.EDIT_MENU.value:
        min_and_max = str(message_text).split('-')
        if len(min_and_max) == 2 and min_and_max[0].isdigit() and min_and_max[1].isdigit() and int(
                min_and_max[0]) < int(min_and_max[1]):
            api.update_field_for_user(telegram_id, int(min_and_max[0]), 'priceMin')
            api.update_field_for_user(telegram_id, int(min_and_max[1]), 'priceMax')
            if user['userStatus'] == status.UserStatus.STEP_PRICE.value:
                api.update_field_for_user(telegram_id, status.UserStatus.STEP_REGIONS.value, 'userStatus')
                filter_regions(telegram_id, '', user['language'], user['city'])
            else:
                api.update_field_for_user(telegram_id, status.UserStatus.YES_FILTERS.value, 'userStatus')
                menu_filters(telegram_id, api.get_user(telegram_id))
        else:
            bot.send_message(telegram_id, messages['filter_price_error'][user['language']])


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                              error_message='ПОМИЛКА')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="ПОМИЛКА")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user = api.get_user(message.chat.id)
    total_amount = int(message.successful_payment.total_amount)
    if total_amount == 19900:
        api.update_field_for_user(message.chat.id, user['daysOfSubscription'] + 7, 'daysOfSubscription')
    elif total_amount == 29900:
        api.update_field_for_user(message.chat.id, user['daysOfSubscription'] + 14, 'daysOfSubscription')
    elif total_amount == 49900:
        api.update_field_for_user(message.chat.id, user['daysOfSubscription'] + 30, 'daysOfSubscription')
    user = api.get_user(message.chat.id)
    logging.info(
        f"id_telegram:{user['idTelegram']}; successful_payment:{total_amount}; date: {datetime.datetime.now()}")
    bot.send_message(message.chat.id, messages['pay_good'][user['language']], parse_mode='Markdown')
    if user['userStatus'] == status.UserStatus.NO_FILTERS.value:
        api.update_field_for_user(message.chat.id, status.UserStatus.STEP_TYPE.value, "userStatus")

        filter_city(message.chat.id, '', messages['filter_city'][user['language']], user['language'], True)


@async_dec()
def send_message_with_keyboard(id_telegram, text, call_back_start, array_text, language, multi_select=False,
                               is_first=False):
    inline_keyboard = InlineKeyboardMarkup()
    for i in range(len(array_text)):
        data = call_back_start + ":" + array_text[i]["id"]
        button = InlineKeyboardButton(text=array_text[i][language], callback_data=data)
        inline_keyboard.add(button)
    if multi_select:
        inline_keyboard.add(
            InlineKeyboardButton(text=messages['btn_continue'][language], callback_data=call_back_start + ':continue'),
            InlineKeyboardButton(text=messages['btn_save'][language], callback_data=call_back_start + ':save'))
        if is_first:
            inline_keyboard.row(
                InlineKeyboardButton(text=messages['btn_back'][language], callback_data=call_back_start + ':back'))
    bot.send_message(id_telegram, text, parse_mode="Markdown", reply_markup=inline_keyboard)


@async_dec()
def send_apartment(id_telegram, apartment_object, back_id, next_id, user, message_id=None, edit=False,
                   count_photos=None, is_saved=False):
    media_photos = []
    if apartment_object['images'] is None:
        empty_photo = open('./files/empty_photo.jpg', 'rb')
        media_photos.append(InputMediaPhoto(empty_photo))
    else:
        for i in range(len(apartment_object['images'])):
            if i < 5:
                media_photos.append(InputMediaPhoto(str(apartment_object['images'][i])))
            else:
                break

    category = '🏠  Апартаменти  🏠'
    if not apartment_object['category'] is None:
        if apartment_object['category'] == 'комната':
            category = '🚪  КІМНАТА' + '\n'
        elif apartment_object['category'] == 'квартира':
            category = '🏠  КВАРТИРА' + '\n'
        else:
            category = '🏠  ' + apartment_object['category'] + '  🏠' + '\n'

    price = '💰Ціна: не вказана 😔\n'
    if not apartment_object['price'] is None:
        price = '💰Ціна: ' + str(apartment_object['price']['value']) + ' ' + str(
            apartment_object['price']['currency']) + '\n'

    metro_room = 'Метро: невідоме 😔\n'
    if not apartment_object['location']['metro'] is None:
        if apartment_object['location']['metro']['name'] == '':
            metro_room = 'Метро: невідоме 😔\n'
        else:
            metro_room = 'Метро: ' + apartment_object['location']['metro']['name'] + '\n'

    location = '📍Адреса: невідома 😔\n'
    if not apartment_object['location']['address'] is None:
        if apartment_object['location']['address'] == '':
            '📍Адреса: невідома 😔\n'
        else:
            location = '📍Адреса: ' + apartment_object['location']['address'] + '\n'

    sub_location_name = 'Район: невідомий 😔\n'
    if not apartment_object['location']['subLocationName'] is None:
        sub_location_name = 'Район: ' + apartment_object['location']['subLocationName'] + '\n'

    count_rooms = 'Кімнат: невідомо 😔\n'
    if not apartment_object['rooms'] is None:
        count_rooms = 'Кімнат: ' + str(apartment_object['rooms']) + '\n'

    area = 'Площа: невідома 😔\n'
    if not apartment_object['area']['value'] is None:
        area = 'Площа: ' + str(apartment_object['area']['value']) + 'м²\n'

    floor = 'Поверх: невідомий 😔\n'
    if not apartment_object['floor'] is None:
        floor = 'Поверх: ' + str(apartment_object['floor']) + '\n'

    url_details = generator_telegraph.get_url_by_id_apartment(apartment_object["internalId"])

    media_photos[0].parse_mode = 'Markdown'
    media_photos[
        0].caption = f'{category + price + location + metro_room + sub_location_name + count_rooms + area + floor}' \
                     f'👉[ДЕТАЛЬНІШЕ]({url_details})👈'

    navigation = 'navigation'
    text_save_btn = messages['btn_navigation_save'][user['language']]
    if is_saved:
        navigation = 'navigation_save'
        text_save_btn = messages['btn_del_save'][user['language']]

    navigation_keyboard = InlineKeyboardMarkup()
    navigation_keyboard.row(InlineKeyboardButton(
        text=messages['btn_navigation_back'][user['language']],
        callback_data=f'{navigation}:{str(back_id)}:{str(len(media_photos))}'),
        InlineKeyboardButton(
            text=messages['btn_navigation_next'][user['language']],
            callback_data=f'{navigation}:{str(next_id)}:{str(len(media_photos))}'))
    navigation_keyboard.row(InlineKeyboardButton(
        text=text_save_btn,
        callback_data=f'{navigation}:save:{str(apartment_object["internalId"])}'),
        InlineKeyboardButton(
            text=messages['btn_send_apartm_help'][user['language']],
            callback_data=f'{navigation}:help:{str(apartment_object["internalId"])}')
    )

    if user['daysOfSubscription'] > 0:
        update_apartment_msg(id_telegram, edit, count_photos, message_id, media_photos, user, navigation_keyboard)
    else:
        if user['freeCounterSearch'] > 0:
            api.update_field_for_user(id_telegram, user['freeCounterSearch'] - 1, 'freeCounterSearch')
            update_apartment_msg(id_telegram, edit, count_photos, message_id, media_photos, user, navigation_keyboard)
        else:
            if edit:
                for i in range(count_photos + 1):
                    bot.delete_message(id_telegram, message_id - i)
            bot.send_message(id_telegram, messages['msg_end_5_free_apartments'][user['language']])
            pay_message(id_telegram, user)


@async_dec()
def update_apartment_msg(id_telegram, edit, count_photos, message_id, media_photos, user, navigation_keyboard):
    if edit:
        for i in range(count_photos + 1):
            bot.delete_message(id_telegram, message_id - i)
    bot.send_media_group(id_telegram, media_photos)
    bot.send_message(id_telegram, messages['msg_navigation'][user['language']],
                     reply_markup=navigation_keyboard)


print('Listening....')
count_restarts = 0
while True:
    try:
        bot.polling(none_stop=True)
    except:
        count_restarts = count_restarts + 1
        print(f'count_restarts = {count_restarts}')
        logging.error(sys.exc_info()[0])
        time.sleep(TIME_SLEEP)
