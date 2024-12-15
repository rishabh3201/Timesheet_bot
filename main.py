
# Bot token

import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time
import pytz

# Bot token
TOKEN = '7899558751:AAFi7a23-GhAvbX5WGpglzpKuaBmVYaQ6ME'
bot = telebot.TeleBot(TOKEN)

# Scheduler instance
scheduler = BackgroundScheduler(timezone=pytz.utc)
scheduler.start()

# In-memory storage for user reminders
reminders = {}


# Start command handler
@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.id)
    # print(message.from_user.first_name)
    # print(message.from_user.last_name)
    user = message.from_user.first_name
    print(user)
    bot.reply_to(
        message,
        f"Welcome {user}! I can remind you to fill your timesheet. Use /setreminder to schedule your reminder."
    )


# Set reminder command handler
@bot.message_handler(commands=['setreminder'])
def set_reminder(message):
    msg = bot.send_message(
        message.chat.id,
        "Please enter the time (in HH:MM format, 24-hour clock) when you'd like to be reminded."
    )
    bot.register_next_step_handler(msg, process_time_input)


def process_time_input(message):
    try:
        input_time = datetime.strptime(message.text, "%H:%M").time()
        current_time = datetime.now().time()

        # Store the reminder
        chat_id = message.chat.id
        reminders[chat_id] = input_time
        last_name = message.from_user.last_name
        print(last_name)
        print(input_time)
        bot.send_message(chat_id,
                         f"Reminder set for {input_time.strftime('%H:%M')}. I'll remind you to fill your timesheet.")

        # Start checking the time
        check_reminders(last_name)
    except ValueError:
        bot.send_message(message.chat.id, "Invalid time format. Please use HH:MM format (24-hour clock).")

def check_reminders(last_name):
    print(last_name)
    while True:
        # print(chat_id)
        current_time = datetime.now().time()
        for chat_id, reminder_time in list(reminders.items()):
            # Check if the current time matches the reminder time
            if current_time.hour == reminder_time.hour and current_time.minute == reminder_time.minute:
                bot.send_message(chat_id, "⏰ Reminder: It's time to fill your timesheet!")
                # del reminders[chat_id]  # Remove the reminder after notifying

        time.sleep(30)  # Check every 30 seconds

# Process time input
# def process_time_input(message):
#     user_id = message.chat.id
#     try:
#         # Parse the time
#         reminder_time = datetime.strptime(message.text.strip(), "%H:%M").time()
#
#         # Store the reminder time
#         user_reminders[user_id] = reminder_time
#
#         # Schedule the reminder
#         schedule_reminder(user_id, reminder_time)
#
#         bot.send_message(
#             user_id,
#             f"Your reminder has been set for {reminder_time.strftime('%H:%M')} UTC. "
#             "I'll remind you to fill your timesheet every day at this time."
#         )
#     except ValueError:
#         bot.send_message(
#             message.chat.id,
#             "Invalid time format. Please enter the time in HH:MM format (24-hour clock)."
#         )
#         set_reminder(message)


# Schedule the reminder
def schedule_reminder(user_id, reminder_time):
    # Remove existing job if any
    scheduler.remove_job(str(user_id), jobstore=None)

    # Schedule a new job
    def send_reminder():
        bot.send_message(user_id, "This is your reminder to fill your timesheet!")

    # Get the next occurrence of the specified time
    now = datetime.now(pytz.utc)
    reminder_datetime = datetime.combine(now.date(), reminder_time, tzinfo=pytz.utc)
    if reminder_datetime < now:
        reminder_datetime += timedelta(days=1)

    # Schedule the job
    scheduler.add_job(
        send_reminder,
        trigger='cron',
        hour=reminder_time.hour,
        minute=reminder_time.minute,
        id=str(user_id)
    )


# Cancel reminder command handler
@bot.message_handler(commands=['cancelreminder'])
def cancel_reminder(message):
    user_id = message.chat.id
    if user_id in user_reminders:
        del user_reminders[user_id]
        scheduler.remove_job(str(user_id), jobstore=None)
        bot.send_message(user_id, "Your reminder has been canceled.")
    else:
        bot.send_message(user_id, "You don't have any active reminders to cancel.")


# Run the bot
bot.polling()
