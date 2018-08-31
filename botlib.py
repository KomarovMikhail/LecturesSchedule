from telebot import types
from constants.emoji import *


def if_menu(text):
    if text == 'Меню' or text == 'меню' or text == 'Menu' or text == 'menu':
        return True
    else:
        return False


def main_menu_button():
    main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_markup.add("Меню")
    return main_markup


def skip_button(take_from_profile=False):
    skip_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    skip_markup.add("Пропустить")
    if take_from_profile:
        skip_markup.add("Взять из профиля")
    return skip_markup


def generate_menu():
    inline_markup = types.InlineKeyboardMarkup()
    buttons = [
        ('Показать расписание', CLIPBOARD),
        ('Найти собеседника', SPEECH_BALLOON),
        ('Обновить профиль', PENCIL),
        ('Сканировать визитку', MAGNIFYING_GLASS),
        ('Мой профиль', BUST),
        ('Мое избранное', FIRE),
        ('FAQ', QUESTION),
        ('Задать вопрос организаторам', ENVELOPE)
    ]
    for b in buttons:
        if b[0] == 'Сканировать визитку':
            inline_markup.add(types.InlineKeyboardButton(text=b[1] + b[0], url='http://qrs.ly/iw4uqj5'))
        else:
            inline_markup.add(types.InlineKeyboardButton(text=b[1] + b[0], callback_data=b[0]))
    return inline_markup


def generate_schedule_options():
    inline_markup = types.InlineKeyboardMarkup()
    data = [
        ('Полное расписание', 'Показать расписание(full)'),
        ('Идет сейчас', 'Показать расписание(current)'),
        ('Ближайние доклады', 'Показать расписание(upcoming)')
    ]
    for item in data:
        inline_markup.add(types.InlineKeyboardButton(text=item[0], callback_data=item[1]))
    return inline_markup


def generate_answer_buttons(pid):
    inline_markup = types.InlineKeyboardMarkup()
    b_1 = types.InlineKeyboardButton(text=THUMBS_UP, callback_data='like' + str(pid))
    b_2 = types.InlineKeyboardButton(text=THUMBS_DOWN, callback_data='dislike')
    b_3 = types.InlineKeyboardButton(text='Показать еще...', callback_data='more_users')
    inline_markup.add(b_1, b_2)
    inline_markup.add(b_3)
    return inline_markup


def generate_thumbs(cid):
    inline_markup = types.InlineKeyboardMarkup()
    b_1 = types.InlineKeyboardButton(text=THUMBS_UP, callback_data='agree' + str(cid))
    b_2 = types.InlineKeyboardButton(text=THUMBS_DOWN, callback_data='disagree')
    inline_markup.add(b_1, b_2)
    return inline_markup


def generate_more_users():
    inline_markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Показать еще...', callback_data='more_users')
    inline_markup.add(button)
    return inline_markup


def generate_lectures_list(lid, already_added=False):
    inline_markup = types.InlineKeyboardMarkup()
    callback_data_1 = 'get_full_info{0}'.format(lid)
    callback_data_3 = 'estimate{0}'.format(lid)
    b_1 = types.InlineKeyboardButton(text='Подробнее...', callback_data=callback_data_1)
    if already_added:
        callback_data_2 = 'rem_from_fav{0}'.format(lid)
        b_2 = types.InlineKeyboardButton(text=CROSS_MARK, callback_data=callback_data_2)
    else:
        callback_data_2 = 'add_to_fav{0}'.format(lid)
        b_2 = types.InlineKeyboardButton(text=FIRE, callback_data=callback_data_2)
    b_3 = types.InlineKeyboardButton(text='Оценить', callback_data=callback_data_3)
    inline_markup.add(b_1, b_2, b_3)
    return inline_markup


def generate_favorite_list(lid):
    inline_markup = types.InlineKeyboardMarkup()
    callback_data_1 = 'get_full_info{0}'.format(lid)
    callback_data_2 = 'rem_from_fav{0}'.format(lid)
    callback_data_3 = 'estimate{0}'.format(lid)
    b_1 = types.InlineKeyboardButton(text='Подробнее...', callback_data=callback_data_1)
    b_2 = types.InlineKeyboardButton(text=CROSS_MARK, callback_data=callback_data_2)
    b_3 = types.InlineKeyboardButton(text='Оценить', callback_data=callback_data_3)
    inline_markup.add(b_1, b_2, b_3)
    return inline_markup


def generate_esimate_lecture(lid):
    inline_markup = types.InlineKeyboardMarkup()
    callback_data_1 = 'get_full_info{0}'.format(lid)
    callback_data_2 = 'estimate{0}'.format(lid)
    b_1 = types.InlineKeyboardButton(text='Подробнее...', callback_data=callback_data_1)
    b_2 = types.InlineKeyboardButton(text='Оценить', callback_data=callback_data_2)
    inline_markup.add(b_1, b_2)
    return inline_markup


def generate_show_more(lid):
    inline_markup = types.InlineKeyboardMarkup()
    callback_data = 'get_full_info{0}'.format(lid)
    button = types.InlineKeyboardButton(text='Подробнее...', callback_data=callback_data)
    inline_markup.add(button)
    return inline_markup


def generate_more_lectures():
    inline_markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Еще доклады...', callback_data='Показать расписание(more)')
    inline_markup.add(button)
    return inline_markup


def generate_marks(lid):
    inline_markup = types.InlineKeyboardMarkup()
    marks = [('1', ONE), ('2', TWO), ('3', THREE), ('4', FOUR), ('5', FIVE)]
    buttons = []
    for mark in marks:
        buttons.append(types.InlineKeyboardButton(text=mark[1], callback_data='mark' + lid + ',' + mark[0]))
    inline_markup.add(buttons[4], buttons[3], buttons[2])
    inline_markup.add(buttons[1], buttons[0])
    return inline_markup


def mass_mailing(cids, text, bot):
    for i in cids:
        bot.send_message(i, text)
