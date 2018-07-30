from telebot import types


def generate_menu():
    inline_markup = types.InlineKeyboardMarkup()
    buttons = ['Показать расписание', 'Найти собеседника', 'Обновить профиль', 'Мой профиль', 'FAQ']
    for button in buttons:
        inline_markup.add(types.InlineKeyboardButton(text=button, callback_data=button))
    return inline_markup


def generate_answer_buttons():
    inline_markup = types.InlineKeyboardMarkup()
    b_1 = types.InlineKeyboardButton(text='+', callback_data='+')
    b_2 = types.InlineKeyboardButton(text='-', callback_data='-')
    b_3 = types.InlineKeyboardButton(text='Показать еще...', callback_data='Показать еще...')
    inline_markup.add(b_1, b_2)
    inline_markup.add(b_3)
    return inline_markup

