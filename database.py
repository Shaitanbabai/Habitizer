
# Этот код создает базу данных SQLite с 4 таблицами: `users`, `habits`, 'reminders` и 'statistics'.
# В нем также реализованы основные функции для добавления пользователей, привычек
# и отметок выполнения привычек, а также для получения данных из базы.

import sqlite3
from sqlite3 import Error
from datetime import datetime as dt


class HabitTrackerDatabase:
    def __init__(self, db_file):
        """Инициализация соединения с базой данных."""
        self.db_file = "habit_tracker.db"
        self.connection = self.create_connection(db_file)
        self.create_tables()
        self.close_connection()

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
        db.create_connection(self)
        # Создание таблицы пользователей
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_tg_id INTEGER NOT NULL, /* id пользователя в Телеграм */
            user_name TEXT NOT NULL, /* имя пользователя (можно получить только по запросу у пользователя) */
            user_status TEXT NOT NULL DEFAULT '1', /* 0 - не активный пользователь, 1 - активный пользователь */
            user_date_entry TEXT NOT NULL, /* дата регистрации пользователя */
            reminder_time_from TEXT NOT NULL DEFAULT '07:00', /* время начала оповещения, удобное для пользователя*/
            reminder_time_till TEXT NOT NULL DEFAULT '22:00' /* время начала оповещения, удобное для пользователя*/
        );
        """
        # Создание таблицы привычек
        create_habits_table = """
        CREATE TABLE IF NOT EXISTS habits (
            habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* для связи с таблицей `users` */
            habit_name TEXT NOT NULL, /* название привычки (например: Занятие спортом)*/
            habit_description TEXT, /* описание привычки (например: Занятие спортом в фитнес-зале, минимум 1 час)*/
            habit_frequency TEXT, /* частота выполнения привычки (например: раз в день)*/
            habit_status TEXT NOT NULL DEFAULT '0', /* 0 - привычка в работе, 1 - завершено выполнение */
            habit_start_date TEXT NOT NULL, /* дата начала выполнения  привычки */
            /*habit_end_date TEXT, /* дата отказа от привычки - на перспективу*/
            FOREIGN KEY (user_id) REFERENCES users (user_id) /* Связь с таблицей `users` */
        );
        """

        # Создание таблицы напоминаний и выполнения привычки
        create_reminders_table = """
        CREATE TABLE IF NOT EXISTS reminders (
            reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* для связи с таблицей `users` */
            habit_id INTEGER NOT NULL, /* для связи с таблицей `habits` */
            reminder_date TEXT NOT NULL, /* время установленного напоминания */
            reminder_status INTEGER NOT NULL DEFAULT '2', /* 0 - выполнение пропущено, 1 - выполнено, 2 - выполнение запланировано */
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (habit_id) REFERENCES habits (habit_id)
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
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (habit_id) REFERENCES habits (habit_id),
            FOREIGN KEY (reminder_id) REFERENCES reminders (reminder_id)
        );
        """

        self.execute_query(create_users_table)  # cоздание таблицы пользователей
        self.execute_query(create_habits_table)  # cоздание таблицы привычек
        self.execute_query(create_reminders_table)  # cоздание таблицы напоминаний
        self.execute_query(create_statistics_table)  # cоздание таблицы статистики
        db.close_connection()

    def execute_query(self, query, params=None, fetch=False):
        """Выполнение SQL-запроса."""
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
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None

    def add_user(self, user_tg_id, user_name):
        """Добавление нового пользователя."""
        # Проверка, существует ли пользователь с данным user_tg_id в таблице users
        query_check = """
        SELECT COUNT(*) FROM users WHERE user_tg_id = ?
        """
        result = self.execute_query(query_check, (user_tg_id,), fetch=True)

        if result:
            user_exists = result[0][0]
        else:
            user_exists = 0

        # Если пользователя нет, добавляем его в таблицу users
        if user_exists == 0:
            query_insert = """
            INSERT INTO users (user_tg_id, user_name, user_date_entry)
            VALUES (?, ?, ?)
            """
            self.execute_query(query_insert, (user_tg_id, user_name, dt.now().strftime("%Y-%m-%d %H:%M:%S")))

    def changing_convenient_reminder_time(self, reminder_time_from, reminder_time_till, user_id):
        """Изменение удобного времени оповещения."""
        query = """
        UPDATE users SET users.reminder_time_from=?, users.reminder_time_till=? WHERE user_id=?
        """
        self.execute_query(query, (reminder_time_from, reminder_time_till, user_id))

    def add_habit(self, user_id, habit_name, habit_description, habit_frequency):
        """Добавление новой привычки."""
        query = """
        INSERT INTO habits (user_id, habit_name, habit_description, habit_frequency, habit_start_date)
        VALUES (?, ?, ?, ?, ?)
        """
        self.execute_query(query, (user_id, habit_name, habit_description, habit_frequency, dt.now().strftime("%Y-%m-%d %H:%M:%S")))

    def add_reminder(self, user_id, habit_id, reminder_date, reminder_status):
        """Добавление напоминаний о привычке"""
        query = """
        INSERT INTO reminders (user_id, habit_id, reminder_date, reminder_status)
        VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (user_id, habit_id, reminder_date, reminder_status))

    # def mark_habit_rejection(self, habit_id):
    #     """Отметка временного отказа от привычки - на перспективу"""
    #     query = """
    #     UPDATE habits SET habit_status=? AND habit_end_date=? WHERE habit_id=?
    #     """
    #     self.execute_query(query, (1, dt.now().strftime("%Y-%m-%d %H:%M:%S"), habit_id))

    def mark_reminder_completed(self, reminder_id):
        """Отметка о выполнении привычки."""
        query = """
        UPDATE reminders SET reminders.reminder_status=? WHERE reminder_id=?
        """
        self.execute_query(query, (1, reminder_id))

    def mark_reminder_missed(self, reminder_id):
        """Отметка о пропуске выполнения привычки."""
        query = """
        UPDATE reminders SET reminders.reminder_status=? WHERE reminder_id=?
        """
        self.execute_query(query, (0, reminder_id))

    def delete_habit(self, habit_id):
        """Удаление привычки и напоминаний."""
        query = """
         DELETE FROM habits WHERE habits.habit_id=?
         """
        self.execute_query(query, habit_id)
        query = """
         DELETE FROM reminders WHERE reminders.habit_id=?
         """
        self.execute_query(query, habit_id)

    def get_habits(self, user_id):
        """Получение всех привычек пользователя."""
        query = """
        SELECT * FROM habits WHERE user_id = ?
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (user_id,))
        return cursor.fetchall()

#     # def get_progress(self, user_id, habit_id):
#     #     """Получение прогресса выполнения привычки."""
#     #     query = """
#     #     SELECT * FROM progress WHERE user_id = ? AND habit_id = ?
#     #     """
#     #     cursor = self.connection.cursor()
#     #     cursor.execute(query, (user_id, habit_id))
#     #     return cursor.fetchall()

    def close_connection(self):
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто.")


# # Пример использования
# if __name__ == "__main__":
db = HabitTrackerDatabase("habit_tracker.db")
#     db.add_user(1101, "username")
#     db.add_habit(1, "Exercise", "Daily morning exercise", "30 minutes", "daily")
#     db.mark_habit_done(1, 1, "2023-10-01")
#     habits = db.get_habits(1)
# #    progress = db.get_progress(1, 1)
#     print("Habits:", habits)
# #    print("Progress:", progress)
#     db.close_connection()
