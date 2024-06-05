import time
from datetime import datetime, timedelta
import sqlite3

# Класс привычки
class Habit:
    # Инициализатор класса Habit
    def __init__(self, habit_id, user_id, habit_name, habit_description, habit_frequency, habit_status,
                 habit_start_date, habit_end_date=None):
        self.habit_id = habit_id
        self.user_id = user_id
        self.habit_name = habit_name
        self.habit_description = habit_description
        self.habit_frequency = habit_frequency
        self.habit_status = habit_status
        self.habit_start_date = habit_start_date
        self.habit_end_date = habit_end_date

# Статический метод для создания новой привычки в базе данных
    @staticmethod
    def create_habit(conn, user_id, habit_name, habit_description, habit_frequency):
        if conn is None:
            raise ValueError("Connection object is None")  # Проверка наличия соединения с базой данных
        habit_start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Получение текущей даты и времени
        habit_status = "0"  # по умолчанию - привычка в работе
        habit_end_date = None  # по умолчанию - нет даты окончания
        sql = '''INSERT INTO habits (user_id, habit_name, habit_description, habit_frequency, habit_status, habit_start_date, habit_end_date)
                  VALUES (?, ?, ?, ?, ?, ?, ?)'''  # SQL-запрос для вставки новой записи в таблицу habits
        cur = conn.cursor()  # Создание курсора
        cur.execute(sql, (user_id, habit_name, habit_description, habit_frequency, habit_status, habit_start_date, habit_end_date))  # Выполнение SQL-запроса
        conn.commit()  # Сохранение изменений в базе данных
        return cur.lastrowid  # Возвращение ID созданной привычки

# Статический метод для редактирования существующей привычки в базе данных
    @staticmethod
    def edit_habit(conn, habit_id, habit_name=None, habit_description=None, habit_frequency=None,
                   habit_status=None, habit_end_date=None):
        sql = 'UPDATE habits SET'  # Начало SQL-запроса для обновления записи в таблице habits
        params = []  # Пустой список для параметров запроса
        if habit_name:
            sql += ' habit_name = ?,'
            params.append(habit_name)
        if habit_description:
            sql += ' habit_description = ?,'
            params.append(habit_description)
        if habit_frequency:
            sql += ' habit_frequency = ?,'
            params.append(habit_frequency)
        if habit_status:
            sql += ' habit_status = ?,'
            params.append(habit_status)
        if habit_end_date:
            sql += ' habit_end_date = ?,'
            params.append(habit_end_date)

        sql = sql.rstrip(',')  # Удаление лишней запятой из конца запроса
        sql += ' WHERE habit_id = ?'  # Добавление условия WHERE для обновления только определенной записи
        params.append(habit_id)  # Добавление ID привычки в список параметров

        cur = conn.cursor()  # Создание курсора
        cur.execute(sql, params)  # Выполнение SQL-запроса с параметрамиlit
        conn.commit()  # Сохранение изменений в базе данных

# Статический метод для удаления привычки из базы данных
    @staticmethod
    def delete_habit(conn, habit_id):
        sql = 'DELETE FROM habits WHERE habit_id = ?'  # SQL-запрос для удаления записи из таблицы habits
        cur = conn.cursor()
        cur.execute(sql, (habit_id,))
        conn.commit()

# Статический метод для получения привычки из базы данных
    @staticmethod
    def get_habit(conn, habit_id):
        sql = 'SELECT * FROM habits WHERE habit_id = ?'  # SQL-запрос для получения записи из таблицы habits
        cur = conn.cursor()
        cur.execute(sql, (habit_id,))
        row = cur.fetchone()  # Получение первой строки
        if row:  # Если строка существует
            return Habit(*row)  # Возвращение объекта Habit, созданного из строки результата запроса
        return None  # Если строка не существует, возвращение None

# Статический метод для получения списка привычек из базы данных
    @staticmethod
    def list_habits(conn):
        sql = 'SELECT * FROM habits'  # SQL-запрос для получения всех записей из таблицы habits
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        habits = [Habit(*row) for row in rows]  # Создание списка объектов Habit из строк результата запроса
        return habits  # Возвращение списка привычек

# Статический метод для отправки напоминания о привычке в базу данных
    @staticmethod
    def send_reminder(conn, habit_id):  # Отправка напоминания о привычке
        print(f'Напоминание отправленно для привычки: {habit_id}')
        next_reminder_time = datetime.now() + timedelta(minutes=1)  # Установка времени следующего напоминания через 1 минуту от текущего времени.
        return next_reminder_time  # Возвращение времени следующего напоминания

# Статический метод для проверки статуса напоминания о привычке в базе данных
    @staticmethod
    def check_reminder_status(conn, habit_id):  # Проверка статуса напоминания
        sql = 'SELECT habit_status FROM habits WHERE habit_id = ?'  # SQL-запрос для получения статуса напоминания
        cur = conn.cursor()
        cur.execute(sql, (habit_id,))  # Выполнение SQL-запроса с подстановкой идентификатора привычки.
        row = cur.fetchone()  # Получение первой строки
        if row: # Извлечение первой строки результата запроса.
            return row[0] == "1"  # Возврат значения True, если статус напоминания равен "1", иначе False.
        return False

# Метод для мониторинга привычек и отправки напоминаний в базу данных
    @staticmethod
    def monitor_habits():
        while True:   # Бесконечный цикл для постоянного мониторинга привычек.
            conn = sqlite3.connect('habits.db')  # Открытие соединения с базой данных
            habits = Habit.list_habits(conn)  # Получение списка привычек из базы данных
            for habit in habits:  # Перебор всех привычек в списке
                next_reminder_time = Habit.send_reminder(conn, habit.habit_id)  # Отправка напоминания о привычке
                conn.close()  # Закрываем соединение после отправки напоминания

                while datetime.now() < next_reminder_time:  # Ожидание до времени следующего напоминания.
                    time.sleep(10)  # Сон на 10 секунд

                conn = sqlite3.connect('habits.db')  # Повторное подключение к базе данных для проверки статуса напоминания.
                if Habit.check_reminder_status(conn, habit.habit_id):
                    print(f'Привычка {habit.habit_id} подтверждена.')
                else:
                    print(f'Привычка {habit.habit_id} не подтверждена.')
                    Habit.edit_habit(conn, habit.habit_id, habit_status="0")
                conn.close()  # Закрываем соединение после проверки статуса