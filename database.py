# Этот код создает базу данных SQLite с тремя таблицами: `users`, `habits` и `progress`.
# В нем также реализованы основные функции для добавления пользователей, привычек
# и отметок выполнения привычек, а также для получения данных из базы.

import sqlite3
from sqlite3 import Error


class HabitTrackerDatabase:
    def __init__(self, db_file):
        """Инициализация соединения с базой данных."""
        self.connection = self.create_connection(db_file)
        self.create_tables()

    def create_connection(self, db_file):
        """Создание подключения к SQLite базе данных."""
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print(f"Соединение с базой данных {db_file} установлено.")
        except Error as e:
            print(f"Ошибка соединения с базой данных: {e}")
        return conn

    def create_tables(self):
        """Создание таблиц в базе данных."""
        # Создание таблицы пользователей
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            user_status TEXT NOT NULL DEFAULT '1', /*0 - inactive, 1 - active*/
            user_date_entry TEXT NOT NULL
        );
        """
        # Создание таблицы привычек
        create_habits_table = """
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* Для связи с таблицей `users` */
            habit_name TEXT NOT NULL,
            habit_description TEXT,
            habit_target_name TEXT,
            habit_frequency TEXT,
            habit_status TEXT NOT NULL DEFAULT '0', /*0 - active, 1 - completed*/
            /*habit_start_date TEXT NOT NULL,
            habit_end_date TEXT, - лишнее?*/
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """

        # Создание служебной таблицы привычек
        create_habits_log = """
        CREATE TABLE IF NOT EXISTS habits_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL, /* Для связи с таблицей `habits` */
            habit_log_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        );
        """

        # Создание таблицы расписания выполнения привычек
        create_progress_table = """
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* Для связи с таблицей `users` */
            habit_id INTEGER NOT NULL, /* Для связи с таблицей `habits` */
            habit_start_date TEXT NOT NULL,
            habit_end_date TEXT,
            /*habit_status TEXT NOT NULL DEFAULT 'active', - лишнее?*/            
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        );
        """

        # Создание таблицы напоминаний о привычках
        create_reminders_table = """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* Для связи с таблицей `users` */
            habit_id INTEGER NOT NULL, /* Для связи с таблицей `habits` */
            reminder_date TEXT NOT NULL,
            reminder_status TEXT NOT NULL DEFAULT '0', /* 0 - active, 1 - completed */
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        );
        """

        # Создание таблицы данных для статистики
        create_statistics_table = """
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* Для связи с таблицей `users` */
            /*user_status TEXT NOT NULL DEFAULT '1', - лишнее?*/
            habit_id INTEGER NOT NULL, /* Для связи с таблицей `habits` */
            reminder_id INTEGER NOT NULL, /* Для связи с таблицей `reminders` */
            habit_status TEXT NOT NULL DEFAULT '0', /* 0 - active, 1 - completed */
            reminder_status TEXT NOT NULL DEFAULT '0', /* 0 - active, 1 - completed */
            habit_start_date TEXT NOT NULL,
            reminder_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (habit_id) REFERENCES habits (id),
            FOREIGN KEY (reminder_id) REFERENCES reminders (id)
        );
        """

        self.execute_query(create_users_table)
        self.execute_query(create_habits_table)
        self.execute_query(create_progress_table)
        self.execute_query(create_habits_log)
        self.execute_query(create_reminders_table)
        self.execute_query(create_statistics_table)

    def execute_query(self, query, params=None):
        """Выполнение SQL-запроса."""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")

    def add_user(self, user_id, username):
        """Добавление нового пользователя."""
        query = """
        INSERT INTO users (user_id, username)
        VALUES (?, ?)
        """
        self.execute_query(query, (user_id, username))

    def add_habit(self, user_id, habit_name, description, goal, frequency):
        """Добавление новой привычки."""
        query = """
        INSERT INTO habits (user_id, habit_name, description, goal, frequency)
        VALUES (?, ?, ?, ?, ?)
        """
        self.execute_query(query, (user_id, habit_name, description, goal, frequency))

    def mark_habit_done(self, user_id, habit_id, date, status='done'):
        """Отметка выполнения привычки."""
        query = """
        INSERT INTO progress (user_id, habit_id, date, status)
        VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (user_id, habit_id, date, status))

    def get_habits(self, user_id):
        """Получение всех привычек пользователя."""
        query = """
        SELECT * FROM habits WHERE user_id = ?
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (user_id,))
        return cursor.fetchall()

    def get_progress(self, user_id, habit_id):
        """Получение прогресса выполнения привычки."""
        query = """
        SELECT * FROM progress WHERE user_id = ? AND habit_id = ?
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (user_id, habit_id))
        return cursor.fetchall()

    def close_connection(self):
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто.")


# # Пример использования
# if __name__ == "__main__":
#     db = HabitTrackerDatabase("habit_tracker.db")
#     db.add_user(1, "username")
#     db.add_habit(1, "Exercise", "Daily morning exercise", "30 minutes", "daily")
#     db.mark_habit_done(1, 1, "2023-10-01")
#     habits = db.get_habits(1)
#     progress = db.get_progress(1, 1)
#     print("Habits:", habits)
#     print("Progress:", progress)
#     db.close_connection()
