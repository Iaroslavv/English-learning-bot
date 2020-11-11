from config.config import TOKEN
import telebot

bot = telebot.TeleBot(TOKEN)

def main_menu(message):
    list_of_levels = ["Beginner", "Elementary", "Pre-intermediate",
                      "Intermediate", "Upper-intermediate"
                      ]
    chat_id = message.from_user.id
    text = message.text
    bot.send_message(chat_id, "MAIN MENU")