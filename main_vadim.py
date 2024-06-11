import telebot
import sqlite3
from config import Config
from habits import Habit  # Импортируем класс Habit из habits.py
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
bot = telebot.TeleBot(Config.TELEGRAM_API_TOKEN)
message_count = 0

# Инициализация базы данных
db = HabitTrackerDatabase("habit_tracker.db")

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('habits.db')
    return conn

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
  bot.reply_to(
      message,
      "Привет! Я бот -трекер привычек (вер 1.0). Мне можно задать свои привычки , задать им напоминания , я буду тебе "
      "помогать.\nНапиши /help для просмотра команд"
  )


# Обработчик команды help
@bot.message_handler(commands=['help'])
def send_help(message):
  help_text = ("Доступные команды:\n/start - начало работы\n/help - помощь\n/habit - создать привычку \n/change - "
               "изменить привычку \n/delete - удалить привычку \n/statistics - статистика")
  bot.reply_to(message, help_text)

# Обработчик команды habit
# @bot.message_handler(commands=['habit'])
# def send_count(message):
#   bot.reply_to(message, f"Функционал в разработке. Приятно познакомиться, {message.from_user.first_name}!")

# Обработчик команды habit
@bot.message_handler(commands=['habit'])
def create_habit(message):
    try:
        # Разделяем сообщение на части
        parts = message.text.split(',')[1:]
        if len(parts) < 3:
            bot.reply_to(message, "Пожалуйста, введите все параметры привычки: /habit <название>, <описание>, <частота>")
            return

        habit_name = parts[0].strip()
        habit_description = parts[1].strip()
        habit_frequency = parts[2].strip()

        conn = get_db_connection()
        habit_id = Habit.create_habit(conn, message.from_user.id, habit_name, habit_description, habit_frequency)
        conn.close()

        bot.reply_to(message, f"Привычка '{habit_name}' была успешно создана с ID {habit_id}.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при создании привычки: {str(e)}")

# Обработчик команды habit
# @bot.message_handler(commands=['habit'])
# def create_habit(message):
#     user_id = message.from_user.id
#     habit_name = "Название привычки"  # Замените на реальное имя привычки
#     habit_description = "Описание привычки"  # Замените на реальное описание привычки
#     habit_frequency = "ежедневно"  # Замените на реальную частоту
#
#     habit_id = Habit.create_habit(db.connection, user_id, habit_name, habit_description, habit_frequency)
#     bot.reply_to(message, f"Привычка '{habit_name}' создана с ID {habit_id}")

@bot.message_handler(commands=['change'])
def change_habit(message):
    bot.reply_to(message, f"Функционал в разработке. Приятно познакомиться, {message.from_user.first_name}! ")


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


if __name__ == "__main__":
  bot.polling(non_stop=True)