import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('habits.db')
    cur = conn.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS habits (
                habits_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_habit TEXT NOT NULL,
                habit_description TEXT,
                name_targets TEXT,
                habit_frequency TEXT,
                status TEXT,
                date_entry TEXT,
                category TEXT,
                user_id INTEGER
            );''')
    conn.commit()
    conn.close()

class Habit:
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

    @staticmethod
    def create_habit(conn, name_habit, habit_description, name_targets, habit_frequency, category, user_id):
        date_entry = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "active"
        sql = '''INSERT INTO habits (name_habit, habit_description, name_targets, habit_frequency, status, date_entry, category, user_id)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        cur = conn.cursor()
        cur.execute(sql, (name_habit, habit_description, name_targets, habit_frequency, status, date_entry, category, user_id))
        conn.commit()
        return cur.lastrowid

    @staticmethod
    def edit_habit(conn, habit_id, name_habit=None, habit_description=None, name_targets=None, habit_frequency=None,
                   status=None, category=None, user_id=None):
        sql = 'UPDATE habits SET'
        params = []
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

        sql = sql.rstrip(',')
        sql += ' WHERE habits_id = ?'
        params.append(habit_id)

        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()

    @staticmethod
    def delete_habit(conn, habit_id):
        sql = 'DELETE FROM habits WHERE habits_id = ?'
        cur = conn.cursor()
        cur.execute(sql, (habit_id,))
        conn.commit()

    @staticmethod
    def get_habit(conn, habit_id):
        sql = 'SELECT * FROM habits WHERE habits_id = ?'
        cur = conn.cursor()
        cur.execute(sql, (habit_id,))
        row = cur.fetchone()
        if row:
            return Habit(*row)
        return None

    @staticmethod
    def list_habits(conn):
        sql = 'SELECT * FROM habits'
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        habits = [Habit(*row) for row in rows]
        return habits

    # Тест:
def main():
    init_db()
    with sqlite3.connect('habits.db') as conn:
        habit_id = Habit.create_habit(conn, "Зарядка", "Ежедневная утренняя разминка", "Спорт", "Каждый день",
                                      "Напоминать", 1)
        print(f"Создание новой привычки с ID: {habit_id}")

        habit = Habit.get_habit(conn, habit_id)
        print(f"Получение только что созданной привычки по её ID: {habit.name_habit}")

        Habit.edit_habit(conn, habit_id, status="Выполнено")
        print(f"Обновление статуса привычки на 'Выполнено'")

        habits = Habit.list_habits(conn)
        print(f"Получение списка всех привычек: {len(habits)}")

        Habit.delete_habit(conn, habit_id)
        print(f"Удаление привычки по её ID: {habit_id}")

if __name__ == "__main__":
    main()