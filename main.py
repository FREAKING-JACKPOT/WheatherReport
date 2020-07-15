import telebot
import WeatherTools
import config
import keyboards
from telebot import types

bot = telebot.TeleBot(config.bot_token)


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        'Привет,{}. Чтобы получить информацию о погоде, введи название населенного пункта в чат :)'
        .format(message.from_user.first_name))


@bot.message_handler(content_types=['text'])
def search(message):
    city = message.text
    data = WeatherTools.search_cities(message.text)
    try:
        msg = []
        for city in enumerate(data['list']):
            msg.append('{}) {}, {}'.format(city[0] + 1, city[1]['name'],
                                           city[1]['sys']['country']))
        bot.send_message(message.chat.id, '\n'.join(msg))
        msg = bot.send_message(
            message.chat.id,
            'Введите номер населенного пункта',
            reply_markup=keyboards.cities_list_keyboard_maker(len(
                data['list'])))
        bot.register_next_step_handler(msg, city_request_check, data)
    except Exception:
        bot.send_message(
            message.chat.id,
            'Я не знаю такого города. Пожалуйста введите город повторно.')


def city_request_check(message, data):
    if message.text.isdigit() and int(message.text) <= len(
            data['list']) and int(message.text) != 0:
        city_id = data['list'][int(message.text) - 1]['id']
        msg = bot.send_message(message.chat.id,
                               'Выберите функцию:',
                               reply_markup=keyboards.mode_keyboard_maker())
        bot.register_next_step_handler(msg, user_request, city_id)
    else:
        msg = bot.send_message(
            message.chat.id,
            'Вы выбрали неправильный номер. Попробуйте ещё раз.')
        bot.register_next_step_handler(msg, city_request_check, data)


def user_request(message, city_id):
    if (message.text == 'Текущая погода'):
        WeatherTools.current_wheather(bot, city_id, message.chat.id)
    elif (message.text == 'Погода на 5 дней'):
        WeatherTools.five_day_weather_forecast(bot, city_id, message.chat.id)
    else:
        msg = bot.send_message(
            message.chat.id,
            'Выбрана несуществующая функция. Попробуйте выбрать ещё раз.')
        bot.register_next_step_handler(msg, user_request, city_id)


bot.polling()
