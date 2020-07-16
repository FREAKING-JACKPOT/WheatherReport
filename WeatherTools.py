import telebot
import requests
from telebot import types

url_base = "http://api.openweathermap.org/data/2.5/"


class WeatherTools:
    def __init__(self, appid, bot):
        """Получаем appid и бота"""
        self.appid = appid
        self.bot = bot

    def search_cities(self, city):
        """Получаем список городов"""
        request = requests.get(url_base + "find",
                               params={
                                   'q': city,
                                   'units': 'metric',
                                   'appid': self.appid
                               })
        return request.json()

    def current_wheather(self, city_id, chat_id):
        """Получаем информацию об определенном городе и отправляем пользователю ввиде сообщения"""
        request = requests.get(url_base + "weather",
                               params={
                                   'id': city_id,
                                   'units': 'metric',
                                   'appid': self.appid,
                                   'lang': 'ru'
                               })
        data = request.json()
        self.bot.send_message(
            chat_id, 'погода: {} \nтемпература: {:.0f} °C\n'.format(
                data['weather'][0]['description'], data['main']['temp']) +
            'минимальная температура: {:.0f} °C \n'.format(
                data['main']['temp_min']) +
            'максимальная температура: {:.0f} °C\n'.format(
                data['main']['temp_max']) +
            'скорость ветра: {} м/c\nдавление: {} гПа'.format(
                data['wind']['speed'], data['main']['pressure']))
        self.bot.send_message(
            chat_id,
            'Введите название населенного пункта.',
            reply_markup=types.ReplyKeyboardRemove(selective=False))

    def five_day_weather_forecast(self, city_id, chat_id):
        """Получаем погоду на 5 дней и отправляем её пользователю ввиде сообщения"""
        request = requests.get(url_base + "forecast",
                               params={
                                   'id': city_id,
                                   'units': 'metric',
                                   'lang': 'ru',
                                   'appid': self.appid
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
                format(day['dt_txt'], day['main']['temp'],
                       day['wind']['speed'], day['weather'][0]['description']))
        self.bot.send_message(chat_id, '\n'.join(msg))
        self.bot.send_message(
            chat_id,
            'Введите название населенного пункта.',
            reply_markup=types.ReplyKeyboardRemove(selective=False))
