# -*- coding: utf-8 -*-
from config import *
import telebot
from sslib import get_nearest
import os
from flask import Flask, request
import logging
from botlib import *
from authlib import AuthHandler


bot = telebot.TeleBot(TOKEN)
auth_handler = AuthHandler(DB_PATH)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    main_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_markup.add("Меню")
    text = 'Этот бот поможет тебе узнать о ближайших лекциях.\nЧтобы получить актуальное расписание введи /get'
    bot.send_message(message.chat.id, text, reply_markup=main_markup)

    text = 'Что я могу для тебя сделать?'
    inline_markup = generate_menu()
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(commands=["get"])
def get_schedule(message):
    text = ['Расписание ближайших лекций:\n------\n']

    nearest = get_nearest(CSV_URL)
    for lecture in nearest:
        buf_text = 'Что: {0}.\nКогда: {1}.\nКто ведет: {2}\n------\n'.format(lecture['name'],
                                                                             lecture['date'] + ' в ' + lecture['start'],
                                                                             lecture['lecturer'])
        text.append(buf_text)
    text = ''.join(text)
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.text == 'Меню', content_types=['text'])
def menu(message):
    text = 'Что я могу для тебя сделать?'
    inline_markup = generate_menu()
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(content_types=["text"])
def unknown_messages(message):
    if auth_handler.is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Извини, я тебя не понимаю. Попробуй еще раз.")
    else:
        auth_handler.make_step(message.chat.id, message, bot)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    print(call.data)
    if call.data == 'Показать расписание':
        bot.send_message(call.message.chat.id, "Вот тебе расписание")
    if call.data == 'Найти собеседника':
        bot.send_message(call.message.chat.id, "Вот тебе собеседник")
    if call.data == 'Обновить профиль':
        auth_handler.add_client(call.message.chat.id)
        auth_handler.make_step(call.message.chat.id, call.message, bot)


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

server = Flask(__name__)


@server.route("/" + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://" + APP_NAME + "/" + TOKEN)
    return "!", 200


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
