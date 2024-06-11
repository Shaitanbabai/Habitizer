from datetime import datetime
import threading
import time
import telebot
from telebot import types
from database import HabitTrackerDatabase
# import requests
# from openai import OpenAI
# from config import api_key1
# # Настройка клиента API OpenAI (убедитесь, что используете корректный метод для вашего случая)
# client = OpenAI(
#     api_key=api_key1,
#     base_url=
#     "https://api.proxyapi.ru/openai/v1",  # Проверьте этот URL, возможно, нужно использовать официальный URL OpenAI.
# )


# Инициализация бота
from config import Config

bot = telebot.TeleBot(Config.TELEGRAM_API_TOKEN)
message_count = 0
db = HabitTrackerDatabase('habit_tracker.db')


# def chat_with_ai(initial_message):
#   """
#   Функция для получения ответа от AI.
#   """
#   chat_history = [{"role": "user", "content": initial_message}]
#   chat_completion = client.chat.completions.create(model="gpt-3.5-turbo-1106",
#                                                    messages=chat_history)
#   chat_history.append({
#       "role": "system",
#       "content": "отвечай в стиле веселого ученого"
#   })
#   reply = chat_completion.choices[0].message.content  # Получение ответа от AI
#   return reply


# Обработчик команды start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_tg_id = message.from_user.id
    # print(user_tg_id)

    # Проверяем, есть ли пользователь в базе данных
    query_check = "SELECT COUNT(*) FROM users WHERE user_tg_id = ?"
    result = db.execute_query(query_check, (user_tg_id,), fetch=True)
    # db.close_connection()
    # print(result)

    if result and result[0][0] > 0:
        user_name = db.get_user_name_by_user_tg_id(user_tg_id)
        bot.reply_to(
            message,
            f"Привет, {user_name}! Я бот-трекер привычек (вер 1.0). Мне можно задать свои привычки , задать им напоминания, я буду тебе помогать.\nНапиши /help для просмотра команд"
        )
    else:
        # Запрашиваем у пользователя его имя
        msg = bot.reply_to(message, "Привет, Гость!  Для продолжения, предлагаю познакомиться. Я бот-трекер привычек (вер 1.0). Пожалуйста, напишите ваше имя:")
        bot.register_next_step_handler(msg, get_user_name, user_tg_id)

    reminder_thread = threading.Thread(target=check_and_send_reminders, args=(message.chat.id,))
    reminder_thread.start()


def get_user_name(message, user_tg_id):
    user_name = message.text
    # Добавляем пользователя в базу данных
    db.add_user(user_tg_id, user_name)
    bot.reply_to(message, f"Спасибо, {user_name}! Вы зарегистрированы.\nТеперь вы можете задавать свои привычки и напоминания.")


# Обработчик команды help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = ("Доступные команды:\n/start - начало работы\n/help - помощь\n/habit - создать привычку \n/change - "
                 "изменить привычку \n/delete - удалить привычку \n/statistics - статистика")
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['habit'])
def send_count(message):
    user_tg_id = message.from_user.id
    user_id = db.get_user_id_by_user_tg_id(user_tg_id)

    msg = bot.reply_to(message, "Введите название привычки (например: Правильное питание):")
    bot.register_next_step_handler(msg, get_habit_name, user_id)


def get_habit_name(message, user_id):
    habit_name = message.text
    msg = bot.reply_to(message, "Введите описание привычки (например: Есть овощи 3 раза в день):")
    bot.register_next_step_handler(msg, get_habit_description, user_id, habit_name)


def get_habit_description(message, user_id, habit_name):
    habit_description = message.text
    msg = bot.reply_to(message, "Введите частоту повторения привычки (например: 3 раза в день). Вводите только число:")
    bot.register_next_step_handler(msg, get_habit_frequency, user_id, habit_name, habit_description)


def get_habit_frequency(message, user_id, habit_name, habit_description):
    try:
        habit_frequency = int(message.text)
        if habit_frequency <= 0:
            raise ValueError
    except ValueError:
        msg = bot.reply_to(message, "Частота повторения должна быть целым положительным числом. Пожалуйста, попробуйте снова:")
        bot.register_next_step_handler(msg, get_habit_frequency, user_id, habit_name, habit_description)
        return

    msg = bot.reply_to(message, "Введите время начала оповещения (например: 07:00):")
    bot.register_next_step_handler(msg, get_reminder_time_from, user_id, habit_name, habit_description, habit_frequency)


def get_reminder_time_from(message, user_id, habit_name, habit_description, habit_frequency):
    reminder_time_from = message.text
    try:
        datetime.strptime(reminder_time_from, "%H:%M")
    except ValueError:
        msg = bot.reply_to(message, "Время начала оповещения должно быть в формате ЧЧ:ММ. Пожалуйста, попробуйте снова:")
        bot.register_next_step_handler(msg, get_reminder_time_from, user_id, habit_name, habit_description, habit_frequency)
        return

    msg = bot.reply_to(message, "Введите время окончания оповещения (например: 19:00):")
    bot.register_next_step_handler(msg, get_reminder_time_till, user_id, habit_name, habit_description, habit_frequency, reminder_time_from)


def get_reminder_time_till(message, user_id, habit_name, habit_description, habit_frequency, reminder_time_from):
    reminder_time_till = message.text
    try:
        datetime.strptime(reminder_time_till, "%H:%M")
    except ValueError:
        msg = bot.reply_to(message, "Время окончания оповещения должно быть в формате ЧЧ:ММ. Пожалуйста, попробуйте снова:")
        bot.register_next_step_handler(msg, get_reminder_time_till, user_id, habit_name, habit_description, habit_frequency, reminder_time_from)
        return

    # Добавляем привычку в базу данных
    # print(f"{user_id}, {habit_name}, {habit_description}, {habit_frequency}, {reminder_time_from}, {reminder_time_till}")
    db.add_habit(user_id, habit_name, habit_description, habit_frequency, reminder_time_from, reminder_time_till)
    bot.reply_to(message, f"Привычка '{habit_name}' добавлена успешно!")
    db.close_connection()


@bot.message_handler(commands=['change'])
def change_habit(message):
    bot.reply_to(message, f"Функционал в разработке. Приятно познакомиться, {message.from_user.first_name}!")


@bot.message_handler(commands=['delete'])
def delete_habit(message):
    bot.reply_to(message, f"Функционал в разработке. Приятно познакомиться, {message.from_user.first_name}!")


@bot.message_handler(commands=['statistics'])
def statistics(message):
    bot.reply_to(message, f"Функционал в разработке. Приятно познакомиться, {message.from_user.first_name}!")


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    pass


# Обработчик поиска


def handle_all_messages(message):
    pass
    # reply = chat_with_ai(message.text)  # Получение ответа от AI
    # bot.reply_to(message, reply)  # Отправка ответа пользователю


def check_and_send_reminders(chat_id):
    while True:
        current_time = datetime.now().strftime("%H:%M")
        reminders = db.get_due_reminders(current_time)
        print(current_time, reminders)
        for reminder in reminders:
            user_id, habit_name, habit_description, reminder_id, habit_id = reminder
            bot.send_message(user_id, f"Текущее время {current_time}. Направляю напоминание, что Вам необходимо выполнить следующее: Название привычки: {habit_name}, Описание привычки: {habit_description}")
            db.send_reminder_and_log_statistics(user_id, habit_id, reminder_id)
        time.sleep(60)


if __name__ == "__main__":
    bot.polling(non_stop=True)