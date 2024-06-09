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
        self.habit_start_date = datetime.strptime(habit_start_date, "%Y-%m-%d %H:%M:%S")
        self.habit_end_date = datetime.strptime(habit_end_date, "%Y-%m-%d %H:%M:%S") if habit_end_date else None

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
    def send_reminder(conn, habit_id):
        print(f'Напоминание отправлено для привычки {habit_id}')
        # Здесь можно добавить логику отправки уведомлений пользователю
        sql = 'UPDATE habits SET last_reminder_time = ? WHERE habit_id = ?'
        cur = conn.cursor()
        cur.execute(sql, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), habit_id))
        conn.commit()

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
    
# Метод рассчитывает время следующего напоминания на основе частоты привычки (habit_frequency) и даты начала (habit_start_date).
    def calculate_next_reminder_time(habit):
        current_time = datetime.now()
        next_reminder_time = habit.habit_start_date
        while next_reminder_time <= current_time:
            next_reminder_time += timedelta(minutes=habit.habit_frequency)
        return next_reminder_time

# Метод для мониторинга привычек и изменения статуса напоминания
    @staticmethod
    def monitor_habits():
        while True:  #Метод `monitor_habits` выполняет мониторинг привычек в бесконечном цикле.
            conn = sqlite3.connect('habits.db')
            habits = Habit.list_habits(conn)
            conn.close()

            for habit in habits:
                next_reminder_time = Habit.calculate_next_reminder_time(habit)  # Вычисление следующего времени напоминания для привычки.
                print(f'Следующее напоминание для привычки {habit.habit_id} в {next_reminder_time}')

                while datetime.now() < next_reminder_time - timedelta(minutes=1):  # Ждем 1 минуту до следующего напоминания.
                    time.sleep(10)

                conn = sqlite3.connect('habits.db')
                if Habit.check_reminder_status(conn, habit.habit_id):  # Проверка статуса напоминания.
                    Habit.send_reminder(conn, habit.habit_id)
                else:
                    print(f'Привычка {habit.habit_id} отключена')
                    Habit.edit_habit(conn, habit.habit_id, habit_status="0")  # Изменение статуса привычки в базе данных.
                conn.close()