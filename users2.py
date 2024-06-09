# Это скрипт на Python, который использует библиотеку telebot для создания бота Telegram.
# Бот обрабатывает различные команды и запросы обратного вызова для выполнения различных действий.
# Скрипт импортирует необходимые модули, такие как telebot, types, sqlite3, datetime и timezone.
# Он подключается к базе данных SQLite с именем habit_tracker.db.
# В скрипте определено несколько функций для обработки различных команд и обратных запросов,
# таких как запуск бота, добавление привычки, показ привычек, изменение периода и частоты напоминаний,
#   создание отчета и удаление привычки.
# Также есть вспомогательные функции для обработки новых пользователей,
#   обработки часовых поясов пользователей, обработки приветственных сообщений и создания клавиатуры.

# Описание функций
#
# 1. **Функции для обработки команд:**
#    - `show_habits`: Показывает текущие привычки пользователя.
#    - `handle_period`: Позволяет пользователю изменить период напоминания для выбранной привычки.
#    - `handle_frequency`: Позволяет пользователю изменить частоту напоминаний для выбранной привычки.
#    - `handle_report`: Генерирует и отправляет отчет по выбранной привычке.
#    - `remove_habit`: Запрашивает подтверждение на удаление привычки и обрабатывает его.
#    - `handle_habit_deletion_confirmation`: Обрабатывает подтверждение или отказ от удаления привычки.
#    - `handle_cancel`: Обрабатывает запрос на отмену.
#    - `handle_add_habit`: Обрабатывает добавление новой привычки.
#    - `handle_remove_habit`: Обрабатывает запрос на удаление привычки.
#    - `handle_remove_habit_confirmation`: Обрабатывает подтверждение или отказ от удаления привычки.
#    - `handle_habit_deletion_confirmation`: Обрабатывает подтверждение или отказ от удаления привычки.
#    - `handle_add_habit_name`: Обрабатывает имя новой привычки.
#    - `handle_back_to_main_menu`: Обрабатывает нажатие кнопки "Вернуться в главное меню".
#    - `handle_timezone_selection`: Обрабатывает выбор временного пояса.
#    - `handle_timezone_confirmation`: Обрабатывает подтверждение временного пояса.
#    - `handle_help`: Обрабатывает запрос помощи.
#     - `handle_back_to_main_menu`: Обрабатывает нажатие кнопки "Вернуться в главное меню".
#
# 2. **Вспомогательные функции:**
#    - `confirm_deletion`: Отправляет запрос на подтверждение удаления привычки.
#    - `handle_habit_deletion_confirmation`: Обрабатывает подтверждение или отказ от удаления привычки.
#    - `update_habit_period`, `update_habit_frequency`: Обновляют период и частоту напоминаний для привычки в базе данных.
#    - `get_formatted_date`: Форматирует дату в удобочитаемый формат.
#    - `format_time`: Форматирует время с учетом временной зоны.
#    - `get_user_habits`: Возвращает список привычек пользователя из базы данных.
#    - `delete_habit`: Удаляет привычку из базы данных.
#    - `get_habit_id_from_message`: Возвращает идентификатор привычки из сообщения пользователя.
#    - `create_keyboard_and_message_text`: Создает клавиатуру и текст сообщения для привычки.
#    - `create_habits_keyboard`: Создает клавиатуру с привычками пользователя.
#    - `send_message_with_keyboard`: Отправляет сообщение с клавиатурой.
#    - `send_error_message`: Отправляет сообщение об ошибке.
#
# Эти функции взаимодействуют друг с другом, обеспечивая полный цикл управления привычками в рамках телеграм-бота
#   и предоставляя пользователю удобный интерфейс для взаимодействия с ботом.
#
import telebot
from telebot import types
import types
import sqlite3
from datetime import datetime, timedelta
from timezone import get_timezone
from config import Config


# Подключение к базе данных
db = sqlite3.connect('habit_tracker.db')
cursor = db.cursor()

# Обработчики команд
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    handle_new_user(user_id)
    handle_user_timezone(user_id, message)
    handle_welcome_message(user_id)

@bot.message_handler(commands=['help'])
def handle_help(message):
    handle_help_message(message)

@bot.message_handler(commands=['add_habit'])
def add_habit(message):
    handle_add_habit(message)

@bot.message_handler(commands=['my_habits'])
def show_habits(message):
    handle_show_habits(message)

@bot.message_handler(commands=['period'])
def handle_period(message):
    handle_period_selection(message)

@bot.message_handler(commands=['frequency'])
def handle_frequency(message):
    handle_frequency_selection(message)

@bot.message_handler(commands=['report'])
def handle_report(message):
    handle_report(message)

@bot.message_handler(commands=['remove_habit'])
def remove_habit(message):
    handle_remove_habit(message)

# Обработчики обратного вызова
@bot.callback_query_handler(func=lambda call: call.data == 'add_habit_name')
def add_habit_name(call):
    handle_add_habit_name(call)

@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def handle_cancel(call):
    handle_cancel(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('period_'))
def handle_period_selection(call):
    handle_period_selection(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('frequency_'))
def handle_frequency_selection(call):
    handle_frequency_selection(call)

# Helper functions
def handle_new_user(user_id):
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    user_exists = cursor.fetchone() is not None
    if not user_exists:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        db.commit()

def handle_user_timezone(user_id, message):
    try:
        timezone = get_timezone(message.chat.location.timezone)
    except KeyError:
        timezone = None
    cursor.execute('UPDATE users SET timezone = ? WHERE user_id = ?', (timezone, user_id))
    db.commit()

def handle_welcome_message(user_id):
    cursor.execute('SELECT timezone FROM users WHERE user_id = ?', (user_id,))
    user_timezone = cursor.fetchone()[0]
    current_time = datetime.now(timezone=get_timezone(user_timezone))
    current_time_str = format_time(current_time, user_timezone)
    welcome_message = f"Welcome to the habit tracker! \n\nCurrent time: {current_time_str} ({user_timezone})\n\nWhat would you like to do?"
    keyboard = create_keyboard_main_menu()
    send_message_with_keyboard(bot, message.chat.id, welcome_message, keyboard)


# Function to handle /help command
@bot.message_handler(commands=['help'])
def handle_help(message):
    keyboard = create_keyboard_back_to_main_menu()
    help_text = """
    **Available Commands:**

    * /start - Start the bot and open the main menu
    * /add_habit - Add a new habit
    * /my_habits - View your habits
    * /period - Change the reminder period for a habit
    * /frequency - Change the reminder frequency for a habit
    * /report - Get a report on a habit
    * /remove_habit - Remove a habit
    * /help - Get help
    """
    send_message_with_keyboard(bot, message.chat.id, help_text, keyboard)

# Функция для обработки команды /add_habit
@bot.message_handler(commands=['add_habit'])
def add_habit(message):
    user_id = message.chat.id
    keyboard = create_keyboard_add_habit_name()
    send_message_with_keyboard(bot, user_id, "Введите название новой привычки:", keyboard)

# Функция для обработки команды /my_habits
@bot.message_handler(commands=['my_habits'])
def show_habits(message):
    user_id = message.chat.id
    habits = get_user_habits(user_id)
    keyboard, message_text = create_keyboard_and_message_text(habits)
    send_message_with_keyboard(bot, user_id, message_text, keyboard)

# Функция обработки команды /period
@bot.message_handler(commands=['period'])
def handle_period(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if habit_id is None:
        send_error_message(bot, user_id, "Выберите привычку, для которой вы хотите изменить период напоминания..")
        return
    keyboard = create_keyboard_for_period_selection(habit_id)
    send_message_with_keyboard(bot, user_id, "Выберите нужный период напоминания:", keyboard)

# Функция обработки команды /frequency
@bot.message_handler(commands=['frequency'])
def handle_frequency(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if habit_id is None:
        send_error_message(bot, user_id, "Выберите привычку, для которой вы хотите изменить частоту напоминаний..")
        return
    keyboard = create_keyboard_for_frequency_selection(habit_id)
    send_message_with_keyboard(bot, user_id, "Выберите нужную частоту напоминаний:", keyboard)

# Функция для обработки команды /report
@bot.message_handler(commands=['report'])
def handle_report(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if habit_id is None:
        send_error_message(bot, user_id, "Выберите привычку, по которой вы хотите получить отчет.")
        return
    habit_info = get_habit_info(habit_id)
    report_text = generate_report_text(habit_info)
    send_message(bot, user_id, report_text)

# Функция для обработки команды /remove_habit
@bot.message_handler(commands=['remove_habit'])
def remove_habit(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if habit_id is None:
        send_error_message(bot, user_id, "Выберите привычку, которую вы хотите удалить.")
        return
    confirm_deletion(bot, message, habit_id)

# Функция подтверждения удаления привычек
def confirm_deletion(bot, message, habit_id):
    user_id = message.chat.id
    keyboard = create_keyboard_back_to_main_menu()
    message_text = "Вы уверены, что хотите удалить эту привычку?"
    send_message_with_keyboard(bot, user_id, message_text, keyboard, habit_id)

# Fфункция подтверждения удаления привычек
@bot.message_handler(func=lambda message: message.text in ["Yes", "No"])
def handle_habit_deletion_confirmation(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if message.text == "Yes":
        delete_habit(habit_id)
        send_message(bot, user_id, "Привычка успешно удалена.")
    elif message.text == "No":
        send_message(bot, user_id, "Привычка не была удалена.")
    else:
        send_error_message(bot, user_id, "Некорректный ответ.")

# import types

def update_habit_period(habit_id, period):
    cursor.execute('UPDATE habits SET period = ? WHERE habit_id = ?', (period, habit_id))
    db.commit()

def update_habit_frequency(habit_id, frequency):
    cursor.execute('UPDATE habits SET frequency = ? WHERE habit_id = ?', (frequency, habit_id))
    db.commit()

def get_formatted_date(date_str):
    if date_str is None:
        return ""

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        return date_str

def format_time(time_obj, timezone=None):
    if timezone is None:
        timezone = get_timezone()

    return time_obj.astimezone(timezone).strftime("%H:%M")

def send_message_with_keyboard(bot, chat_id, text, keyboard):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*keyboard)
    bot.send_message(chat_id, text, reply_markup=markup)

def send_message_with_back_button(bot, chat_id, text):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    bot.send_message(chat_id, text, reply_markup=keyboard)

def send_error_message(bot, chat_id, text):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    bot.send_message(chat_id, text, reply_markup=keyboard)

def create_main_menu_keyboard():
    keyboard = [
        ["Добавить привычку"],
        ["Мои привычки"],
        ["Помощь"],
    ]
    return keyboard

def create_habits_keyboard(habits):
    keyboard = []
    for habit_id, name in habits:
        keyboard_row = [types.KeyboardButton(f"{habit_id}. {name}")]
        keyboard.append(keyboard_row)
    keyboard.append(["Назад"])
    return keyboard

def create_period_selection_keyboard(habit_id):
    keyboard = []
    for period in ["Ежедневно", "Раз в неделю", "Раз в месяц"]:
        keyboard_row = [types.KeyboardButton(f"{period}_{habit_id}")]
        keyboard.append(keyboard_row)
    keyboard.append(["Назад"])
    return keyboard

def create_frequency_selection_keyboard(habit_id):
    keyboard = []
    for frequency in ["Утром", "Днем", "Вечером"]:
        keyboard_row = [types.KeyboardButton(f"{frequency}_{habit_id}")]
        keyboard.append(keyboard_row)
    keyboard.append(["Назад"])
    return keyboard

def get_habit_name_from_message(habit_id):
    cursor.execute('SELECT name FROM habits WHERE habit_id = ?', (habit_id,))
    habit_name = cursor.fetchone()[0]
    return habit_name

bot.polling()
