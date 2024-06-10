# Код запрашивает значения количества пропущенных напоминаний из поля missed_number_reminders_habit
# количества выполненных напоминаний из поля completed_number_reminders_habit
# значения количества отправленных напоминаний из поля habit_status
# количества выполненных напоминаний из поля reminders_status
# таблицы statistics
# По этим данным строит круговую диаграмму % выполнения привычек за весь период.
# строит круговую диаграмму % выполнения привычек за интересующий период.
# строит сравнительную гистограмму
# Все графики выводятся последовательно


import sqlite3
from matplotlib import pyplot
import datetime

# Данные для проверки построения
# completed_habit = 10 # выполнено всего
# missed_habit = 7 # не выполнено всего
# habit_status = 9 # отправлено напоминаний за период
# reminder_status = 5 # выполнено напоминаний за период

# Получение имени пользователя,  привычки и дат для анализа за период
user_name = input("Введите имя пользователя: ") # если ввод вручную
habit_name = input("Введите имя привычки: ") # если ввод вручную
date_start = input('Введите дату начала интересующего периода через запятую, например - 2024,6,9: ') # если ввод вручную
date_end = input('Введите дату конца интересующего периода через запятую, например - 2024,6,11: ') #если ввод вручную
# Преобразование дат
year, month, day = map(int, date_start.split(','))
custom_date_start = datetime.datetime(year, month, day)
custom_date_start_str = custom_date_start.strftime("%Y-%m-%d")
year, month, day = map(int, date_end.split(','))
custom_date_end = datetime.datetime(year, month, day)
custom_date_end_str = custom_date_end.strftime("%Y-%m-%d")

# Проверка сетевого соединения и получение данных
try:
    sqlite_connection = sqlite3.connect('db_file')
    cursor = sqlite_connection.cursor()

    # Получение выполненных напоминаний за весь период
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

    # Получение пропущенных напоминаний за весь период
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

    # Получение отправленных напоминаний за выбранный период
    query_completed = """
        SELECT COUNT(habit_status)
        FROM statistics
        WHERE user_name = ? AND habit_name = ? AND custom_date_start_str = ? AND custom_date_end_str = ?
        AND reminder_sending_date > custom_date_start_str AND reminder_sending_date < custom_date_end_str
        """
    cursor.execute(query_completed, (user_name, habit_name, custom_date_start_str, custom_date_end_str,))
    habit_status_result = cursor.fetchone()

    if habit_status_result is None:
        raise ValueError("Запись не найдена для данной комбинации пользователя и привычки.")
    habit_status = habit_status_result[0]

> Юрий:
# Получение выполненных напоминаний за выбранный период
    query_missed = """
       SELECT COUNT(reminder_status)
       FROM statistics
       WHERE user_name = ? AND habit_name = ? AND custom_date_start_str = ? AND custom_date_end_str = ?
       AND reminder_sending_date > custom_date_start_str AND reminder_sending_date < custom_date_end_str
       AND reminder_status = 1
       """
    cursor.execute(query_missed, (user_name, habit_name, custom_date_start_str, custom_date_end_str,))
    reminder_status_result = cursor.fetchone()

    if reminder_status_result is None:
        raise ValueError("Запись не найдена для данной комбинации пользователя и привычки.")
    reminder_status = reminder_status_result[0]

except sqlite3.Error as error:
    print("Ошибка при работе с SQLite:", error)
except ValueError as ve:
    print("Ошибка:", ve)
else:
    #Расчет процентов
   try:
        total_habits = completed_habit + missed_habit
        if total_habits == 0:
            raise ZeroDivisionError("Общее количество привычек равно нулю.")

        if habit_status == 0:
            raise ZeroDivisionError("Количество отправленных напоминаний равно нулю.")

        #Расчет процентов для всего периода
        percent_completed_total = completed_habit * 100 / total_habits
        percent_missed_total = 100 - percent_completed_total

        # расчет процентов за период
        percent_reminder_status = reminder_status * 100 / habit_status  # % выполненных напоминаний
        percent_reminder_non = 100 - percent_reminder_status  # % не выполненных напоминаний

        # Построение диаграммы для всего периода
        vals = [percent_completed_total, percent_missed_total]
        labels = ['% выполнения', '% невыполнения']
        plt.title(f"Выполнение привычки {habit_name} за весь период", fontsize=12, color='r')
        plt.pie(vals, labels=labels, autopct='%.2f')
        plt.show()

        # Построение диаграммы за период
        vals = [percent_reminder_status, percent_reminder_non]
        labels = ['% выполнения', '% невыполнения']
        plt.title(f"Выполнение привычки {habit_name} с {custom_date_start_str} по {custom_date_end_str}", fontsize=12,
                  color='r')
        plt.pie(vals, labels=labels, autopct='%.2f')
        plt.show()

        # Построение гистограммы
        plt.title(f"Сравнение выполнения привычек", fontsize=12, color='r')
        x = ['весь период', 'заданный период']
        y = [percent_missed_total, percent_reminder_status]
        plt.bar(x, y, width=0.5, linewidth=2, edgecolor='m')
        plt.show()

   except ZeroDivisionError as zde:
        print("Ошибка при расчете процентов:", zde)
finally:
    if sqlite_connection:
        sqlite_connection.close()
