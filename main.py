import telebot
import WeatherTools
import config
import keyboards
import sqldb
from time import sleep
from threading import Thread
from telebot import types

bot = telebot.TeleBot(config.bot_token)
keyboard = keyboards.KeyboardBuilder()
weather = WeatherTools.WeatherTools(config.appid, bot, keyboard)
database = sqldb.db('database.db')


def sheduled_msg():
    """Рассылка каждый час для подписчиков"""
    while True:
        sleep(3600)
        subs = database.get_subs()
        for sub in subs:
            weather.current_wheather(sub[3], sub[1], type='sheduled')


shedule_thread = Thread(target=sheduled_msg)
shedule_thread.start()


@bot.message_handler(commands=['start'])
def start_message(message):
    """Принимает команду start и отправляет информацию о боте"""
    bot.send_message(
        message.chat.id,
        'Привет,{}. Чтобы получить информацию о погоде'.format(
            message.from_user.first_name) +
        ', введи название населенного пункта в чат, выбирите город из предложенного списка и нужное действие.'
        + ' Для информации о командах /commands')


@bot.message_handler(commands=['commands'])
def commands_list(message):
    """Показывает лист команд бота"""
    bot.send_message(
        message.chat.id,
        '/start - информация о боте\n' + '/unsub-отписка от рассылки\n' +
        '/sub и название города -подписка на рассылку\n')


@bot.message_handler(commands=['unsub'])
def unsub(message):
    """Отписка от рассылки"""
    if database.sub_exists(message.from_user.id) == True:
        database.delete_sub(message.from_user.id)
        bot.send_message(message.chat.id, 'Вы успешно отписались от рассылки!')
    else:
        bot.send_message(message.chat.id, 'Но у вас её нет!')


@bot.message_handler(commands=['sub'])
def subscribe(message):
    """Подписка на рассылку"""
    if database.sub_exists(message.from_user.id) == False:
        data = weather.search_cities(message.text[5:])
        if data['cod'] != '400' and data['count'] != 0:
            msg = weather.list_maker(data, message.chat.id)
            bot.register_next_step_handler(msg,
                                           city_request_check,
                                           data,
                                           type='sub')
        else:
            bot.send_message(
                message.chat.id,
                'Я не знаю такого города. Отмена операции подписки')
    else:
        bot.send_message(message.chat.id, 'Увас уже есть подписка!')


@bot.message_handler(content_types=['text'])
def search(message):
    """Принимает названия города, выводит список существующих городов, переходит к выбору города из списка"""
    data = weather.search_cities(message.text)
    if data['cod'] != '400' and data['count'] != 0:
        msg = weather.list_maker(data, message.chat.id)
        bot.register_next_step_handler(msg, city_request_check, data)
    else:
        bot.send_message(
            message.chat.id,
            'Я не знаю такого города. Пожалуйста введите город повторно.')


def city_request_check(message, data, type='requiest'):
    """Проверяет на правильость выбора города из списка и переходит к выбору функции """
    if message.text.isdigit() and int(message.text) <= len(
            data['list']) and int(message.text) != 0:
        city_id = data['list'][int(message.text) - 1]['id']
        if (type == 'requiest'):
            msg = bot.send_message(message.chat.id,
                                   'Выберите функцию:',
                                   reply_markup=keyboard.mode_keyboard_maker())
            bot.register_next_step_handler(msg, user_request, city_id)
        elif (type == 'sub'):
            database.add_sub(message.from_user.id, city_id)
            bot.send_message(
                message.chat.id,
                'Подписка оформлена',
            )
    else:
        if (type == 'requiest'):
            bot.send_message(
                message.chat.id,
                'Вы выбрали неправильный номер. Возвращение к выбору города.',
                reply_markup=types.ReplyKeyboardRemove(selective=False))
        elif (type == 'sub'):
            bot.send_message(
                message.chat.id,
                'Вы выбрали неправильный номер. Отмена операции подписки.',
                reply_markup=types.ReplyKeyboardRemove(selective=False))


def user_request(message, city_id):
    """Проверяет на существование функции и запускает функцию """
    if (message.text == 'Текущая погода'):
        weather.current_wheather(city_id, message.chat.id)
    elif (message.text == 'Погода на 5 дней'):
        weather.five_day_weather_forecast(city_id, message.chat.id)
    else:
        bot.send_message(
            message.chat.id,
            'Выбрана несуществующая функция.Возвращение к выбору города',
            reply_markup=types.ReplyKeyboardRemove(selective=False))


bot.polling()
