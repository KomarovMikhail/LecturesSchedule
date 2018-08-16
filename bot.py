# -*- coding: utf-8 -*-
from constants.config import *
import telebot
from sslib import get_nearest, get_faq, sort_key, SSHandler
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
from favlib import *
from exeptions.custom_exeptions import *
from estlib import EstimatesHandler
from orglib import AdminHandler


bot = telebot.TeleBot(TOKEN)
auth_handler = AuthHandler(DATABASE_URL)
advisor = Advisor()
n_handler = NotificationHandler()
up_handler = UpdatesHandler(SCHEDULE_PATH, CSV_URL)
ss_handler = SSHandler(CSV_URL)
est_handler = EstimatesHandler(DATABASE_URL)
admin_handler = AdminHandler(ADMIN_PASSWORD)

# Проверяет ближайшие доклады и отправляет напоминания за час до начала
scheduler = BackgroundScheduler()
scheduler.start()

# Проверяет расписание на обновления
updates = BackgroundScheduler()
updates.start()

create_favorite_db()


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
    print(auth_handler.get_all_ids())
    if len(users) == 0:
        bot.send_message(message.chat.id, "Нет зарегестрированных пользователей.")
    else:
        for user in users:
            text = str(user)
            bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['admin'])
def register_admin_first_step(message):
    try:
        admin_handler.add_user(message.chat.id)
        text = 'Введите пароль чтобы получить права администратора.'
        bot.send_message(message.chat.id, text)
    except AlreadyAdminError:
        text = 'Вы уже получили права администратора ранее.'
        bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: admin_handler.need_to_call(message.chat.id))
def register_admin_second_step(message):
    if admin_handler.try_login(message.chat.id, message.text):
        text = 'Вы успешно авторизировались и получили права администратора'
    else:
        text = 'Пароль неверный. Мы не можем выдать вам права администратора'
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: if_menu(message.text), content_types=['text'])
def menu(message):
    text = 'Что я могу для тебя сделать?'
    inline_markup = generate_menu()
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(func=lambda message: admin_handler.asking(message.chat.id), content_types=['text'])
def ask_admins(message):
    admin_handler.remove_asking(message.chat.id)
    profile = auth_handler.get_profile(message.chat.id)
    if profile is None:
        text = 'Сообщение администраторам от незарегистрированного пользователя.\n' + message.text
    else:
        text = 'Сообщение администраторам пользователя {0} (@{1}).\n'.format(profile[2], profile[1])
    mass_mailing(admin_handler.get_ids(), text, bot)
    bot.send_message(message.chat.id, 'Ваше сообщение доставлено организаторам.')


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

    if call.data == 'Показать расписание' or call.data == 'more_lectures':
        if call.data == 'Показать расписание':
            text = ['Расписание ближайших докладов:\n(Нажми {0}, чтобы добавить доклад в "избранное")'.format(FIRE)]
            bot.send_message(cid, text)
        try:
            nearest = ss_handler.get_lectures(cid)
            for l in nearest:
                text = 'Что: {0}\nКогда: {1}\nКто читает: {2}'.format(l['name'], l['start'], l['lecturer'])
                inline_markup = generate_lectures_list(l['id'])
                bot.send_message(cid, text, reply_markup=inline_markup)
            text = 'Жми "Еще доклады", если хочешь больше докладоов.'
            inline_markup = generate_more_lectures()
            bot.send_message(cid, text, reply_markup=inline_markup)
        except TimeError:
            text = "ОШИБКА!\nИнформация о времени начала некоторых докладах заполнена неверно, " \
                   "поэтому в данный момент мы не можем ее отобразить. " \
                   "Сообщение об ошибке уже перенаправлено организаторам. " \
                   "Попробуйте отправить запрос позже."
            bot.send_message(cid, text)
            mass_mailing(admin_handler.get_ids(), SPREADSHEET_ERROR_MESSAGE, bot)
        except FieldNumError:
            text = "ОШИБКА!\nИнформация о докладах еще не заполнена до конца, " \
                   "поэтому в данный момент мы не можем ее отобразить. " \
                   "Сообщение об ошибке уже перенаправлено организаторам. " \
                   "Попробуйте отправить запрос позже."
            bot.send_message(cid, text)
            mass_mailing(admin_handler.get_ids(), SPREADSHEET_ERROR_MESSAGE, bot)

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
        try:
            mark = est_handler.get_mark(int(lid))
            text = '{0} (Читает {1})\nМесто проведения: {2}\nВремя: {3}\n' \
                   'Краткое описание: {4}\nСредняя оценка доклада: {5}' \
                   ''.format(lecture['name'], lecture['lecturer'],
                             lecture['where'], lecture['start'], lecture['about'], mark)
        except NoEstimationsError:
            text = '{0} (Читает {1})\nМесто проведения: {2}\nВремя: {3}\n' \
                   'Краткое описание: {4}' \
                   ''.format(lecture['name'], lecture['lecturer'],
                             lecture['where'], lecture['start'], lecture['about'])
        bot.send_message(cid, text)

    elif call.data[:10] == 'add_to_fav':
        lid = call.data[10:]
        try:
            add_to_favorite(cid, lid)
            lecture = up_handler.get_lecture_by_id(lid)
            text = 'Доклад "{0}" добавлен в избранное.'.format(lecture['name'])
            bot.send_message(cid, text)
        except AlreadyAddedError:
            bot.send_message(cid, 'Этот доклад уже добавлен в избранное.')

    elif call.data[:12] == 'rem_from_fav':
        lid = call.data[12:]
        try:
            remove_from_favorite(cid, lid)
            lecture = up_handler.get_lecture_by_id(lid)
            text = 'Доклад "{0}" удален из избранного.'.format(lecture['name'])
            bot.send_message(cid, text)
        except AlreadyRemovedError:
            bot.send_message(cid, 'Этот доклад уже удален из избранного.')

    elif call.data[:8] == 'estimate':
        lid = call.data[8:]
        if not est_handler.already_estimated(cid, int(lid)):
            lecture = up_handler.get_lecture_by_id(lid)
            text = 'Оцените доклад "{0}" (Читает {1}) по шкале от 1 до 5.'.format(lecture['name'], lecture['lecturer'])
            inline_markup = generate_marks(lid)
            bot.send_message(cid, text, reply_markup=inline_markup)
        else:
            text = 'Вы уже поставили оценку этому докладу.'
            bot.send_message(cid, text)

    elif call.data[:4] == 'mark':
        values = call.data[4:].split(',')
        try:
            est_handler.estimate_lecture(cid, int(values[0]), int(values[1]))
            text = 'Спасибо за оценку доклада. Она поможет нам в дальнейшем развиваться и делать доклады лучше.'
        except AlreadyEstimatedError:
            text = 'Вы уже поставили оценку этому докладу.'
        bot.send_message(cid, text)

    elif call.data == 'Мое избранное':
        lids = select_by_id(cid)
        if len(lids) == 0:
            bot.send_message(cid, 'У вас пока нет избранных докладов.')
        else:
            bot.send_message(cid, 'Избранные доклады:\n'
                                  '(Нажми {0} чтобы уборать доклад из избранного)'.format(CROSS_MARK))
            lectures = up_handler.get_lectures_by_ids(lids)
            for l in lectures:
                text = 'Что: {0}\nКогда: {1}\nКто читает: {2}'.format(l['name'], l['start'], l['lecturer'])
                inline_markup = generate_favorite_list(l['id'])
                bot.send_message(cid, text, reply_markup=inline_markup)

    elif call.data == 'Задать вопрос организаторам':
        admin_handler.add_asking(cid)
        text = 'Ниже напишите свой вопрос. Мы перешлем его организаторам.'
        bot.send_message(cid, text)


def get_actual_schedule():
    try:
        nearest = get_nearest(CSV_URL)
    except TimeError:
        # mass_mailing(admin_handler.get_ids(), SPREADSHEET_ERROR_MESSAGE, bot)
        return
    except FieldNumError:
        # mass_mailing(admin_handler.get_ids(), SPREADSHEET_ERROR_MESSAGE, bot)
        return
    for item in nearest:
        n_handler.try_add_item(item)

    now = datetime.now()
    delta = timedelta(hours=1)
    ids = auth_handler.get_all_ids()

    for item in n_handler.get_data():
        time = sort_key(item)  # время начала доклада
        if now + delta > time and n_handler.need_to_send(item['id']):
            text = 'Напоминание:\nВ {0} состоится доклад "{1}".\n' \
                   'Не пропустите.'.format(item['start'], item['name'])
            inline_markup = generate_show_more(item['id'])
            for i in ids:
                bot.send_message(i, text, reply_markup=inline_markup)
            n_handler.set_flag_false(item['id'])
        if now > time:
            n_handler.rm_key(item['id'])


def check_updates():
    ids = auth_handler.get_all_ids()
    try:
        declined, added, changed = up_handler.get_updates()
    except SpreadSheetError:
        mass_mailing(admin_handler.get_ids(), SPREADSHEET_ERROR_MESSAGE, bot)
        return
    for item in declined:
        for i in ids:
            bot.send_message(i, item)
    for item in added:
        inline_markup = generate_show_more(item[1])
        for i in ids:
            bot.send_message(i, item[0], reply_markup=inline_markup)
    for item in changed:
        inline_markup = generate_show_more(item[1])
        for i in ids:
            bot.send_message(i, item[0], reply_markup=inline_markup)


scheduler.add_job(get_actual_schedule, 'interval', minutes=1)
updates.add_job(check_updates, 'interval', minutes=5)

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
