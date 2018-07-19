from telebot import types


def generate_menu():
    inline_markup = types.InlineKeyboardMarkup()
    buttons = ['Показать расписание', 'Найти собеседника', 'Обновить профиль']
    for button in buttons:
        inline_markup.add(types.InlineKeyboardButton(text=button, callback_data=button))
    return inline_markup


def make_auth_step(bot, message, client):
    if client.get_step() == 1:
        bot.send_message(message.chat.id, 'Имя: ' + message.text)
        client.increment_step()
        bot.send_message(message.chat.id, 'Кем ты работаешь?')
    if client.get_step() == 2:
        bot.send_message(message.chat.id, 'Место работы: ' + message.text)
        client.increment_step()
        bot.send_message(message.chat.id, 'Расскажи немного о себе и своих интересах')
    if client.get_step() == 3:
        bot.send_message(message.chat.id, 'Интересы: ' + message.text)
        client.clean_step()
        bot.send_message(message.chat.id, 'Спасибо! Я записал тебя в список участников')
