import telebot
from telebot import types
import sqlite3
from datetime import datetime as dt

bot = telebot.TeleBot('здесь_должен_быть_наш_API_KEY')

class HabitTrackerDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = self.create_connection(db_file)
        self.create_tables()

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print(f"Соединение с базой данных {db_file} установлено.")
        except sqlite3.Error as e:
            print(f"Ошибка соединения с базой данных: {e}")
        return conn

    def create_tables(self):
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_tg_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            user_status TEXT NOT NULL DEFAULT '1',
            user_date_entry TEXT NOT NULL,
            reminder_time_from TEXT NOT NULL DEFAULT '07:00',
            reminder_time_till TEXT NOT NULL DEFAULT '22:00'
        );
        """
        create_habits_table = """
        CREATE TABLE IF NOT EXISTS habits (
            habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            habit_name TEXT NOT NULL,
            habit_description TEXT,
            habit_frequency TEXT,
            habit_status TEXT NOT NULL DEFAULT '0',
            habit_start_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        );
        """
        create_reminders_table = """
        CREATE TABLE IF NOT EXISTS reminders (
            reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            habit_id INTEGER NOT NULL,
            reminder_date TEXT NOT NULL,
            reminder_status INTEGER NOT NULL DEFAULT '2',
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (habit_id) REFERENCES habits (habit_id)
        );
        """
        create_statistics_table = """
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            habit_id INTEGER NOT NULL,
            reminder_id INTEGER NOT NULL,
            habit_status TEXT NOT NULL DEFAULT '0',
            total_number_reminders_habit INTEGER NOT NULL,
            missed_number_reminders_habit INTEGER NOT NULL,
            completed_number_reminders_habit INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (habit_id) REFERENCES habits (habit_id),
            FOREIGN KEY (reminder_id) REFERENCES reminders (reminder_id)
        );
        """
        self.execute_query(create_users_table)
        self.execute_query(create_habits_table)
        self.execute_query(create_reminders_table)
        self.execute_query(create_statistics_table)

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
            print(f"Ошибка выполнения запроса: {e}")
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

    def add_reminder(self, user_id, habit_id, reminder_date, reminder_status):
        query = """
        INSERT INTO reminders (user_id, habit_id, reminder_date, reminder_status)
        VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (user_id, habit_id, reminder_date, reminder_status))

    def mark_reminder_completed(self, reminder_id):
        query = "UPDATE reminders SET reminder_status = ? WHERE reminder_id = ?"
        self.execute_query(query, (1, reminder_id))

    def get_habits(self, user_id):
        query = "SELECT * FROM habits WHERE user_id = ?"
        return self.execute_query(query, (user_id,), fetch=True)

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных завершено.")

db = HabitTrackerDatabase("habit_tracker.db")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    db.add_user(user_id, username)
    bot.reply_to(message, "Привет! Я бот-трекер привычек. Давай начнем отслеживать твои привычки!")

@bot.message_handler(commands=['add_habit'])
def add_habit(message):
    msg = bot.reply_to(message, "Введи название новой привычки:")
    bot.register_next_step_handler(msg, process_habit_name_step)

def process_habit_name_step(message):
    habit_name = message.text
    if not habit_name:
        bot.reply_to(message, "Название привычки не может быть пустым. Пожалуйста, введи название:")
        return
    msg = bot.reply_to(message, "Введи описание привычки:")
    bot.register_next_step_handler(msg, process_habit_description_step, habit_name)

def process_habit_description_step(message, habit_name):
    habit_description = message.text
    if not habit_description:
        habit_description = "Описание отсутствует"
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Ежедневно', 'Раз в несколько дней')
    msg = bot.reply_to(message, "Укажите частоту выполнения привычки:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_habit_frequency_step, habit_name, habit_description)

def process_habit_frequency_step(message, habit_name, habit_description):
    habit_frequency = message.text
    if habit_frequency not in ['Ежедневно', 'Раз в несколько дней']:
        bot.reply_to(message, "Неверная частота. Пожалуйста, выбери из предложенных вариантов.")
        return
    user_id = message.from_user.id
    db.add_habit(user_id, habit_name, habit_description, habit_frequency)
    bot.send_message(message.chat.id, f"Привычка '{habit_name}' добавлена успешно!")

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
            report_message += f"Привычка: {row[0]}, Выполнено: {row[1]} раз(а)\n"
        bot.send_message(message.chat.id, report_message)
    else:
        bot.reply_to(message, "У тебя пока нет данных для отчета.")

bot.polling()