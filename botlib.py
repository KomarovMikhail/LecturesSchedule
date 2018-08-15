from telebot import types
from constants.emoji import *


def if_menu(text):
    if text == 'Меню' or text == 'меню' or text == 'Menu' or text == 'menu':
        return True
    else:
        return False


def generate_menu():
    inline_markup = types.InlineKeyboardMarkup()
    buttons = [
        ('Показать расписание', CLIPBOARD),
        ('Найти собеседника', SPEECH_BALLOON),
        ('Обновить профиль', PENCIL),
        ('Мой профиль', BUST),
        ('Мое избранное', FIRE),
        ('FAQ', QUESTION)
    ]
    for b in buttons:
        inline_markup.add(types.InlineKeyboardButton(text=b[1] + b[0], callback_data=b[0]))
    return inline_markup


def generate_answer_buttons():
    inline_markup = types.InlineKeyboardMarkup()
    b_1 = types.InlineKeyboardButton(text='+', callback_data='+')
    b_2 = types.InlineKeyboardButton(text='-', callback_data='-')
    b_3 = types.InlineKeyboardButton(text='Показать еще...', callback_data='Показать еще...')
    inline_markup.add(b_1, b_2)
    inline_markup.add(b_3)
    return inline_markup


def generate_lectures_list(lid):
    inline_markup = types.InlineKeyboardMarkup()
    callback_data_1 = 'get_full_info{0}'.format(lid)
    callback_data_2 = 'add_to_fav{0}'.format(lid)
    callback_data_3 = 'estimate{0}'.format(lid)
    b_1 = types.InlineKeyboardButton(text='Подробнее...', callback_data=callback_data_1)
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


def generate_show_more(lid):
    inline_markup = types.InlineKeyboardMarkup()
    callback_data = 'get_full_info{0}'.format(lid)
    button = types.InlineKeyboardButton(text='Подробнее...', callback_data=callback_data)
    inline_markup.add(button)
    return inline_markup


def generate_more_lectures():
    inline_markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Еще доклады...', callback_data='more_lectures')
    inline_markup.add(button)
    return inline_markup


def generate_marks(lid):
    inline_markup = types.InlineKeyboardMarkup()
    marks = ['1', '2', '3', '4', '5']
    buttons = []
    for mark in marks:
        buttons.append(types.InlineKeyboardButton(text=mark, callback_data='mark' + lid + ',' + mark))
    inline_markup.add(buttons[4], buttons[3], buttons[2])
    inline_markup.add(buttons[1], buttons[0])
    return inline_markup
