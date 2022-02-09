import api
import json

from telebot.util import async_dec

messages = json.load(open('./static/messages_v2.json', encoding='utf-8'))


@async_dec()
def statistics_message(bot, message):
    chat_id = message.chat.id
    stat = api.get_statistics()
    user = api.get_user(chat_id)
    bot.send_message(chat_id, f'{messages["messages"]["statistics_all"][user["language"]]}{stat["allUsers"]}\n'
                              f'{messages["messages"]["statistics_day"][user["language"]]}{stat["forDay"]}\n'
                              f'{messages["messages"]["statistics_week"][user["language"]]}{stat["forWeek"]}\n'
                              f'{messages["messages"]["statistics_month"][user["language"]]}{stat["forMonth"]}')


@async_dec()
def offer_message(bot, chat_id):
    bot.send_message(chat_id, 'https://roomsua.me/#/oferta')