from database import save_user_state, load_user_state
from handlers import bot
from newsapi import NewsApiClient
from telebot import types

# словарь с возможными категориями новостей
categories = {
    'Спорт': 'sports',
    'Главное': 'general',
    'Технологии': 'technology'
}


# обработчик для получения выбранной категории новостей
@bot.message_handler(commands=['news'])
def handle_news(message):
    current_command = message.text.split()[0]
    user_id = message.chat.id
    save_user_state(user_id, current_command=current_command)

    # загрузка состояние пользователя
    user_state = load_user_state(user_id)

    if user_state and user_state.selected_settings:
        category = user_state.selected_settings
        if category in categories.values():
            newsapi = NewsApiClient(api_key='514446dd8dda4a8f99d5b5cc3bf0dc39')
            news = newsapi.get_top_headlines(category=category, language='ru')

            # если есть новости в выбранной категории
            if news['articles']:
                first_article = news['articles'][0]
                article_text = f"{first_article['title']}\n{first_article['description']}\n{first_article['url']}"
                bot.send_message(user_id, article_text)
                bot.send_message(user_id, "Для изменения любимой категории перейдите в /settings.")
                return

    # если нет выбранной любимой категории или в этой категории нет новостей, предлагаем пользователю выбрать категорию
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories.keys():
        keyboard.row(category)

    # отправляем сообщение с запросом выбора категории с помощью клавиатуры
    bot.send_message(user_id, "Выберите категорию новостей:", reply_markup=keyboard)


# обработчик для получения новости по выбранной категории
@bot.message_handler(func=lambda message: message.text in categories.keys())
def handle_selected_category(message):
    # инициализация клиента News API
    newsapi = NewsApiClient(api_key='514446dd8dda4a8f99d5b5cc3bf0dc39')
    category = categories[message.text]
    news = newsapi.get_top_headlines(category=category, language='ru')

    # если есть новости в выбранной категории
    if news['articles']:
        first_article = news['articles'][0]
        article_text = f"{first_article['title']}\n{first_article['description']}\n{first_article['url']}"
        bot.send_message(message.chat.id, article_text)
        bot.send_message(message.chat.id, "Для изменения любимой категории перейдите в /settings.")
    else:
        bot.send_message(message.chat.id, f"По категории '{message.text}' новостей не найдено.")
        bot.send_message(message.chat.id, "Для изменения любимой категории перейдите в /settings.")
