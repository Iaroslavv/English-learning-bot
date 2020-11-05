import telebot
from config.config import TOKEN, NGROK_URI
from flask import Blueprint, request, abort


bot = telebot.TeleBot(TOKEN)
web = Blueprint("Web", __name__)

BOT_URL = "https://api.telegram.org/bot{TOKEN}/setWebhook?url={NGROK_URI}/setweb".format(
    TOKEN=TOKEN,
    NGROK_URI=NGROK_URI,
    )


@web.route("/setweb", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "Hello")





