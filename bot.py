# -*- coding: utf-8 -*-
from constants.config import *
import telebot
from sslib import get_nearest, get_faq, sort_key
import os
from flask import Flask, request
import logging
from botlib import *
from authlib import AuthHandler
from advisor import Advisor
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from nothandler import NotificationHandler
from uplib import UpdatesHandler
from constants.emoji import *
import psycopg2
from constants.queries import *


bot = telebot.TeleBot(TOKEN)
auth_handler = AuthHandler(DB_PATH)
advisor = Advisor()
n_handler = NotificationHandler()
up_handler = UpdatesHandler(SCHEDULE_PATH, CSV_URL)

scheduler = BackgroundScheduler()
scheduler.start()

updates = BackgroundScheduler()
updates.start()

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
#
# cursor = conn.cursor()
#
# cursor.execute(CREATE)
# cursor.execute(INSERT.format("Some another message"))
# conn.commit()
#
# cursor.execute(SELECT)
# rows = cursor.fetchall()
# for msg in rows:
#     print(msg[0])
#
# cursor.execute(DROP)
# conn.commit()
#
# conn.close()


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
        # bot.send_photo(message.chat.id, open(IMG_PATH + str(message.chat.id), 'rb'))
    # except Exception as e:
    #     bot.send_message(message.chat.id, e.args)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    print(call.data)
    cid = call.message.chat.id

    if call.data == 'Показать расписание':
        text = ['Расписание ближайших докладов:\n(Нажми {0}, чтобы добавить доклад в "избранное")'.format(FIRE)]
        bot.send_message(cid, text)
        nearest = get_nearest(CSV_URL)
        for l in nearest:
            text = 'Что: {0}\nКогда: {1}\nКто читает: {2}'.format(l['name'], l['start'], l['lecturer'])
            inline_markup = generate_lectures_list(l)
            bot.send_message(cid, text, reply_markup=inline_markup)

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

    elif call.data[:13] == 'get_full_info':
        lid = call.data[13:]
        lecture = up_handler.get_lecture_by_id(lid)
        print(lecture)
        # добавить описание и отправку сообщения

    elif call.data[:10] == 'add_to_fav':
        lid = call.data[10:]
        print('Got id: ' + lid)


def get_actual_schedule():
    nearest = get_nearest(CSV_URL)
    for item in nearest:
        n_handler.try_add_item(item)

    now = datetime.now()
    delta = timedelta(hours=1)
    ids = auth_handler.get_all_ids()

    for item in n_handler.get_data():
        time = sort_key(item)  # время начала доклада
        if now + delta > time and n_handler.need_to_send(item['id']):
            text = 'Напоминание:\nВ {0} состоится доклад "{1}".\nЛектор: {2}.\n' \
                   'Не пропустите.'.format(item['start'], item['name'], item['lecturer'])
            for i in ids:
                bot.send_message(i, text)
            n_handler.set_flag_false(item['id'])
        if now > time:
            n_handler.rm_key(item['id'])


def check_updates():
    ids = auth_handler.get_all_ids()
    new = up_handler.get_updates()
    for text in new:
        for i in ids:
            bot.send_message(i, text)


scheduler.add_job(get_actual_schedule, 'interval', minutes=1)
updates.add_job(check_updates, 'interval', minutes=1)

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
