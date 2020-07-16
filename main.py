import telebot
import WeatherTools
import config
import keyboards
from telebot import types

bot = telebot.TeleBot(config.bot_token)
weather = WeatherTools.WeatherTools(config.appid, bot)
keyboard = keyboards.KeyboardBuilder()


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    """Принимает команды help и start и отправляет информацию о боте"""
    bot.send_message(
        message.chat.id,
        'Привет,{}. Чтобы получить информацию о погоде'.format(
            message.from_user.first_name) +
        ', введи название населенного пункта в чат :)')


@bot.message_handler(content_types=['text'])
def search(message):
    """Принимает названия города, выводит список существующих городов, переходит к выбору города из списка"""
    data = weather.search_cities(message.text)
    if data['cod'] != '400' and data['count'] != 0:
        msg = []
        for city in enumerate(data['list']):
            msg.append('{}) {}, {}'.format(city[0] + 1, city[1]['name'],
                                           city[1]['sys']['country']))
        bot.send_message(message.chat.id, '\n'.join(msg))
        msg = bot.send_message(
            message.chat.id,
            'Выберите номер населенного пункта изсписка.',
            reply_markup=keyboard.cities_list_keyboard_maker(len(
                data['list'])))
        bot.register_next_step_handler(msg, city_request_check, data)
    else:
        bot.send_message(
            message.chat.id,
            'Я не знаю такого города. Пожалуйста введите город повторно.')


def city_request_check(message, data):
    """Проверяет на правильость выбора города из списка и переходит к выбору функции """
    if message.text.isdigit() and int(message.text) <= len(
            data['list']) and int(message.text) != 0:
        city_id = data['list'][int(message.text) - 1]['id']
        msg = bot.send_message(message.chat.id,
                               'Выберите функцию:',
                               reply_markup=keyboard.mode_keyboard_maker())
        bot.register_next_step_handler(msg, user_request, city_id)
    else:
        msg = bot.send_message(
            message.chat.id,
            'Вы выбрали неправильный номер. Попробуйте ещё раз.')
        bot.register_next_step_handler(msg, city_request_check, data)


def user_request(message, city_id):
    """Проверяет на существование функции и запускает функцию """
    if (message.text == 'Текущая погода'):
        weather.current_wheather(city_id, message.chat.id)
    elif (message.text == 'Погода на 5 дней'):
        weather.five_day_weather_forecast(city_id, message.chat.id)
    else:
        msg = bot.send_message(
            message.chat.id,
            'Выбрана несуществующая функция. Попробуйте выбрать ещё раз.')
        bot.register_next_step_handler(msg, user_request, city_id)


bot.polling()
