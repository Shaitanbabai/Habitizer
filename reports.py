# Код запрашивает значения количества отправленных напоминаний из поля habit_status
# и количества выполненных напоминаний из поля reminders_status таблицы statistics
# по значениям имени пользователя user_name, имени привычки habit_name, даты начала и конца
# интересующего периода.
# По этим данным строит круговую диаграмму % выполнения привычек за интересующий период.
# Предусмотрен ручной ввод имени пользователя, имени привычки, даты начала и конца интересующего периода.

import sqlite3
from matplotlib import pyplot as plt
import datetime

# Получение имени пользователя и привычки
user_name = input("Введите имя пользователя: ")
habit_name = input("Введите имя привычки: ")
date_start = input('Введите дату начала интересующего периода через запятую, например - 2024,6,9: ')
date_end = input('Введите дату конца интересубщего периода через запятую, например - 2024,6,11: ')
# Преобразование дат
year, month, day = map(int, date_start.split(','))
custom_date_start = datetime.datetime(year, month, day)
custom_date_start_str = custom_date_start.strftime("%Y,%m,%d")
year, month, day = map(int, date_end.split(','))
custom_date_end = datetime.datetime(year, month, day)
custom_date_end_str = custom_date_start.strftime("%Y-%m-%d")

# Проверка сетевого соединения и получение данных
try:
    sqlite_connection = sqlite3.connect('db_file')
    cursor = sqlite_connection.cursor()

    # Получение отправленных напоминаний
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

    # Получение выполненных напоминаний
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
    # Расчет процентов
    try:
        if habit_status == 0:
            raise ZeroDivisionError("Количество отправленных напоминаний равно нулю.")

        percent_reminder_status = reminder_status * 100 / habit_status #% выполненных напоминаний
        percent_reminder_non = 100 - percent_reminder_status # % не выполненных напоминаний

        # Построение диаграммы
        vals = [percent_reminder_status, percent_reminder_non]
        labels = ['% выполнения', '% невыполнения']
        plt.title(f"Выполнение привычки {habit_name} с {custom_date_start_str} по {custom_date_end_str}", fontsize=12, color='r')
        plt.pie(vals, labels=labels, autopct='%.2f')
        plt.show()

    except ZeroDivisionError as zde:
        print("Ошибка при расчете процентов:", zde)
finally:
    if sqlite_connection:
        sqlite_connection.close()