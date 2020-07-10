import telebot
import requests
import config
from telebot import types

bot = telebot.TeleBot(config.bot_token)
appid = config.appid


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    bot.send_message(
        message.chat.id, 'Привет,{}. Чтобы получить информацию о погоде, введи название населенного пункта в чат :)'.format(message.from_user.first_name))


@bot.message_handler(content_types=['text'])
def search(message):
    try:
        city = message.text
        request = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': city, 'units': 'metric', 'appid': appid})
        data = request.json()
        msg = []
        for city in enumerate(data['list']):
            msg.append('{}) {}, {}'.format(
                city[0]+1, city[1]['name'], city[1]['sys']['country']))
        bot.send_message(message.chat.id, '\n'.join(msg))
        msg = bot.send_message(
            message.chat.id, 'Введите номер населенного пункта')
        bot.register_next_step_handler(msg, city_request_check, data)
    except Exception as WrongName:
        bot.send_message(
            message.chat.id, 'Такого населенного пункта не существует. Убедитесь, что название населенного пункта введено правильно.')


def city_request_check(message, data):
    if(message.text.isdigit() and (int(message.text) <= len(data['list'])) and int(message.text) != 0):
        city_id = data['list'][int(message.text)-1]['id']
        keyboard = keyboard_maker()
        msg = bot.send_message(
            message.chat.id, 'Выберите функцию:', reply_markup=keyboard)
        bot.register_next_step_handler(msg, user_request, city_id)
    else:
        msg = bot.send_message(
            message.chat.id, 'Вы выбрали неправильный номер. Попробуйте ещё раз.')
        bot.register_next_step_handler(msg, city_request_check, data)


def user_request(message, city_id):
    if (message.text == 'Текущая погода'):
        current_wheather(city_id, message.chat.id)
    elif (message.text == 'Погода на 5 дней'):
        five_day_weather_forecast(city_id, message.chat.id)
    else:
        msg = bot.send_message(
            message.chat.id, 'Выбрана несуществующая функция. Попробуйте выбрать ещё раз.')
        bot.register_next_step_handler(msg, user_request, city_id)


def keyboard_maker():
    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    current_weather_button = types.KeyboardButton("Текущая погода")
    five_day_weather_forecast_button = types.KeyboardButton("Погода на 5 дней")
    keyboard.add(current_weather_button, five_day_weather_forecast_button)
    return keyboard


def current_wheather(city_id, chat_id):
    request = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': city_id, 'units': 'metric', 'appid': appid, 'lang': 'ru'})
    data = request.json()
    bot.send_message(chat_id, 'погода: {0} \nтемпература: {1:.0f} °C \nминимальная температура: {2:.0f} °C \nмаксимальная температура: {3: .0f} °C\nскорость ветра: {4} м/c\nдавление: {5} гПа'.format(
        data['weather'][0]['description'], data['main']['temp'], data['main']['temp_min'], data['main']['temp_max'], data['wind']['speed'], data['main']['pressure']))
    bot.send_message(chat_id, 'Введите название населенного пункта.',
                     reply_markup=types.ReplyKeyboardRemove(selective=False))


def five_day_weather_forecast(city_id, chat_id):
    request = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'appid': appid})
    data = request.json()
    msg = []
    tmp_day = None
    for day in data['list']:
        if (tmp_day != day['dt_txt'][8:10] or tmp_day == None):
            msg.append('\n'+day['dt_txt'][8:10]+'\n')
            tmp_day = day['dt_txt'][8:10]
        msg.append('{}, температура: {} °C, скорость ветра: {} м/c, погода: {}'.format(
            day['dt_txt'], day['main']['temp'], day['wind']['speed'], day['weather'][0]['description']))
    bot.send_message(chat_id, '\n'.join(msg))
    bot.send_message(chat_id, 'Введите название населенного пункта.',
                     reply_markup=types.ReplyKeyboardRemove(selective=False))


bot.polling()
