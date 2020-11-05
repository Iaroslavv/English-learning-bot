import telebot
from config.config import TOKEN, NGROK_URI
from flask import Blueprint, request, abort


bot = telebot.TeleBot(TOKEN)
web = Blueprint("Web", __name__)

BOT_URL = "https://api.telegram.org/bot{TOKEN}/setWebhook?url={NGROK_URI}/setweb".format(
    TOKEN=TOKEN,
    NGROK_URI=NGROK_URI,
    )

#  set webhook for telegram bot
@web.route("/setweb", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.from_user.id

    bot.send_message(chat_id,
"""
Welcome to 'StudyEnglish with Bot'!
List of commands:
/addwords - add words to learn
/delwords - delete words from your vocabulary
/startpractice - start your exercises
/finish - finish and see the result
""")


@bot.message_handler(func=lambda m: True, content_types=["text"])
def addwords(message):
    chat_id = message.from_user.id
    bot.send_message(chat_id, "No")


