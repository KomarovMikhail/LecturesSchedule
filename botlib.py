from telebot import types
from emoji import *


def generate_menu():
    inline_markup = types.InlineKeyboardMarkup()
    buttons = [
        ['Показать расписание', CLIPBOARD],
        ['Найти собеседника', SPEECH_BALLOON],
        ['Обновить профиль', PENCIL],
        ['Мой профиль', BUST],
        ['Мое избранное', FIRE],
        ['FAQ', QUESTION]
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


def generate_lectures_list(lecture):
    inline_markup = types.InlineKeyboardMarkup()
    callback_data_1 = 'get_full_info{0}'.format(lecture['id'])
    callback_data_2 = 'add_to_fav{0}'.format(lecture['id'])
    b_1 = types.InlineKeyboardButton(text='Подробнее...', callback_data=callback_data_1)
    b_2 = types.InlineKeyboardButton(text=FIRE, callback_data=callback_data_2)
    inline_markup.add(b_1, b_2)
    return inline_markup

