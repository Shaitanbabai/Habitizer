import telebot
from telebot import types
import sqlite3
from datetime import datetime as dt
from config import Config  # Импорт конфигурации из config.py
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(Config.TELEGRAM_API_TOKEN)

# Класс для работы с базой данных - записи только в лог (настройки логирования выше)
class HabitTrackerDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = self.create_connection(db_file)

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            logger.info(f"Соединение с базой данных {db_file} установлено.")
        except sqlite3.Error as e:
            logger.error(f"Ошибка соединения с базой данных: {e}")
        return conn

    def execute_query(self, query, params=None, fetch=False):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            if fetch:
                return cursor.fetchall()
            return None
        except sqlite3.Error as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            return None

    def add_user(self, user_tg_id, user_name):
        query_check = "SELECT COUNT(*) FROM users WHERE user_tg_id = ?"
        result = self.execute_query(query_check, (user_tg_id,), fetch=True)

        if result and result[0][0] == 0:
            query_insert = """
            INSERT INTO users (user_tg_id, user_name, user_date_entry)
            VALUES (?, ?, ?)
            """
            self.execute_query(query_insert, (user_tg_id, user_name, dt.now().strftime("%Y-%m-%d %H:%M:%S")))

    def add_habit(self, user_id, habit_name, habit_description, habit_frequency):
        query = """
        INSERT INTO habits (user_id, habit_name, habit_description, habit_frequency, habit_start_date)
        VALUES (?, ?, ?, ?, ?)
        """
        self.execute_query(query, (user_id, habit_name, habit_description, habit_frequency, dt.now().strftime("%Y-%m-%d %H:%M:%S")))

    def update_habit(self, habit_id, habit_name=None, habit_description=None, habit_frequency=None):
        updates = []
        params = []
        if habit_name:
            updates.append("habit_name = ?")
            params.append(habit_name)
        if habit_description:
            updates.append("habit_description = ?")
            params.append(habit_description)
        if habit_frequency:
            updates.append("habit_frequency = ?")
            params.append(habit_frequency)
        params.append(habit_id)
        query = f"UPDATE habits SET {', '.join(updates)} WHERE habit_id = ?"
        self.execute_query(query, params)

    def get_habits(self, user_id):
        query = "SELECT * FROM habits WHERE user_id = ?"
        return self.execute_query(query, (user_id,), fetch=True)

    def delete_habit(self, habit_id):
        query = "DELETE FROM habits WHERE habit_id = ?"
        self.execute_query(query, (habit_id,))
        query = "DELETE FROM reminders WHERE habit_id = ?"
        self.execute_query(query, (habit_id,))

    def count_habits(self, user_id):
        query = "SELECT COUNT(*) FROM habits WHERE user_id = ?"
        result = self.execute_query(query, (user_id,), fetch=True)
        return result[0][0] if result else 0

    def close_connection(self):
        if self.connection:
            self.connection.close()
            logger.info("Соединение с базой данных закрыто.")

db = HabitTrackerDatabase(Config.get_db_uri())

def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("Создать привычку"), types.KeyboardButton("Изменить привычку"))
    markup.row(types.KeyboardButton("Статистика"), types.KeyboardButton("Удалить привычку"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    db.add_user(user_id, username)
    bot.reply_to(message, "Привет! Я бот-трекер привычек. Давай начнем отслеживать твои привычки!", reply_markup=create_main_menu())

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "/start - регистрация\n"
        "/help - список команд\n"
        "/add_habit - добавление привычки\n"
        "/describe_habit - описание привычки\n"
        "/period - период напоминаний\n"
        "/frequency - частота напоминаний\n"
        "/edit_habit - редактирование привычки\n"
        "/report - отчет\n"
        "/remove_habit - удаление привычки"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['add_habit'])
def add_habit(message):
    if db.count_habits(message.from_user.id) >= 5:
        bot.reply_to(message, "Ты не можешь добавить более 5 привычек.")
        return
    msg = bot.reply_to(message, "Введи название новой привычки (до 50 знаков):")
    bot.register_next_step_handler(msg, process_habit_name_step)

def process_habit_name_step(message):
    habit_name = message.text
    if not habit_name:
        bot.reply_to(message, "Название привычки не может быть пустым. Пожалуйста, введи название:")
        return
    if len(habit_name) > 50:
        bot.reply_to(message, "Название привычки не должно превышать 50 знаков. Пожалуйста, введи название:")
        return
    msg = bot.reply_to(message, "Введи описание привычки (до 120 знаков):")
    bot.register_next_step_handler(msg, process_habit_description_step, habit_name)

def process_habit_description_step(message, habit_name):
    habit_description = message.text
    if not habit_description:
        habit_description = "Описание отсутствует"
    if len(habit_description) > 120:
        bot.reply_to(message, "Описание привычки не должно превышать 120 знаков. Пожалуйста, введи описание:")
        return
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Ежедневно', 'Раз в несколько дней')
    msg = bot.reply_to(message, "Укажи частоту выполнения привычки:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_habit_frequency_step, habit_name, habit_description)

def process_habit_frequency_step(message, habit_name, habit_description):
    habit_frequency = message.text
    if habit_frequency not in ['Ежедневно', 'Раз в несколько дней']:
        bot.reply_to(message, "Неверная частота. Пожалуйста, выбери из предложенных вариантов.")
        return
    user_id = message.from_user.id
    db.add_habit(user_id, habit_name, habit_description, habit_frequency)
    bot.send_message(message.chat.id, f"Привычка '{habit_name}' добавлена успешно!")

@bot.message_handler(commands=['edit_habit'])
def edit_habit(message):
    user_id = message.from_user.id
    habits = db.get_habits(user_id)
    if habits:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for habit in habits:
            markup.add(habit[2])
        msg = bot.reply_to(message, "Выбери привычку для редактирования:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_edit_habit_step)
    else:
        bot.reply_to(message, "У тебя пока нет добавленных привычек. Добавь привычку с помощью команды /add_habit")

def process_edit_habit_step(message):
    habit_name = message.text
    user_id = message.from_user.id
    habits = db.get_habits(user_id)
    habit_id = next((habit[0] for habit in habits if habit[2] == habit_name), None)
    if habit_id is None:
        bot.reply_to(message, "Неверное название привычки. Пожалуйста, попробуй снова.")
        return
    msg = bot.reply_to(message, "Введи новое название привычки (оставь пустым, чтобы не менять):")
    bot.register_next_step_handler(msg, process_new_habit_name_step, habit_id)

def process_new_habit_name_step(message, habit_id):
    new_habit_name = message.text
    if new_habit_name and len(new_habit_name) > 50:
        bot.reply_to(message, "Название привычки не должно превышать 50 знаков. Пожалуйста, введи название:")
        return
    msg = bot.reply_to(message, "Введи новое описание привычки (оставь пустым, чтобы не менять):")
    bot.register_next_step_handler(msg, process_new_habit_description_step, habit_id, new_habit_name)

def process_new_habit_description_step(message, habit_id, new_habit_name):
    new_habit_description = message.text
    if new_habit_description and len(new_habit_description) > 120:
        bot.reply_to(message, "Описание привычки не должно превышать 120 знаков. Пожалуйста, введи описание:")
        return
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Ежедневно', 'Раз в несколько дней')
    msg = bot.reply_to(message, "Укажи новую частоту выполнения привычки (оставь пустым, чтобы не менять):", reply_markup=markup)
    bot.register_next_step_handler(msg, process_new_habit_frequency_step, habit_id, new_habit_name, new_habit_description)

def process_new_habit_frequency_step(message, habit_id, new_habit_name, new_habit_description):
    new_habit_frequency = message.text
    if new_habit_frequency and new_habit_frequency not in ['Ежедневно', 'Раз в несколько дней']:
        bot.reply_to(message, "Неверная частота. Пожалуйста, выбери из предложенных вариантов.")
        return
    db.update_habit(habit_id, new_habit_name, new_habit_description, new_habit_frequency)
    bot.send_message(message.chat.id, "Привычка успешно обновлена!")

@bot.message_handler(commands=['track_habit'])
def track_habit(message):
    user_id = message.from_user.id
    habits = db.get_habits(user_id)
    if habits:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for habit in habits:
            markup.add(habit[2])
        msg = bot.reply_to(message, "Выбери привычку для отметки выполнения:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_track_habit_step)
    else:
        bot.reply_to(message, "У тебя пока нет добавленных привычек. Добавь привычку с помощью команды /add_habit")

def process_track_habit_step(message):
    habit_name = message.text
    user_id = message.from_user.id
    habits = db.get_habits(user_id)
    habit_id = next((habit[0] for habit in habits if habit[2] == habit_name), None)
    if habit_id is None:
        bot.reply_to(message, "Неверное название привычки. Пожалуйста, попробуй снова.")
        return
    db.add_reminder(user_id, habit_id, dt.now().strftime("%Y-%m-%d"), 2)
    reminder_id = db.execute_query("SELECT last_insert_rowid()", fetch=True)[0][0]
    db.mark_reminder_completed(reminder_id)
    bot.send_message(message.chat.id, f"Выполнение привычки '{habit_name}' отмечено!")

@bot.message_handler(commands=['report'])
def send_report(message):
    user_id = message.from_user.id
    query = """
    SELECT h.habit_name, COUNT(r.reminder_id) as completed_count
    FROM habits h
    LEFT JOIN reminders r ON h.habit_id = r.habit_id AND r.reminder_status = 1
    WHERE h.user_id = ?
    GROUP BY h.habit_id
    """
    report = db.execute_query(query, (user_id,), fetch=True)
    if report:
        report_message = "Твои привычки и статистика их выполнения:\n\n"
        for row in report:
            report_message += f"Привычка: {row[0]}, Выполнена: {row[1]} раз(а)\n"
        bot.send_message(message.chat.id, report_message)
    else:
        bot.reply_to(message, "У тебя пока нет данных для отчета.")

@bot.message_handler(commands=['remove_habit'])
def remove_habit(message):
    user_id = message.from_user.id
    habits = db.get_habits(user_id)
    if habits:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for habit in habits:
            markup.add(habit[2])
        msg = bot.reply_to(message, "Выбери привычку для удаления:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_remove_habit_step)
    else:
        bot.reply_to(message, "У тебя пока нет добавленных привычек. Добавь привычку с помощью команды /add_habit")

def process_remove_habit_step(message):
    habit_name = message.text
    user_id = message.from_user.id
    habits = db.get_habits(user_id)
    habit_id = next((habit[0] for habit in habits if habit[2] == habit_name), None)
    if habit_id is None:
        bot.reply_to(message, "Неверное название привычки. Пожалуйста, попробуй снова.")
        return
    db.delete_habit(habit_id)
    bot.send_message(message.chat.id, f"Привычка '{habit_name}' удалена успешно!")

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    if message.text == "Создать привычку":
        add_habit(message)
    elif message.text == "Изменить привычку":
        edit_habit(message)
    elif message.text == "Статистика":
        send_report(message)
    elif message.text == "Удалить привычку":
        remove_habit(message)
    else:
        bot.reply_to(message, "Неизвестная команда. Пожалуйста, используй меню для навигации.")

bot.polling()