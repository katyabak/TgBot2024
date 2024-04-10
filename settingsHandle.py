from database import save_user_state, load_user_state
from telebot import types
from handlers import bot
from newsHandle import categories


# обработчик команды /settings
@bot.message_handler(commands=['settings'])
def handle_settings(message):
    current_command = message.text.split()[0]

    user_state = load_user_state(message.chat.id)

    # клавиатура для выбора действия
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton(text="Изменить никнейм", callback_data="change_nickname"))

    keyboard.add(types.InlineKeyboardButton(text="Изменить информацию о себе", callback_data="change_info"))

    keyboard.add(types.InlineKeyboardButton(text="Выбрать любимую категорию", callback_data="select_favorite_category"))

    # если у пользователя уже есть выбранная любимая категория
    if user_state and user_state.selected_settings:
        keyboard.add(types.InlineKeyboardButton(text="Убрать любимую категорию", callback_data="remove_news_category"))

    # сохраняет текущую команду пользователя в БД
    save_user_state(message.chat.id, current_command=current_command)

    # проверяем, есть ли уже сохраненные настройки у пользователя
    if user_state and user_state.current_command == '/settings':
        # если есть, продолжаем с уже существующими настройками
        bot.send_message(message.chat.id, "Что вы хотите изменить в настройках?", reply_markup=keyboard)
    else:
        # если нет, предлагаем пользователю настроить параметры заново
        bot.send_message(message.chat.id, "Добро пожаловать в настройки! Что вы хотите изменить в настройках?",
                         reply_markup=keyboard)


# обработчик нажатия кнопки для изменения никнейма
@bot.callback_query_handler(func=lambda call: call.data == "change_nickname")
def change_nickname(call):
    bot.send_message(call.message.chat.id, "Введите ваш новый никнейм:")
    bot.register_next_step_handler(call.message, process_nickname_input)


# обработчик введенного пользователем нового никнейма
def process_nickname_input(message):
    user_id = message.chat.id
    new_nickname = message.text

    # обновляю информацию о пользователе
    user_info = load_user_state(user_id).user_info or {}
    user_info["Никнейм"] = new_nickname
    save_user_state(user_id, input_data=new_nickname, user_info=user_info)
    save_user_state(user_id, user_info=user_info)

    bot.send_message(user_id, f"Ваш никнейм успешно изменен на {new_nickname}.")


# обработчик нажатия кнопки для изменения информации о себе
@bot.callback_query_handler(func=lambda call: call.data == "change_info")
def change_info(call):
    bot.send_message(call.message.chat.id, "Введите ваш пол:")
    bot.register_next_step_handler(call.message, process_gender_input)


# обработчик введенного пользователем пола
def process_gender_input(message):
    user_id = message.chat.id
    gender = message.text

    # обновление информации о пользователе
    user_info = load_user_state(user_id).user_info or {}
    user_info["Пол"] = gender
    save_user_state(user_id, input_data=gender, user_info=user_info)
    save_user_state(user_id, user_info=user_info)
    bot.send_message(user_id, f"Ваш пол успешно сохранен.")

    # запрашивание возраст
    bot.send_message(user_id, "Введите ваш возраст:")
    bot.register_next_step_handler(message, process_age_input)


# обработчик введенного пользователем возраста
def process_age_input(message):
    user_id = message.chat.id
    age = message.text

    # обновление информации о пользователе
    user_info = load_user_state(user_id).user_info or {}
    user_info["Возраст"] = age
    save_user_state(user_id, input_data=age, user_info=user_info)
    save_user_state(user_id, user_info=user_info)
    bot.send_message(user_id, f"Ваш возраст успешно сохранен.")

    bot.send_message(user_id, "Введите ваш город проживания:")
    bot.register_next_step_handler(message, process_city_input)


# обработчик введенного пользователем города
def process_city_input(message):
    user_id = message.chat.id
    city = message.text

    # обновление информацию о пользователе
    user_info = load_user_state(user_id).user_info or {}
    user_info["Город"] = city
    save_user_state(user_id, input_data=city, user_info=user_info)
    save_user_state(user_id, user_info=user_info)

    bot.send_message(user_id, f"Ваш город проживания успешно сохранен.")


# обработчик нажатия кнопки для удаления любимой категории новостей
@bot.callback_query_handler(func=lambda call: call.data == "remove_news_category")
def remove_news_category(call):
    user_id = call.message.chat.id

    # удаление выбранной любимой категории новостей
    save_user_state(user_id, selected_settings=" ")

    bot.send_message(user_id,
                     "Любимая категория новостей успешно удалена. Вы можете заново добавить любимую категорию в "
                     "/settings.")


# обработчик нажатия кнопки для выбора категории новостей в качестве любимой
@bot.callback_query_handler(func=lambda call: call.data == "select_favorite_category")
def select_favorite_category(call):
    user_id = call.message.chat.id

    # клавиатура с кнопками категорий новостей
    keyboard = types.InlineKeyboardMarkup()
    for category_name in categories.keys():
        keyboard.add(types.InlineKeyboardButton(text=category_name, callback_data=f"favorite_category_{category_name}"))

    bot.send_message(user_id, "Выберите любимую категорию новостей:", reply_markup=keyboard)


# обработчик нажатия кнопки для выбора категории новостей в качестве любимой
@bot.callback_query_handler(func=lambda call: call.data.startswith("favorite_category_"))
def handle_favorite_category_selection(call):
    user_id = call.message.chat.id
    selected_category = call.data.split("_")[-1]

    # сохранение выбранной категории в качестве любимой
    save_user_state(user_id, selected_settings=categories[selected_category])
    bot.send_message(user_id, f"Категория {selected_category} успешно выбрана в качестве любимой.\nДля просмотра "
                              f"новостей наберите /news ")
