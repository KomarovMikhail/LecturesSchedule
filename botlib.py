from telebot import types


def generate_menu():
    inline_markup = types.InlineKeyboardMarkup()
    buttons = ['Показать расписание', 'Найти собеседника', 'Обновить профиль']
    for button in buttons:
        inline_markup.add(types.InlineKeyboardButton(text=button, callback_data=button))
    return inline_markup
