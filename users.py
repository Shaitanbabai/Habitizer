# В этом блоке происходит импорт необходимых для работы кода библиотек и модулей:
# telebot: Библиотека для работы с Telegram Bot API.
# types: Модуль из telebot для работы с клавиатурами и другими элементами интерфейса.
# bot: Это модуль для работы с Telegram Bot API-позволяет создавать ботов, обрабатыватьи отправлять сообщения, работать с клавиатурами и 
# другими функциями Telegram Bot API. Модуль bot можно установить с помощью pip install pytelegrambot
# sqlite3: Библиотека для работы с базами данных SQLite. Подключение к базе данных habit_tracker.db, создание курсора для работы с ней.
# datetime: Модуль для работы с датами и временем.
# config: Модуль config.py, содержащий токен бота.
import telebot
from telebot import types
import bot
import sqlite3
import datetime
from config import bot
from datetime import datetime, timedelta
from timezone import get_timezone
from db import cursor, db


db = sqlite3.connect('habit_tracker.db')
cursor = db.cursor()


# В этом блоке происходит обработка упраляющих команд меню, обработка ошибок и исключений.
# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
# Получение ID пользователя
user_id = message.chat.id


# Проверка наличия пользователя в базе данных
cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
user_exists = cursor.fetchone() is not None


if not user_exists:
# Создание нового пользователя в базе данных
cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
db.commit()


# Получение часового пояса пользователя
try:
timezone = get_timezone(message.chat.location.timezone)
except KeyError:
timezone = None


# Сохранение часового пояса пользователя
cursor.execute('UPDATE users SET timezone = ? WHERE user_id = ?', (timezone, user_id))
db.commit()


# Получение информации о пользователе
cursor.execute('SELECT timezone FROM users WHERE user_id = ?', (user_id,))
user_timezone = cursor.fetchone()[0]


# Текущее время в часовом поясе пользователя
current_time = datetime.now(timezone=get_timezone(user_timezone))
current_time_str = format_time(current_time, user_timezone)


# Приветственное сообщение
welcome_message = f"Приветствую в трекере привычек! \n\nТекущее время: {current_time_str} ({user_timezone})\n\nЧто хотите сделать?"


# Создание клавиатуры
keyboard = create_keyboard_main_menu()


# Отправка приветствия и клавиатуры
send_message_with_keyboard(bot, message.chat.id, welcome_message, keyboard)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
# Создание клавиатуры
keyboard = create_keyboard_back_to_main_menu()

# Текст справки
help_text = """
**Доступные команды:**

* /start - Запустить бота и открыть главное меню
* /add_habit - Добавить новую привычку
* /my_habits - Посмотреть список своих привычек
* /period - Изменить период напоминаний для привычки
* /frequency - Изменить частоту напоминаний для привычки
* /report - Получить отчет о привычке
* /remove_habit - Удалить привычку
* /help - Получить справку

**Описание команд:**

* ... (описание каждой команды)

**Важно:**

* ... (информация о базе данных)

**Если у вас есть вопросы или предложения, 
не стесняйтесь обращаться ко мне!**
 """


# Отправка справки и клавиатуры
send_message_with_keyboard(bot, message.chat.id, help_text, keyboard)


# Обработчик команды /add_habit
@bot.message_handler(commands=['add_habit'])
def add_habit(message):
# Получение ID пользователя
user_id = message.chat.id


# Создание клавиатуры
keyboard = keyboard_add_habit_name


# Запрос названия привычки
send_message_with_keyboard(bot, message.chat.id, "Введите название новой привычки:", keyboard)


# Обработчик команды /my_habits
@bot.message_handler(commands=['my_habits'])
def show_habits(message):
# Получение ID пользователя
user_id = message.chat.id


# Получение списка привычек пользователя
cursor.execute('SELECT habit_id, name FROM habits WHERE user_id = ?', (user_id,))
habits = cursor.fetchall()

# Проверка наличия привычек
if habits:
# Создание клавиатуры
    keyboard = create_keyboard_from_habits(habits)

# Сообщение о наличии привычек
message_text = "Список ваших привычек:"
    else:
# Создание клавиатуры
    keyboard = keyboard_back_to_main_menu

# Сообщение о отсутствии привычек
    message_text = "У вас пока нет привычек. Добавьте новую с помощью команды /add_habit."

# Отправка сообщения и клавиатуры
    send_message_with_keyboard(bot, message.chat.id, message_text, keyboard)


# Обработчик команды /period
@bot.message_handler(commands=['period'])
def handle_period(message):
# Получение ID пользователя
    user_id = message.chat.id

# Получение ID привычки из сообщения
    habit_id = get_habit_id_from_message(message)

# Проверка наличия привычки
  if habit_id is None:
    send_error_message(bot, message.chat.id, "Выберите привычку, для которой хотите изменить период напоминаний.")
    return

# Создание клавиатуры
  keyboard = create_keyboard_for_period_selection(habit_id)

# Запрос периода напоминаний
  send_message_with_keyboard(bot, message.chat.id, "Выберите желаемый период напоминаний:", keyboard)


# Обработчик команды /frequency
@bot.message_handler(commands=['frequency'])
def handle_frequency(message):
  # Получение ID пользователя
    user_id = message.chat.id

# Получение ID привычки из сообщения
    habit_id = get_habit_id_from_message(message)

# Проверка наличия привычки
  if habit_id is None:
    send_error_message(bot, message.chat.id, "Выберите привычку, для которой хотите изменить частоту напоминаний.")
return

# Создание клавиатуры
  keyboard = create_keyboard_for_frequency_selection(habit_id)

# Запрос частоты напоминаний
  send_message_with_keyboard(bot, message.chat.id, "Выберите желаемую частоту напоминаний:", keyboard)


# Обработчик команды /report
@bot.message_handler(commands=['report'])
def handle_report(message):
# Получение ID пользователя
  user_id = message.chat.id

# Получение ID привычки из сообщения
  habit_id = get_habit_id_from_message(message)

# Проверка наличия привычки
if habit_id is None:
  send_error_message(bot, message.chat.id, "Выберите привычку, для которой хотите получить отчет.")
return

# Получение информации о привычке
  habit_info = get_habit_info(habit_id)

# Формирование отчета
report_text = generate_report_text(habit_info)

# Отправка отчета
send_message(bot, message.chat.id, report_text)


# Обработчик команды /remove_habit
def remove_habit(message):
  # Получение ID пользователя
  user_id = message.chat.id

  # Получение ID привычки из сообщения
  habit_id = get_habit_id_from_message(message)

  # Проверка наличия привычки
  if habit_id is None:
    send_error_message(bot, message.chat.id, "Выберите привычку, которую хотите удалить.")
    return

  # Подтверждение удаления
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
  keyboard.add("Да", "Нет")
  send_message_with_keyboard(bot, message.chat.id, f"Удалить привычку '{get_habit_name(habit_id)}'?", keyboard)
  bot.register_message_handler(remove_habit_confirmation_handler, func=lambda m: m.chat.id == message.chat.id and m.text in ["Да", "Нет"])


# Обработчик подтверждения удаления привычки
def remove_habit_confirmation_handler(message):
  # Получение ID пользователя
  user_id = message.chat.id

  # Получение ID привычки из сообщения
  habit_id = get_habit_id_from_message(message)

  # Проверка наличия привычки
  if habit_id is None:
    send_error_message(bot, message.chat.id, "Выберите привычку, которую хотите удалить.")
    return

  # Удаление привычки
  delete_habit(habit_id)

  # Сообщение о том, что привычка удалена
  send_message(bot, message.chat.id, f"Привычка '{get_habit_name(habit_id)}' успешно удалена.")


# Обработчик нажатия на кнопку "Добавить название"
@bot.callback_query_handler(func=lambda call: call.data == 'add_habit_name')
def add_habit_name(call):
  # Получение ID пользователя и ID чата
  user_id = call.from_user.id
  chat_id = call.message.chat.id

  # Запрос описания привычки
  keyboard = keyboard_add_habit_description
  send_message_with_keyboard(bot, chat_id, "Введите описание своей привычки:", keyboard)


# Обработчик нажатия на кнопку "Отмена"
@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def handle_cancel(call):
  # Получение ID пользователя и ID чата
  user_id = call.from_user.id
  chat_id = call.message.chat.id

  # Создание клавиатуры
  keyboard = keyboard_back_to_main_menu

  # Отправка сообщения и клавиатуры
  send_message_with_keyboard(bot, chat_id, "Действие отменено.", keyboard)


# Обработчик нажатия на кнопки выбора периода напоминаний
@bot.callback_query_handler(func=lambda call: call.data.startswith('period_'))
def handle_period_selection(call):
  # Получение ID пользователя, ID чата и ID привычки
  user_id = call.from_user.id
  chat_id = call.message.chat.id
  habit_id = int(call.data[7:])

  # Изменение периода напоминаний
  set_habit_period(habit_id, call.data[7:])

  # Сообщение о том, что период напоминаний изменен
  send_message(bot, chat_id, f"Период напоминаний для привычки '{get_habit_name(habit_id)}' изменен на {call.data[7:]}.")

# Обработчик нажатия на кнопки выбора частоты напоминаний
def handle_frequency_selection(call):
  # Получение ID пользователя, ID чата и ID привычки
  user_id = call.from_user.id
  chat_id = call.message.chat.id
  habit_id = int(call.data[10:])

  # Изменение частоты напоминаний
  set_habit_frequency(habit_id, call.data[10:])

# Сообщение о том, что частота напоминаний изменена
  send_message(bot, chat_id, f"Частота напоминаний для привычки '{get_habit_name(habit_id)}' изменена на {call.data[10:]}.")


# Функция для получения ID привычки из сообщения
def get_habit_id_from_message(message):
  try:
    habit_id = int(message.text.split()[1])
  except (IndexError, ValueError):
    return None

  return habit_id


# Функция для получения информации о привычке
def get_habit_info(habit_id):
  cursor.execute('SELECT * FROM habits WHERE habit_id = ?', (habit_id,))
  habit_info = cursor.fetchone()

  if habit_info is None:
    return None

  return {
    'habit_id': habit_info[0],
    'name': habit_info[1],
    'description': habit_info[2],
    'period': habit_info[3],
    'frequency': habit_info[4],
    'start_date': habit_info[5],
    'completions': habit_info[6],
  }


# Функция для формирования текста отчета
def generate_report_text(habit_info):
  report_text = f"**Отчет о привычке '{habit_info['name']}':**\n\n"

  # Описание
  if habit_info['description']:
    report_text += f"Описание: {habit_info['description']}\n\n"

  # Период и частота напоминаний
  report_text += f"Период напоминаний: {habit_info['period']}\n"
  report_text += f"Частота напоминаний: {habit_info['frequency']}\n\n"

  # Дата начала
  report_text += f"Дата начала: {format_date(habit_info['start_date'])}\n\n"

  # Количество выполнений
  report_text += f"Количество выполнений: {habit_info['completions']}\n\n"

  return report_text


# Функция для удаления привычки
def delete_habit(habit_id):
  cursor.execute('DELETE FROM habits WHERE habit_id = ?', (habit_id,))
  cursor.execute('DELETE FROM habit_completions WHERE habit_id = ?', (habit_id,))
  db.commit()


# Функция для изменения периода напоминаний привычки
def set_habit_period(habit_id, period):
  cursor.execute('UPDATE habits SET period = ? WHERE habit_id = ?', (period, habit_id))
  db.commit()


# Функция для изменения частоты напоминаний привычки
def set_habit_frequency(habit_id, frequency):
  cursor.execute('UPDATE habits SET frequency = ? WHERE habit_id = ?', (frequency, habit_id))
  db.commit()


# Функция для форматирования даты
def format_date(date_str):
  if date_str is None:
    return ""

  try:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d.%m.%Y")
  except ValueError:
    return date_str


# Функция для форматирования времени
def format_time(time_obj, timezone=None):
  if timezone is None:
    timezone = get_timezone()

  return time_obj.astimezone(timezone).strftime("%H:%M")


# Функция для отправки сообщения с клавиатурой
def send_message_with_keyboard(bot, chat_id, text, keyboard):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  markup.add(*keyboard)
  bot.send_message(chat_id, text, reply_markup=markup)


# Функция для отправки сообщения с кнопкой "Назад"
def send_message_with_back_button(bot, chat_id, text):
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
  keyboard.add("Назад")
  bot.send_message(chat_id, text, reply_markup=keyboard)


# Функция для отправки сообщения об ошибке
def send_error_message(bot, chat_id, text):
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
  keyboard.add("Назад")
  bot.send_message(chat_id, text, reply_markup=keyboard)


# Функция для создания клавиатуры главного меню
def create_keyboard_main_menu():
  keyboard = [
    ["Добавить привычку"],
    ["Мои привычки"],
    ["Помощь"],
  ]
  return keyboard


# Функция для создания клавиатуры с списком привычек
def create_keyboard_from_habits(habits):
  keyboard = []
  for habit_id, name in habits:
    keyboard_row = [types.KeyboardButton(f"{habit_id}. {name}")]
    keyboard.append(keyboard_row)
  keyboard.append(["Назад"])
  return keyboard


# Функция для создания клавиатуры для выбора периода
def create_keyboard_for_period_selection(habit_id):
  keyboard = []
  for period in ["Ежедневно", "Раз в неделю", "Раз в месяц"]:
    keyboard_row = [types.KeyboardButton(f"{period}_{habit_id}")]
    keyboard.append(keyboard_row)
  keyboard.append(["Назад"])
  return keyboard


# Функция для создания клавиатуры для выбора частоты
def create_keyboard_for_frequency_selection(habit_id):
  keyboard = []
  for frequency in ["Утром", "Днем", "Вечером"]:
    keyboard_row = [types.KeyboardButton(f"{frequency}_{habit_id}")]
    keyboard.append(keyboard_row)
  keyboard.append(["Назад"])
  return keyboard


# Функция для получения названия привычки из сообщения
def get_habit_name(habit_id):
  cursor.execute('SELECT name FROM habits WHERE habit_id = ?', (habit_id,))
  habit_name = cursor.fetchone()[0]
  return habit_name


# Запуск бота
bot.polling()
