from datetime import datetime

from database import HabitTrackerDatabase


if __name__ == "__main__":

    db = HabitTrackerDatabase("habit_tracker.db")
    #
    # # Добавление новых пользователей в БД
    # db.add_user(5185362611, "Эдуард")
    # db.add_user(258128224, "Денис")
    # db.add_user(949247259, "Юрий")
    # db.add_user(1328953283, "Лев")
    # db.add_user(388383693, "Татьяна")
    #
    # # Добавление новых привычек в БД
    # db.add_habit(1, "Правильное питание", "Есть овощи 3 раза в день", 3,
    #              "07:00", "19:00")
    # db.add_habit(1, "Водопой", "Пить воду 6 раз в день", 6,
    #              "07:00", "19:00")
    # db.add_habit(1, "Спорт", "Заниматься спортом 1 раз в день", 1,
    #              "18:00", "22:00")
    #
    # db.add_habit(2, "Утренняя зарядка", "Делать зарядку по утрам", 1,
    #              "06:00", "06:30")
    # db.add_habit(2, "Чтение книг", "Читать книги каждый день по 30 минут", 1,
    #              "20:00", "20:30")
    # db.add_habit(2, "Пить воду", "Пить 8 стаканов воды в день", 8,
    #              "08:00", "22:00")
    #
    # db.add_habit(3, "Медитация", "Медитировать по утрам", 1,
    #              "07:30", "08:00")
    # db.add_habit(3, "Изучение иностранного языка", "Изучать английский язык 1 час каждый день",
    #              1, "18:00", "19:00")
    # db.add_habit(3, "Беговые тренировки", "Бегать 4 раза в день", 4,
    #              "06:00", "18:00")
    #
    # # Эмуляция текущего времени, вводимого пользователем
    # current_time_input = ["06:00", "07:00", "07:30", "08:00", "09:00", "09:45", "11:00", "11:30", "12:00", "13:00",
    #                       "13:15", "15:00", "16:45", "17:00", "18:00", "18:30", "20:00", "20:15"]
    #
    # # Перебор значений времени из списка
    # for time_input in current_time_input:
    #     current_time = datetime.strptime(time_input, "%H:%M")
    #
    #     # ID пользователя для тестирования
    #     for i in range(1, 4):
    #         user_id = i
    #         db.send_reminders_based_on_time(user_id, current_time)

    # user_id = 2
    # db.send_reminders_based_on_time(user_id, current_time)
    #
    # user_id = 3
    # db.send_reminders_based_on_time(user_id, current_time)
    #
    # user_id = 4
    # db.send_reminders_based_on_time(user_id, current_time)

    # reminder_id = 26
    # user_id = 3
    # habit_id = 9
    # response_time = "2024-06-10 15:15:00"
    # db.add_user_response(user_id, habit_id, reminder_id, response_time)

    db.close_connection()
