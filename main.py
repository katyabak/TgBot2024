from handlers import bot
from settingsHandle import handle_settings, select_favorite_category
from weatherHandle import handle_weather

if __name__ == '__main__':
    bot.polling(none_stop=True)
