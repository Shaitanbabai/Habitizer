import sqlite3
from datetime import datetime

# Класс привычки
class Habit:
    # Инициализатор класса Habit
    def __init__(self, habit_id, name_habit, habit_description, name_targets, habit_frequency, status, date_entry,
                 category, user_id):
        self.habit_id = habit_id
        self.name_habit = name_habit
        self.habit_description = habit_description
        self.name_targets = name_targets
        self.habit_frequency = habit_frequency
        self.status = status
        self.date_entry = date_entry
        self.category = category
        self.user_id = user_id

    # Статический метод для создания новой привычки в базе данных
    @staticmethod
    def create_habit(conn, name_habit, habit_description, name_targets, habit_frequency, category, user_id):
        if conn is None:
            raise ValueError("Connection object is None") # Проверка наличия соединения с базой данных
        date_entry = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Получение текущей даты и времени
        status = "active" # Установка статуса привычки как "active"
        sql = '''INSERT INTO habits (name_habit, habit_description, name_targets, habit_frequency, status, date_entry, category, user_id)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''' # SQL-запрос для вставки новой записи в таблицу habits
        cur = conn.cursor() # Создание курсора для выполнения SQL-запросов
        cur.execute(sql, (name_habit, habit_description, name_targets, habit_frequency, status, date_entry, category, user_id)) # Выполнение SQL-запроса
        conn.commit() # Сохранение изменений
        return cur.lastrowid # Возвращение ID созданной записи

    # Статический метод для редактирования существующей привычки в базе данных
    @staticmethod
    def edit_habit(conn, habit_id, name_habit=None, habit_description=None, name_targets=None, habit_frequency=None,
                   status=None, category=None, user_id=None):
        sql = 'UPDATE habits SET' # Начало SQL-запроса для обновления записи в таблице habits
        params = [] # Список параметров для запроса
        if name_habit:
            sql += ' name_habit = ?,'
            params.append(name_habit)
        if habit_description:
            sql += ' habit_description = ?,'
            params.append(habit_description)
        if name_targets:
            sql += ' name_targets = ?,'
            params.append(name_targets)
        if habit_frequency:
            sql += ' habit_frequency = ?,'
            params.append(habit_frequency)
        if status:
            sql += ' status = ?,'
            params.append(status)
        if category:
            sql += ' category = ?,'
            params.append(category)
        if user_id:
            sql += ' user_id = ?,'
            params.append(user_id)

        sql = sql.rstrip(',') # Удаление лишней запятой из конца запроса
        sql += ' WHERE habits_id = ?' # Добавление условия WHERE для обновления только определенной записи
        params.append(habit_id) # Добавление ID привычки в список параметров

        cur = conn.cursor() # Создание курсора для выполнения SQL-запросов
        cur.execute(sql, params) # Выполнение запроса с параметрами
        conn.commit() # Сохранение изменений

    # Статический метод для удаления привычки из базы данных
    @staticmethod
    def delete_habit(conn, habit_id):
        sql = 'DELETE FROM habits WHERE habits_id = ?' # SQL-запрос для удаления записи из таблицы habits
        cur = conn.cursor() # Создание курсора для выполнения SQL-запросов
        cur.execute(sql, (habit_id,)) # Выполнение SQL-запроса
        conn.commit() # Сохранение изменений

    # Статический метод для получения привычки из базы данных
    @staticmethod
    def get_habit(conn, habit_id):
        sql = 'SELECT * FROM habits WHERE habits_id = ?' # SQL-запрос для получения записи из таблицы habits
        cur = conn.cursor() # Создание курсора для выполнения SQL-запросов
        cur.execute(sql, (habit_id,)) # Выполнение SQL-запроса
        row = cur.fetchone() # Получение первой строки
        if row: # Если строка существует
            return Habit(*row) # Возвращение объекта Habit, созданного из строки результата запроса
        return None # Возвращение None, если запись не найдена

    # Статический метод для получения списка всех привычек
    @staticmethod
    def list_habits(conn):
        sql = 'SELECT * FROM habits' # SQL-запрос для получения всех записей из таблицы habits
        cur = conn.cursor() # Создание курсора для выполнения SQL-запросов
        cur.execute(sql) # Выполнение SQL-запроса
        rows = cur.fetchall() # Получение всех строк результата запроса
        habits = [Habit(*row) for row in rows] # Создание списка объектов Habit из строк результата
        return habits # Возвращение списка привычек
