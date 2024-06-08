parse.py

Функция `parse_message`, которая обрабатывает текстовое сообщение, отправленное пользователем через бота Telegram, 
  и возвращает кортеж с заданной структурой, мы можем выполнить следующие шаги:

1. Определите функцию `parse_message`, которая принимает в качестве аргументов идентификатор пользователя и текст сообщения.
2. Разделите сообщение на основе разделителей `,` и `;`.
3. Обрезать части и прекратить обработку, если встречается `.`.
4. Построить кортеж, начинающийся с идентификатора пользователя и первой части сообщения (имя привычки), 
  за которой следуют остальные части максимум до 10 элементов.

```python
import telebot
from config import Config
import sqlite3
from sqlite3 import Error
from datetime import datetime as dt, datetime
from database import *
from habits import *
from users import *


bot = telebot.TeleBot(Config.TELEGRAM_API_TOKEN)

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Соединение с базой данных {db_file} установлено.")
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return conn

def parse_message(user_id, message):
    # Split the message by ',' and ';'
    parts = []
    for part in message.split(','):
        parts.extend(part.split(';'))
    
    # Удалите из каждой части ведущие и завершающие пробельные символы
    parts = [part.strip() for part in parts]
    
    # If есть '.', усеките список на этом месте
    if '.' in parts:
        parts = parts[:parts.index('.')]
    
    # Ограничьте количество частей до 9 (чтобы общее количество элементов в кортеже было 10, включая user_id)
    parts = parts[:9]
    
    # Сформируйте кортеж, начинающийся с user_id и первой части в виде имени привычки
    result = (user_id, parts[0]) + tuple(parts[1:])
    
    return result

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать в бот Habit Tracker! Отправьте мне сообщение в формате 'habit, time1, time2, ...'")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text
    parsed_data = parse_message(user_id, text)
    bot.reply_to(message, f"Разобранные данные: {parsed_data}")

if __name__ == "__main__":
    bot.polling(none_stop=True)

```
 Объяснение:
 1. **Функция `parse_message`**:
   - **Входные данные**: `user_id` (идентификатор Telegram пользователя) и `message` (текстовое сообщение от пользователя).
   - **Разбиение**: Сообщение делится на `,` и `;` для получения отдельных частей.
   - **Обрезка**: Из каждой части удаляются пробелы.
   - **Усечение**: Если встречается `.`, список усекается на этом месте.
   - **Ограничение**: Список ограничивается 9 частями, чтобы кортеж не превышал 10 элементов.
   - **result**: Создается кортеж, начинающийся с `user_id`, за которым следует первая часть (имя привычки), а затем остальные части.

 2. **Обработчики бота**:
   - **`send_welcome`**: Отвечает на команды `/start` и `/help` приветственным сообщением.

   - **`handle_message`:
 **: Обрабатывает любое сообщение, отправленное пользователем:
     - Извлекает `user_id` и текст сообщения.
     - Вызывает `parse_message` для обработки сообщения.
     - Отправляет разобранные данные обратно пользователю в качестве ответа.

 3. **`bot.polling(none_stop=True)`**: Запускает бота и продолжает его работу для прослушивания сообщений.

 Эта реализация гарантирует, что ваш бот сможет разобрать сообщения в соответствии с заданным форматом 
  и вернуть нужную структуру кортежей.


config.py
Пояснение:
 1. **TELEGRAM_API_TOKEN**: Токен для доступа к Telegram API, который вы должны получить у @BotFather в Telegram.
   Этот токен можно установить через переменные окружения
    или заменить `your-telegram-api-token-here` на ваш реальный токен.
 2. **DB_NAME**: Имя файла базы данных SQLite.
 3. **DB_PATH**: Путь к файлу базы данных. По умолчанию используется текущая директория.
 4. **get_db_uri()**: Метод, который возвращает полный путь к базе данных.

 Использование переменных окружения:
 Для более безопасного хранения конфиденциальной информации, такой как токен API,
 рекомендуется использовать переменные окружения.
 Вы можете установить переменные окружения с помощью командной строки
 или использовать файл `.env`, если используете пакет `python-dotenv`.

 Пример использования переменных окружения с `python-dotenv`:
 1. Установите пакет `python-dotenv`:
    
```python
 pip install python-dotenv
```
 2. Создайте файл `.env` в корневой директории вашего проекта:
```python
   TELEGRAM_API_TOKEN=your-telegram-api-token-here
   DB_NAME=habit_tracker.db
   DB_PATH=./
```
3. Обновите `config.py` для загрузки переменных окружения из файла `.env`:

```python
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
```
