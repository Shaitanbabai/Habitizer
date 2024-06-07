# Этот код создает базу данных SQLite с 4 таблицами: `users`, `habits`, 'reminders` и 'statistics'.
# В нем также реализованы основные функции для добавления пользователей, привычек
# и отметок выполнения привычек, а также для получения данных из базы.

import sqlite3
from sqlite3 import Error
from datetime import datetime as dt, datetime


class HabitTrackerDatabase:
    def __init__(self, db_file):
        """Инициализация соединения с базой данных."""
        self.db_file = "habit_tracker.db"
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
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_tg_id INTEGER NOT NULL, /* id пользователя в Телеграм */
            user_name TEXT NOT NULL, /* имя пользователя (можно получить только по запросу у пользователя) */
            user_status INTEGER DEFAULT 1, /* 0 - не активный пользователь, 1 - активный пользователь */
            user_date_entry TEXT NOT NULL, /* дата регистрации пользователя */
            user_access_level INTEGER DEFAULT 0, /* уровень доступа пользователя */
            user_timezone TEXT  /* часовой пояс пользователя */
        );
        """

        # Создание таблицы привычек
        create_habits_table = """
        CREATE TABLE IF NOT EXISTS habits (
            habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, /* для связи с таблицей `users` */
            habit_name TEXT NOT NULL, /* название привычки (например: Занятие спортом)*/
            habit_description TEXT, /* описание привычки (например: Занятие спортом в фитнес-зале, минимум 1 час)*/
            habit_frequency INTEGER DEFAULT 1, /* частота выполнения привычки (например: 1 раз в день)*/
            habit_status INTEGER NULL DEFAULT 0, /* 0 - привычка в работе, 1 - завершено выполнение */
            habit_start_date TEXT NOT NULL, /* дата начала выполнения  привычки */
            habit_end_date TEXT, /* дата отказа от привычки - на перспективу*/
            reminder_time_from TEXT NOT NULL DEFAULT '07:00', /* время начала оповещения, удобное для пользователя*/
            reminder_time_till TEXT NOT NULL DEFAULT '22:00', /* время начала оповещения, удобное для пользователя*/
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
            reminder_status INTEGER NOT NULL DEFAULT 0, /* 0 - не выполнено, 1 - выполнено*/
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
            habit_status INTEGER NOT NULL DEFAULT 0, /* 0 - активная, 1 - завершенная */
            reminder_status INTEGER NOT NULL DEFAULT 0, /* 0 - НеВыполнено, 1 - Выполнено, 2 - Активное */
            reminder_status_name TEXT NOT NULL DEFAULT 'НеВыполнено', /* Записываем НеВыполнено / Выполнено / Активное */
            reminder_sending_date TEXT, /* записываем время направления юзеру уведомления */
            reminder_receive_response_date TEXT, /* записываем время получения от юзера отклика по уведомлению */
            total_number_reminders_habit INTEGER NOT NULL DEFAULT 0, /* общее количество напоминаний по привычке - НУЖНО??? */
            missed_number_reminders_habit INTEGER NOT NULL DEFAULT 0, /* количество пропущенных напоминаний по привычке - НУЖНО??? */
            completed_number_reminders_habit INTEGER NOT NULL DEFAULT 0, /* количество выполненных напоминаний по привычке - НУЖНО??? */
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (habit_id) REFERENCES habits (habit_id),
            FOREIGN KEY (reminder_id) REFERENCES reminders (reminder_id)
        );
        """

        self.execute_query(create_users_table)  # cоздание таблицы пользователей
        self.execute_query(create_habits_table)  # cоздание таблицы привычек
        self.execute_query(create_reminders_table)  # cоздание таблицы напоминаний
        self.execute_query(create_statistics_table)  # cоздание таблицы статистики

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

    def add_habit(self, user_id, habit_name, habit_description, habit_frequency, reminder_time_from,
                  reminder_time_till):
        """Добавление новой привычки с проверкой на дублирование."""
        # Проверка на дублирование привычки
        if self.is_habit_duplicate(user_id, habit_name):
            print("Привычка с таким именем уже существует.")  # Вывод предупреждения пользователю
            return False

        query = """
        INSERT INTO habits (user_id, habit_name, habit_description, habit_frequency, habit_start_date, reminder_time_from, reminder_time_till)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        habit_start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.execute_query(query, (
            user_id, habit_name, habit_description, habit_frequency, habit_start_date, reminder_time_from,
            reminder_time_till))

        habit_id = self.get_habit_id(user_id, habit_name)
        self.add_reminder_habit(user_id, habit_id, habit_frequency, reminder_time_from, reminder_time_till)
        return True

    def is_habit_duplicate(self, user_id, habit_name):
        """Проверка на дублирование привычки."""
        query = """
        SELECT COUNT(*) FROM habits WHERE user_id=? AND habit_name=?
        """
        result = self.execute_query(query, (user_id, habit_name), fetch=True)
        count = result[0][0]
        return count > 0

    def add_reminder_habit(self, user_id, habit_id, habit_frequency, reminder_time_from, reminder_time_till):
        """Добавление напоминаний для привычки с частотой N раз."""
        time_from = datetime.strptime(reminder_time_from, "%H:%M")
        time_till = datetime.strptime(reminder_time_till, "%H:%M")
        delta = time_till - time_from
        interval = delta / habit_frequency
        reminder_date = time_from
        for i in range(habit_frequency):
            reminder_time_str = reminder_date.strftime("%H:%M")
            query = """
            INSERT INTO reminders (user_id, habit_id, reminder_date)
            VALUES (?, ?, ?)
            """
            self.execute_query(query, (user_id, habit_id, reminder_time_str))
            reminder_date += interval

    def get_habit_id(self, user_id, habit_name):
        """Получение id привычки."""
        query = """
        SELECT habit_id FROM habits WHERE user_id=? AND habit_name=?
        """
        result = self.execute_query(query, (user_id, habit_name), fetch=True)
        habit_id = result[0][0]
        return habit_id

    # def changing_convenient_reminder_time(self, reminder_time_from, reminder_time_till, habit_id):
    #     """Изменение удобного времени оповещения."""
    #     query = """
    #     UPDATE habits SET habits.reminder_time_from=?, habits.reminder_time_till=? WHERE user_id=?
    #     """
    #     self.execute_query(query, (reminder_time_from, reminder_time_till, habit_id))

    # def add_reminder(self, user_id, habit_id, reminder_date, reminder_status):
    #     """Добавление напоминаний о привычке"""
    #     query = """
    #     INSERT INTO reminders (user_id, habit_id, reminder_date, reminder_status)
    #     VALUES (?, ?, ?, ?)
    #     """
    #     self.execute_query(query, (user_id, habit_id, reminder_date, reminder_status))

    # def mark_habit_rejection(self, habit_id):
    #     """Отметка временного отказа от привычки - на перспективу"""
    #     query = """
    #     UPDATE habits SET habit_status=? AND habit_end_date=? WHERE habit_id=?
    #     """
    #     self.execute_query(query, (1, dt.now().strftime("%Y-%m-%d %H:%M:%S"), habit_id))

    # def mark_reminder_completed(self, reminder_id):
    #     """Отметка о выполнении привычки."""
    #     query = """
    #     UPDATE reminders SET reminders.reminder_status=? WHERE reminder_id=?
    #     """
    #     self.execute_query(query, (1, reminder_id))

    # def mark_reminder_missed(self, reminder_id):
    #     """Отметка о пропуске выполнения привычки."""
    #     query = """
    #     UPDATE reminders SET reminders.reminder_status=? WHERE reminder_id=?
    #     """
    #     self.execute_query(query, (0, reminder_id))

    # def delete_habit(self, habit_id):
    #     """Удаление привычки и напоминаний."""
    #     query = """
    #      DELETE FROM habits WHERE habits.habit_id=?
    #      """
    #     self.execute_query(query, habit_id)
    #     query = """
    #      DELETE FROM reminders WHERE reminders.habit_id=?
    #      """
    #     self.execute_query(query, habit_id)

    # def get_habits(self, user_id):
    #     """Получение всех привычек пользователя."""
    #     query = """
    #     SELECT * FROM habits WHERE user_id = ?
    #     """
    #     cursor = self.connection.cursor()
    #     cursor.execute(query, (user_id,))
    #     return cursor.fetchall()

    def close_connection(self):
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто.")

    # def execute_missed(self, query, params='missed_number_reminders_habit', fetch=False):
    #     """Выполнение SQL-запроса."""
    #     try:
    #         cursor = self.connection.cursor()
    #         query = "SELECT COUNT(missed_number_reminders_habit) FROM statistics"
    #         if params:
    #             cursor.execute(query, params)
    #         else:
    #             cursor.execute(query)
    #             missed_habit = cursor.fetchone()[0]
    #         self.connection.commit()
    #         if fetch:
    #             return cursor.fetchall()
    #         return None
    #     except Error as e:
    #         print(f"Ошибка выполнения запроса: {e}")
    #         return None
    #

# # # Пример использования
# if __name__ == "__main__":
#     db = HabitTrackerDatabase("habit_tracker.db")
# #     db.add_user(1101, "username")
# #     db.add_habit(1, "Exercise", "Daily morning exercise", "30 minutes", "daily")
# #     db.mark_habit_done(1, 1, "2023-10-01")
# #     habits = db.get_habits(1)
# # #    progress = db.get_progress(1, 1)
# #     print("Habits:", habits)
# # #    print("Progress:", progress)
#     db.close_connection()
