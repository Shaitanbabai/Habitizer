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
import telebot
import types
import sqlite3
from datetime import datetime
import ptz

# Инициализация бота и базы данных
bot = telebot.TeleBot('YOUR_BOT_API_KEY')
db = sqlite3.connect('habits.db', check_same_thread=False)
cursor = db.cursor()

# Функция для получения привычек пользователя
def get_user_habits(user_id):
    cursor.execute('SELECT habit_id, name FROM habits WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

# Функция для создания клавиатуры с привычками
def create_habits_keyboard(habits):
    keyboard = []
    for habit_id, name in habits:
        keyboard_row = [types.KeyboardButton(f"{habit_id}. {name}")]
        keyboard.append(keyboard_row)
    keyboard.append([types.KeyboardButton("Назад")])
    return keyboard

# Функция для создания клавиатуры выбора периода
def create_period_selection_keyboard(habit_id):
    keyboard = []
    for period in ["Ежедневно", "Раз в неделю", "Раз в месяц"]:
        keyboard_row = [types.KeyboardButton(f"{period}_{habit_id}")]
        keyboard.append(keyboard_row)
    keyboard.append([types.KeyboardButton("Назад")])
    return keyboard

# Функция для создания клавиатуры выбора частоты
def create_frequency_selection_keyboard(habit_id):
    keyboard = []
    for frequency in ["Утром", "Днем", "Вечером"]:
        keyboard_row = [types.KeyboardButton(f"{frequency}_{habit_id}")]
        keyboard.append(keyboard_row)
    keyboard.append([types.KeyboardButton("Назад")])
    return keyboard

# Функция для получения имени привычки из сообщения
def get_habit_name_from_message(habit_id):
    cursor.execute('SELECT name FROM habits WHERE habit_id = ?', (habit_id,))
    habit_name = cursor.fetchone()[0]
    return habit_name

# Функция для обработки команды /my_habits
@bot.message_handler(commands=['my_habits'])
def show_habits(message):
    user_id = message.chat.id
    habits = get_user_habits(user_id)
    keyboard = create_habits_keyboard(habits)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in keyboard:
        markup.add(*row)
    bot.send_message(user_id, "Ваши привычки:", reply_markup=markup)

# Функция обработки команды /period
@bot.message_handler(commands=['period'])
def handle_period(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if habit_id is None:
        bot.send_message(user_id, "Выберите привычку, для которой вы хотите изменить период напоминания.")
        return
    keyboard = create_period_selection_keyboard(habit_id)
    markup =types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in keyboard:
        markup.add(*row)
    bot.send_message(user_id, "Выберите нужный период напоминания:", reply_markup=markup)

# Функция обработки команды /frequency
@bot.message_handler(commands=['frequency'])
def handle_frequency(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if habit_id is None:
        bot.send_message(user_id, "Выберите привычку, для которой вы хотите изменить частоту напоминаний.")
        return
    keyboard = create_frequency_selection_keyboard(habit_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in keyboard:
        markup.add(*row)
    bot.send_message(user_id, "Выберите нужную частоту напоминаний:", reply_markup=markup)

# Функция для обработки команды /report
@bot.message_handler(commands=['report'])
def handle_report(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if habit_id is None:
        bot.send_message(user_id, "Выберите привычку, по которой вы хотите получить отчет.")
        return
    habit_info = get_habit_info(habit_id)
    report_text = generate_report_text(habit_info)
    bot.send_message(user_id, report_text)

# Функция для обработки команды /remove_habit
@bot.message_handler(commands=['remove_habit'])
def remove_habit(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if habit_id is None:
        bot.send_message(user_id, "Выберите привычку, которую вы хотите удалить.")
        return
    confirm_deletion(bot, message, habit_id)

# Функция подтверждения удаления привычек
def confirm_deletion(bot, message, habit_id):
    user_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Yes"), types.KeyboardButton("No"))
    bot.send_message(user_id, "Вы уверены, что хотите удалить эту привычку?", reply_markup=keyboard)

# Функция подтверждения удаления привычек
@bot.message_handler(func=lambda message: message.text in ["Yes", "No"])
def handle_habit_deletion_confirmation(message):
    user_id = message.chat.id
    habit_id = get_habit_id_from_message(message)
    if message.text == "Yes":
        delete_habit(habit_id)
        bot.send_message(user_id, "Привычка успешно удалена.")
    elif message.text == "No":
        bot.send_message(user_id, "Привычка не была удалена.")
    else:
        bot.send_message(user_id, "Некорректный ответ.")
        types.ReplyKeyboardMarkup(resize_keyboard=True)
        for row in keyboard:
            markup.add(*row)
        bot.send_message(user_id, "Выберите нужный период напоминания:", reply_markup=markup)

    # Функция обработки команды /frequency
    @bot.message_handler(commands=['frequency'])
    def handle_frequency(message):
        user_id = message.chat.id
        habit_id = get_habit_id_from_message(message)
        if habit_id is None:
            bot.send_message(user_id, "Выберите привычку, для которой вы хотите изменить частоту напоминаний.")
            return
        keyboard = create_frequency_selection_keyboard(habit_id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for row in keyboard:
            markup.add(*row)
        bot.send_message(user_id, "Выберите нужную частоту напоминаний:", reply_markup=markup)

    # Функция для обработки команды /report
    @bot.message_handler(commands=['report'])
    def handle_report(message):
        user_id = message.chat.id
        habit_id = get_habit_id_from_message(message)
        if habit_id is None:
            bot.send_message(user_id, "Выберите привычку, по которой вы хотите получить отчет.")
            return
        habit_info = get_habit_info(habit_id)
        report_text = generate_report_text(habit_info)
        bot.send_message(user_id, report_text)

    # Функция для обработки команды /remove_habit
    @bot.message_handler(commands=['remove_habit'])
    def remove_habit(message):
        user_id = message.chat.id
        habit_id = get_habit_id_from_message(message)
        if habit_id is None:
            bot.send_message(user_id, "Выберите привычку, которую вы хотите удалить.")
            return
        confirm_deletion(bot, message, habit_id)

    # Функция подтверждения удаления привычек
    def confirm_deletion(bot, message, habit_id):
        user_id = message.chat.id
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("Yes"), types.KeyboardButton("No"))
        bot.send_message(user_id, "Вы уверены, что хотите удалить эту привычку?", reply_markup=keyboard)

    # Функция подтверждения удаления привычек
    @bot.message_handler(func=lambda message: message.text in ["Yes", "No"])
    def handle_habit_deletion_confirmation(message):
        user_id = message.chat.id
        habit_id = get_habit_id_from_message(message)
        if message.text == "Yes":
            delete_habit(habit_id)
            bot.send_message(user_id, "Привычка успешно удалена.")
        elif message.text == "No":
            bot.send_message(user_id, "Привычка не была удалена.")
        else:
            bot.send_message(user_id, "Некорректный ответ.")

    # Вспомогательные функции для обновления форматирования
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
            timezone = pytz.timezone("Europe/Moscow")  # Укажите нужный вам часовой пояс
        return time_obj.astimezone(timezone).strftime("%H:%M")

    # Запуск бота
    bot.polling()
