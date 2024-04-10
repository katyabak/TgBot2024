import random
import telebot
from config import TOKEN
from database import load_user_state, save_user_state

# инициализация бота
bot = telebot.TeleBot(TOKEN)


# меню с кнопками
def send_menu(chat_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(telebot.types.KeyboardButton('/help'),
                 telebot.types.KeyboardButton('/settings'),
                 telebot.types.KeyboardButton('/weather'),
                 telebot.types.KeyboardButton('/news'),
                 telebot.types.KeyboardButton('/joke'))
    bot.send_message(chat_id, "Выберите одну из команд:", reply_markup=keyboard)


# обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # получаем текущую команду пользователя
    current_command = message.text.split()[0]
    # Сохраняем текущую команду пользователя в базу данных
    save_user_state(message.chat.id, current_command=current_command)
    # получаем никнейм пользователя из БД
    user_state = load_user_state(message.chat.id)
    if user_state and user_state.user_info and 'Никнейм' in user_state.user_info:
        nickname = user_state.user_info['Никнейм']
        greeting_message = f"Привет, {nickname}! Это бот-помощник Bot Helper.\n\n"
    else:
        greeting_message = "Привет! Это бот-помощник Bot Helper.\n\n"

    # отправить приветственное сообщение и меню
    bot.send_message(message.chat.id, greeting_message +
                     "Список доступных команд:\n"
                     "/help - информация о боте\n"
                     "/settings - настройки\n"
                     "/weather - выбор города, отображение погоды\n"
                     "/news - выбор категории, отображение новостей\n"
                     "/joke - отображение случайной шутки\n")
    send_menu(message.chat.id)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    # получаем текущую команду пользователя
    current_command = message.text.split()[0]
    # сохраняем текущую команду пользователя в базу данных
    save_user_state(message.chat.id, current_command=current_command)
    bot.send_message(message.chat.id,
                     "Этот бот является ботом-помощником, разработанный @katyaban1 на языке Python с использованием "
                     "библиотеки pyTelegramBotAPI и базы данных PostgreSQL для выполнения технического задания "
                     "StudentLabs 2024 .\n\n"
                     "С помощью этого бота вы можете получить доступ к различным функциям, таким как просмотр погоды, "
                     "чтение новостей, а так же получение случайной шутки.")


# обработчик команды /joke
@bot.message_handler(commands=['joke'])
def handle_joke(message):
    current_command = message.text.split()[0]

    # сохраняем текущую команду пользователя в БД
    save_user_state(message.chat.id, current_command=current_command)
    # ф-ция для чтения случайной шутки из файла
    with open('jokes.txt', 'r', encoding='utf-8') as f:
        jokes = f.readlines()
    # выбираем случайную шутку из списка
    random_joke = random.choice(jokes)
    bot.send_message(message.chat.id, random_joke)
