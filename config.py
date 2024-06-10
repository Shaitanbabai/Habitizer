# config.py
# Пояснение:
# 1. **TELEGRAM_API_TOKEN**: Токен для доступа к Telegram API, который вы должны получить у @BotFather в Telegram.
#  Этот токен можно установить через переменные окружения
#  или заменить `your-telegram-api-token-here` на ваш реальный токен.
# 2. **DB_NAME**: Имя файла базы данных SQLite.
# 3. **DB_PATH**: Путь к файлу базы данных. По умолчанию используется текущая директория.
# 4. **get_db_uri()**: Метод, который возвращает полный путь к базе данных.
#
# Использование переменных окружения:
# Для более безопасного хранения конфиденциальной информации, такой как токен API,
# рекомендуется использовать переменные окружения.
# Вы можете установить переменные окружения с помощью командной строки
# или использовать файл `.env`, если используете пакет `python-dotenv`.
#
# Пример использования переменных окружения с `python-dotenv`:
# 1. Установите пакет `python-dotenv`:
#
# pip install python-dotenv
#
# 2. Создайте файл `.env` в корневой директории вашего проекта:
#
#   TELEGRAM_API_TOKEN=your-telegram-api-token-here
#   DB_NAME=habit_tracker.db
#   DB_PATH=./
#
# 3. Обновите `config.py` для загрузки переменных окружения из файла `.env`:
#
from dotenv import load_dotenv
import os

#  Загрузка переменных окружения из .env файла
load_dotenv()


class Config:
    # Токен Telegram API
    TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', 'your-telegram-api-token-here')
    DB_NAME = os.getenv('DB_NAME', 'habit_tracker.db')
    DB_PATH = os.getenv('DB_PATH', './')


    @staticmethod
    def get_db_uri():
        return os.path.join(Config.DB_PATH, Config.DB_NAME)


# Пример использования:
if __name__ == "__main__":
    print("Telegram API Token:", Config.TELEGRAM_API_TOKEN)
    print("Database URI:", Config.get_db_uri())