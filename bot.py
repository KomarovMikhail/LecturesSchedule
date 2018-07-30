# -*- coding: utf-8 -*-
from config import *
import telebot
from sslib import get_nearest, get_faq
import os
from flask import Flask, request
import logging
from botlib import *
from authlib import AuthHandler
from advisor import Advisor
from apscheduler.schedulers.background import BackgroundScheduler


bot = telebot.TeleBot(TOKEN)
auth_handler = AuthHandler(DB_PATH)
advisor = Advisor()

scheduler = BackgroundScheduler()
scheduler.start()


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    main_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_markup.add("Меню")
    text = 'Этот бот поможет тебе узнать о ближайших лекциях.\nЧтобы получить актуальное расписание введи /get'
    bot.send_message(message.chat.id, text, reply_markup=main_markup)

    text = 'Что я могу для тебя сделать?'
    inline_markup = generate_menu()
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(commands=['test'])
def test_db(message):
    users = auth_handler.get_users()
    if len(users) == 0:
        bot.send_message(message.chat.id, "Нет зарегестрированных пользователей")
    else:
        for user in users:
            text = str(user)
            bot.send_message(message.chat.id, text)


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
    if auth_handler.is_in_queue(message.chat.id):
        bot.send_message(message.chat.id, "Извини, я тебя не понимаю. Попробуй еще раз.")
    else:
        auth_handler.make_step(message.chat.id, message, bot)


@bot.message_handler(content_types='photo')
def handle_photo(message):
    if auth_handler.is_in_queue(message.chat.id):
        bot.send_message(message.chat.id, "Извини, я тебя не понимаю. Попробуй еще раз.")
    else:
        auth_handler.make_step(message.chat.id, message, bot)
    if True:
        file_info = bot.get_file(message.photo[0].file_id)
        downloaded = bot.download_file(file_info.file_path)
        print(file_info.file_path, file_info.file_size)

        src = IMG_PATH + str(message.chat.id)
        with open(src, 'wb') as new_file:
            new_file.write(downloaded)
        bot.send_photo(message.chat.id, open(IMG_PATH + str(message.chat.id), 'rb'))
    # except Exception as e:
    #     bot.send_message(message.chat.id, e.args)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    print(call.data)
    cid = call.message.chat.id

    if call.data == 'Показать расписание':
        bot.send_message(cid, "Вот тебе расписание")

    elif call.data == 'Найти собеседника':
        bot.send_message(cid,
                         "Давай попробуем найти людей, с которыми тебе будет интересно пообщаться.\n"
                         "Нажимай \"+\", если человек интересен и я отправлю ему приглашение связаться с тобой.")
        if auth_handler.is_authorized(cid):
            p = auth_handler.get_participant(cid)
            if p is None:
                bot.send_message(cid, "Извини, я не могу найти тебе подходящего собеседника.")
            else:
                advisor.set_offer(cid, p[0])
                inline_markup = generate_answer_buttons()
                bot.send_message(cid, 'Имя: {0}\nГде работает: {1}\n'
                                 'Интересы: {2}\nUsername: @{3}'.format(p[2], p[3], p[4], p[1]),
                                 reply_markup=inline_markup)
        else:
            bot.send_message(cid, "Ты еще не заполнил информацию о себе.\n"
                             "Нажми \"Обновить профиль\" и пройди авторизацию.")

    elif call.data == '+':
        to_id = advisor.get_offer(cid)
        advisor.del_client(cid)
        p = auth_handler.get_profile(cid)
        text = 'Привет! Один из участников заинтересовался тобой. Держи некоторую информацию о нем:\n' \
               'Имя: {0}\nГде работает: {1}\nИнтересы: {2}\nUsername: {3}\n' \
               'Если этот участник тоже тебя заинтересовал, ' \
               'напиши ему в личные сообщения.'.format(p[2], p[3], p[4], p[1])
        # bot.send_message(to_id, text)
        # bot.send_message(cid, "Участнику отправлено приглашение связаться с тобой.")

    elif call.data == '-':
        pass

    elif call.data == 'Показать еще...':
        p = auth_handler.get_participant(cid)
        if p is None:
            bot.send_message(cid, "Извини, я не могу найти тебе подходящего собеседника.")
        else:
            advisor.set_offer(cid, p[0])
            inline_markup = generate_answer_buttons()
            bot.send_message(cid, 'Имя: {0}\nГде работает: {1}\n'
                                  'Интересы: {2}\nUsername: @{3}'.format(p[2], p[3], p[4], p[1]),
                             reply_markup=inline_markup)

    elif call.data == 'Обновить профиль':
        auth_handler.add_client(cid)
        auth_handler.make_step(cid, call.message, bot)

    elif call.data == 'Мой профиль':
        profile = auth_handler.get_profile(cid)
        if profile is None:
            text = 'Ты еще не заполнял информацию о себе. Чтобы исправить это нажми "Обновить профиль"'
        else:
            text = 'Имя: {0}\nГде работаешь: {1}\nИнтересы: {2}'.format(profile[2], profile[3], profile[4])
            bot.send_photo(cid, open(profile[5], 'rb'))
        bot.send_message(cid, text)

    elif call.data == 'FAQ':
        faq = get_faq(FAQ_URL)
        for q in faq:
            text = 'Вопрос: ' + q['question'] + '\n' + 'Ответ: ' + q['answer']
            bot.send_message(cid, text)


def get_actual_schedule():
    print('I do this every minute')


scheduler.add_job(get_actual_schedule, seconds=1)


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
