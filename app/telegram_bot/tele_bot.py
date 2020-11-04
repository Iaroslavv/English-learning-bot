import telebot
from config.config import TOKEN, NGROK_URI
from flask import Blueprint, request, abort
from app.users.routes import users

bot = telebot.TeleBot(TOKEN)

web = Blueprint("Web", __name__)

BOT_URL = "https://api.telegram.org/bot{TOKEN}/setWebhook?url={NGROK_URI}".format(
    TOKEN=TOKEN,
    NGROK_URI=NGROK_URI,
    )
BOT = "{NGROK_URI}/{TOKEN}".format(NGROK_URI=NGROK_URI, TOKEN=TOKEN)

# method_get_updates = "https://api.telegram.org/bot{TOKEN}/getUpdates".format(TOKEN=TOKEN)


@web.route("/", methods=["POST", "GET"])
def webhook():
    update = request.get_json()
    print(update)
    return {"statuscode": True}, 200


@web.route("/delete_web")
def set_webhook():
    bot.remove_webhook()
    return "!", 200

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "hello")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)



