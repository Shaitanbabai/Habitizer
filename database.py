# Этот код создает базу данных SQLite с тремя таблицами: `users`, `habits` и `progress`.
# В нем также реализованы основные функции для добавления пользователей, привычек
# и отметок выполнения привычек, а также для получения данных из базы.

import sqlite3
from sqlite3 import Error
from datetime import datetime as dt


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
            user_id INTEGER NOT NULL, /* id пользователя в Телеграм */
            user_name TEXT NOT NULL, /* имя пользователя (можно получить только по запросу у пользователя) */
            user_status TEXT NOT NULL DEFAULT '1', /* 0 - не активный пользователь, 1 - активный пользователь */
            user_date_entry TEXT NOT NULL /* дата регистрации пользователя */
        );
        """
        # Создание таблицы привычек
        create_habits_table = """
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* для связи с таблицей `users` */
            habit_name TEXT NOT NULL, /* название привычки (например: Занятие спортом)*/
            habit_description TEXT, /* описание привычки (например: Занятие спортом в фитнес-зале, минимум 1 час)*/
            habit_target INTEGER NOT NULL, /* Время на которое заводится привычка (например: 30 дней) */
            habit_frequency TEXT, /* частота выполнения привычки (например: раз в день)*/
            habit_status TEXT NOT NULL DEFAULT '0', /* 0 - привычка в работе, 1 - завершено выполнение */
            habit_start_date TEXT NOT NULL, /* дата начала выполнения  привычки */
            habit_end_date TEXT, /* дата окончания выполнения привычки */
            FOREIGN KEY (user_id) REFERENCES users (id) /* Связь с таблицей `users` */
        );
        """

        # # Создание служебной таблицы привычек
        # create_habits_log = """
        # CREATE TABLE IF NOT EXISTS habits_log (
        #     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     habit_id INTEGER NOT NULL, /* Для связи с таблицей `habits` */
        #     habit_log_date TEXT NOT NULL,
        #     FOREIGN KEY (habit_id) REFERENCES habits (id)
        # );
        # """

        # # Создание таблицы расписания выполнения привычек
        # create_progress_table = """
        # CREATE TABLE IF NOT EXISTS progress (
        #     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     user_id INTEGER NOT NULL, /* Для связи с таблицей `users` */
        #     habit_id INTEGER NOT NULL, /* Для связи с таблицей `habits` */
        #     habit_start_date TEXT NOT NULL,
        #     habit_end_date TEXT,
        #     /*habit_status TEXT NOT NULL DEFAULT 'active', - лишнее?*/
        #     FOREIGN KEY (user_id) REFERENCES users (id),
        #     FOREIGN KEY (habit_id) REFERENCES habits (id)
        # );
        # """

        # Создание таблицы напоминаний и выполнения привычки
        create_reminders_table = """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* для связи с таблицей `users` */
            habit_id INTEGER NOT NULL, /* для связи с таблицей `habits` */
            reminder_date TEXT NOT NULL, /* Дата установленных напоминаний */
            reminder_status INTEGER NOT NULL DEFAULT '2', /* 0 - выполнение пропущено, 1 - выполнено, 2 - выполнение запланировано */
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        );
        """

        # Создание таблицы данных для статистики
        create_statistics_table = """
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* для связи с таблицей `users` */
            habit_id INTEGER NOT NULL, /* для связи с таблицей `habits` */
            reminder_id INTEGER NOT NULL, /* Для связи с таблицей `reminders` */
            habit_status TEXT NOT NULL DEFAULT '0', /* 0 - активная, 1 - завершенная */
            total_number_reminders_habit INTEGER NOT NULL, /* общее количество напоминаний по привычке*/
            missed_number_reminders_habit INTEGER NOT NULL, /* количество пропущенных напоминаний по привычке*/
            completed_number_reminders_habit INTEGER NOT NULL, /* количество выполненных напоминаний по привычке*/
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (habit_id) REFERENCES habits (id),
            FOREIGN KEY (reminder_id) REFERENCES reminders (id)
        );
        """

        self.execute_query(create_users_table)  # cоздание таблицы пользователей
        self.execute_query(create_habits_table)  # cоздание таблицы привычек
        # self.execute_query(create_progress_table)
        # self.execute_query(create_habits_log)
        self.execute_query(create_reminders_table)  # cоздание таблицы напоминаний
        self.execute_query(create_statistics_table)  # cоздание таблицы статистики

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

    def add_user(self, user_id, user_name):
        """Добавление нового пользователя."""
        query = """
        INSERT INTO users (user_id, user_name, user_date_entry)
        VALUES (?, ?, ?)
        """
        self.execute_query(query, (user_id, user_name, dt.now().strftime("%Y-%m-%d %H:%M:%S")))

    def add_habit(self, user_id, habit_name, habit_description, habit_target, frequency):
        """Добавление новой привычки."""
        query = """
        INSERT INTO habits (user_id, habit_name, habit_description, habit_target, habit_frequency)
        VALUES (?, ?, ?, ?, ?)
        """
        self.execute_query(query, (user_id, habit_name, habit_description, habit_target, frequency))

    def mark_habit_done(self, user_id, habit_id, date, status='done'):
        """Отметка выполнения привычки."""
        query = """
        INSERT INTO habits (user_id, habit_id, date, status)
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

    # def get_progress(self, user_id, habit_id):
    #     """Получение прогресса выполнения привычки."""
    #     query = """
    #     SELECT * FROM progress WHERE user_id = ? AND habit_id = ?
    #     """
    #     cursor = self.connection.cursor()
    #     cursor.execute(query, (user_id, habit_id))
    #     return cursor.fetchall()

    def close_connection(self):
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто.")


# Пример использования
if __name__ == "__main__":
    db = HabitTrackerDatabase("habit_tracker.db")
    db.add_user(1, "username")
    db.add_habit(1, "Exercise", "Daily morning exercise", "30 minutes", "daily")
    db.mark_habit_done(1, 1, "2023-10-01")
    habits = db.get_habits(1)
    progress = db.get_progress(1, 1)
    print("Habits:", habits)
    print("Progress:", progress)
    db.close_connection()
