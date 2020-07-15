import telebot
import requests
import config
from telebot import types

appid = config.appid
url_base = "http://api.openweathermap.org/data/2.5/"


def search_cities(city):
    request = requests.get(url_base + "find",
                           params={
                               'q': city,
                               'units': 'metric',
                               'appid': appid
                           })
    return request.json()


def current_wheather(bot, city_id, chat_id):
    request = requests.get(url_base + "weather",
                           params={
                               'id': city_id,
                               'units': 'metric',
                               'appid': appid,
                               'lang': 'ru'
                           })
    data = request.json()
    bot.send_message(
        chat_id, 'погода: {} \nтемпература: {:.0f} °C\n'.format(
            data['weather'][0]['description'], data['main']['temp']) +
        'минимальная температура: {:.0f} °C \n'.format(
            data['main']['temp_min']) +
        'максимальная температура: {:.0f} °C\n'.format(
            data['main']['temp_max']) +
        'скорость ветра: {} м/c\nдавление: {} гПа'.format(
            data['wind']['speed'], data['main']['pressure']))
    bot.send_message(chat_id,
                     'Введите название населенного пункта.',
                     reply_markup=types.ReplyKeyboardRemove(selective=False))


def five_day_weather_forecast(bot, city_id, chat_id):
    request = requests.get(url_base + "forecast",
                           params={
                               'id': city_id,
                               'units': 'metric',
                               'lang': 'ru',
                               'appid': appid
                           })
    data = request.json()
    msg = []
    tmp_day = None
    for day in data['list']:
        if (tmp_day != day['dt_txt'][8:10] or tmp_day is None):
            msg.append('\n' + day['dt_txt'][8:10] + '\n')
            tmp_day = day['dt_txt'][8:10]
        msg.append(
            '{}, температура: {} °C, скорость ветра: {} м/c, погода: {}'.
            format(day['dt_txt'], day['main']['temp'], day['wind']['speed'],
                   day['weather'][0]['description']))
    bot.send_message(chat_id, '\n'.join(msg))
    bot.send_message(chat_id,
                     'Введите название населенного пункта.',
                     reply_markup=types.ReplyKeyboardRemove(selective=False))