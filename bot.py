# -*- coding: utf-8 -*-
import config
import telebot
from sslib import get_nearest, download_spreadsheet, convert_to_xml
import os
from flask import Flask, request
import logging


bot = telebot.TeleBot(config.TOKEN)

# @server.route('/', methods=['GET', 'HEAD'])
# def index():
#     return ''
#
#
# @server.route(config.WEBHOOK_URL_PATH, methods=['POST'])
# def webhook():
#     if flask.request.headers.get('content-type') == 'application/json':
#         json_string = flask.request.get_data()
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_messages([update.message])
#         return ''
#     else:
#         flask.abort(403)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    text = 'Этот бот поможет тебе узнать о ближайших лекциях.\nЧтобы получить актуальное расписание введи /get'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["get"])
def get_schedule(message):
    text = ['Расписание ближайших лекций:\n------\n']

    download_spreadsheet(config.URL, config.XLSX_PATH)
    convert_to_xml(config.XLSX_PATH, config.XML_PATH)

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


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

server = Flask(__name__)


@server.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://voyage-livre-89482.herokuapp.com/bot")
    return "?", 200


if __name__ == '__main__':
    # bot.remove_webhook()
    # bot.set_webhook(url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
    #                 certificate=open(config.WEBHOOK_SSL_CERT, 'r'))
    # server.run(host=config.WEBHOOK_LISTEN,
    #            port=config.WEBHOOK_PORT,
    #            ssl_context=(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV),
    #            debug=True)
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
#     while True:
#         try:
#             bot.polling(none_stop=True)
#         except Exception:
#             pass

