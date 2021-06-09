import time

import telebot
import config
from telebot import types

from db import users_database, courses_evaluation

bot = telebot.TeleBot(config.TOKEN)

first_button = "Проверка оценок"
second_button = "Расписание рубежного контроля"

username = {
    'login': '',
    'password': '',
    'course': ''
}

@bot.message_handler(commands=['start'])
def welcome(message):
    sti = open('static/welcome_logo.jpeg', 'rb')
    bot.send_sticker(message.chat.id, sti)

    bot.send_message(
        message.chat.id,
        f"Добро пожаловать, <b>{message.from_user.username}</b>!\nЯ - <b>{bot.get_me().first_name}</b>, "
        "бот созданный для проверки твоих оценок.",
        parse_mode='html'
    )
    time.sleep(1)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(first_button)
    item2 = types.KeyboardButton(second_button)

    markup.add(item1, item2)

    bot.send_message(message.chat.id, 'Выберите интересующую Вас рубрику', reply_markup=markup)



@bot.message_handler(content_types=['text'])
def check_evaluation(message):
    if message.chat.type == 'private':
        if message.text == first_button:
            send_login_and_password(message)
        if message.text == second_button:
            ...

def auth(message):
    data = message.text.split() # создаем список ['логин', 'пароль']
    check = list(
        filter(
            lambda x: x["username"] == (data[0]) and x['password'] == (data[1]), users_database
        )
    )
    if not check: # если такой комбинации не существует, ждём команды /start Опять
        yes_button = types.KeyboardButton(first_button)
        no_button = types.KeyboardButton('Нет')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(yes_button, no_button)

        bot.send_message(message.chat.id, f'Неправильно введен логин\пароль. Попробуем снова?', reply_markup=markup)
        check_evaluation(message)


    else: # а если существует, переходим к следующему шагу
        username['login'] = data[0]
        username['password'] = data[1]
        # keyboard
        markup = types.InlineKeyboardMarkup(row_width=6)
        button1 = types.InlineKeyboardButton('1 курс', callback_data='course1')
        button2 = types.InlineKeyboardButton('2 курс', callback_data='course2')
        button3 = types.InlineKeyboardButton('3 курс', callback_data='course3')
        button4 = types.InlineKeyboardButton('4 курс', callback_data='course4')

        markup.add(button1, button2, button3, button4)

        bot.send_message(message.chat.id, 'Логин введен верно. \n Выберите курс', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
        if call.message:
            for i in courses_evaluation:
                if i['username'] == username['login'] and bool(i["evaluation"][call.data]):
                    username['course'] = call.data

                    bot.send_message(
                        call.message.chat.id,
                        f'Ваши оценки за курс:\n'
                        f'РК №1 - {i["evaluation"][username["course"]]["1"]} %\n'
                        f'РК №2 - {i["evaluation"][username["course"]]["2"]} %\n'
                        f'РК №3 - {i["evaluation"][username["course"]]["3"]} %\n'
                        f'РК №4 - {i["evaluation"][username["course"]]["4"]} %'
                    )
                    # markup = types.ReplyKeyboardMarkup(row_width=4)
                    # button1 = types.KeyboardButton('1 РК')
                    # button2 = types.KeyboardButton('2 РК')
                    # button3 = types.KeyboardButton('3 РК')
                    # button4 = types.KeyboardButton('4 РК')
                    #
                    # markup.add(button1, button2, button3, button4)

                    # bot.send_message(call.message.chat.id, 'Выберите номер рубежного контроля', reply_markup=markup)




# @bot.message_handler(content_types=['text'])
# def message_handler(message):
#             print('ya tut')
#             for i in courses_evaluation:
#                 print([username['course']])
#                 if i['username'] == username['login'] and i["evaluation"][username['course']][str(4)]:
#                     bot.send_message(
#                         message.chat.id, f'Ваши оценка за {username["course"]} курс, РК №{} - {i["evaluation"][username["course"][call.data]]}'
#                     )



def send_login_and_password(message):
    msg = bot.send_message(message.chat.id, 'Отправь мне логин и пароль через пробел')
    bot.register_next_step_handler(msg, auth)


bot.polling(none_stop=True)