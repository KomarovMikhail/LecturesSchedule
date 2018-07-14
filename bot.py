# -*- coding: utf-8 -*-
import config
import telebot
from sslib import get_nearest

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=["get"])
def get_schedule(message):
    text = ['Расписание ближайших лекций:\n------\n']

    nearest = get_nearest(config.XML_PATH)
    for lecture in nearest:
        buf_text = 'Что: {0}.\nКогда: {1}.\nКто ведет: {2}\n------\n'.format(lecture['name'],
                                                                             lecture['date'] + ' в ' + lecture['start'],
                                                                             lecture['lecturer'])
        text.append(buf_text)
    text = ''.join(text)
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=["text"])
def unknown_messages(message):
    bot.send_message(message.chat.id, "Sorry, I don't understand you, i'm just a machine :-(")


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            pass

