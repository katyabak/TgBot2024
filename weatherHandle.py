import requests
from telebot import types
from database import load_user_state
from handlers import bot


# обработчик команды /weather
@bot.message_handler(commands=['weather'])
def handle_weather(message):
    # клавиатура для выбора действия
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Ввести город", callback_data="input_city"))
    keyboard.add(types.InlineKeyboardButton(text="Погода в моем городе", callback_data="weather_in_my_city"))

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


# обработчик нажатия кнопки для выбора действия при запросе погоды
@bot.callback_query_handler(func=lambda call: call.data in ["input_city", "weather_in_my_city"])
def handle_weather_action(call):
    if call.data == "input_city":
        bot.send_message(call.message.chat.id, "Введите город для просмотра погоды:")
        bot.register_next_step_handler(call.message, process_city_input)
    elif call.data == "weather_in_my_city":
        handle_weather_in_my_city(call.message)


# обработчик введенного пользователем города
def process_city_input(message):
    city = message.text
    handle_weather_for_city(message, city)


# обработчик вывода погоды в городе, указанном в информации о пользователе
def handle_weather_in_my_city(message):
    # Загружаем состояние пользователя
    user_state = load_user_state(message.chat.id)

    if user_state and user_state.user_info and "Город" in user_state.user_info:
        city = user_state.user_info["Город"]
        handle_weather_for_city(message, city)
    else:
        bot.send_message(message.chat.id,
                         "Извините, вы еще не ввели ваш город.\nВы можете написать ваш город в информацию о себе в "
                         "/settings.")


# обработка погоды для указанного города
def handle_weather_for_city(message, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=63fbcc00cf500cddf08641995ee9c4a0&units" \
          f"=metric&lang=ru"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        bot.send_message(message.chat.id,
                         f"Погода в выбранном городе ({city}): {weather_description}. Температура: {temperature}°C\n\n")
    else:
        bot.send_message(message.chat.id, "Извините, не удалось получить информацию о погоде для указанного города.")
