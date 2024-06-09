# Код запрашивает значения количества пропущенных напоминаний из поля missed_number_reminders_habit
# и количества выполненных напоминаний из поля completed_number_reminders_habit таблицы statistics
# по значениям имени пользователя user_name и имени привычки habit_name
# По этим данным строит круговую диаграмму % выполнения привычек за весь период.
# Предусмотрен ручной ввод имени пользователя и имени привычки

import sqlite3
from matplotlib import pyplot as plt

# Получение имени пользователя и привычки
user_name = input("Введите имя пользователя: ") # если ввод вручную
habit_name = input("Введите имя привычки: ") # если ввод вручную

# Проверка сетевого соединения и получение данных
try:
    sqlite_connection = sqlite3.connect('db_file')
    cursor = sqlite_connection.cursor()

    # Получение выполненных напоминаний
    query_completed = """
    SELECT COUNT(completed_number_reminders_habit)
    FROM statistics
    WHERE user_name = ? AND habit_name = ?
    """
    cursor.execute(query_completed, (user_name, habit_name))
    completed_habit_result = cursor.fetchone()

    if completed_habit_result is None:
        raise ValueError("Запись не найдена для данной комбинации пользователя и привычки.")
    completed_habit = completed_habit_result[0]

    # Получение пропущенных напоминаний
    query_missed = """
    SELECT COUNT(missed_number_reminders_habit)
    FROM statistics
    WHERE user_name = ? AND habit_name = ?
    """
    cursor.execute(query_missed, (user_name, habit_name))
    missed_habit_result = cursor.fetchone()

    if missed_habit_result is None:
        raise ValueError("Запись не найдена для данной комбинации пользователя и привычки.")
    missed_habit = missed_habit_result[0]

except sqlite3.Error as error:
    print("Ошибка при работе с SQLite:", error)
except ValueError as ve:
    print("Ошибка:", ve)
else:
    # Расчет процентов
    try:
        total_habits = completed_habit + missed_habit
        if total_habits == 0:
            raise ZeroDivisionError("Общее количество привычек равно нулю.")

        percent_completed_total = completed_habit * 100 / total_habits
        percent_missed_total = 100 - percent_completed_total

        # Построение диаграммы
        vals = [percent_completed_total, percent_missed_total]
        labels = ['% выполнения', '% невыполнения']
        plt.title(f"Выполнение привычки {habit_name} за весь период", fontsize=12, color='r')
        plt.pie(vals, labels=labels, autopct='%.2f')
        plt.show()

    except ZeroDivisionError as zde:
        print("Ошибка при расчете процентов:", zde)
finally:
    if sqlite_connection:
        sqlite_connection.close()
