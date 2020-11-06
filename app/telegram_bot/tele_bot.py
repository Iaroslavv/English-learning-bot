import telebot
from config.config import TOKEN, NGROK_URI
from flask import Blueprint, request, abort
from app import db
from app.models import User, TbotChatId
from flask_login import current_user
from app.users.routes import find_user_by_access_link


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


# get the hash code from the link on the website where /start=user's hashcode
# generated from his username
def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None


def check_if_unique_code_exists(unique_code):
    code = User.query.filter_by(access_link=unique_code).first()
    if code:
        return True
    return False


# does a query to the db, retrieving the associated username
def get_username_from_db(unique_code):
    username = find_user_by_access_link(unique_code)
    if username:
        return "ABC" if check_if_unique_code_exists(unique_code) else None


# save the chat_id>username to the db
def save_chat_id(chat_id, username):
    save_chat = TbotChatId(chat_id=chat_id, author=username)
    db.session.add(save_chat)
    db.session.commit()


@bot.message_handler(commands=["start"])
def send_welcome(message):
    unique_code = extract_unique_code(message.text)
    print("UNIQUE CODE 1", unique_code)
    print("MESSAGE", message.text.split())
    chat_id = message.from_user.id
    print("UNIQUE CODE EXISTS", unique_code)
    if unique_code:
        username = get_username_from_db(unique_code)
        print("GET USERNAME!", username)
        if username:
            save_chat_id(message.chat.id, username)
            reply = "Hello {0}, how are you?".format(username)
        else:
            reply = "I have no clue who you are"
    else:
        reply = "Doesn't work!"
    bot.send_message(chat_id, reply)



# user_dict = {}
# list_answers = iter(["One more?", "Come on!", "Don't be afraid!", "Yeeaahhhh",
#                 "Moooore", "Give me more words!", "It is never too late to learn new words!",
#                 "I believe in you!", "I am tired.."])


# @bot.message_handler(commands=["start"])
# def send_welcome(message):
#     chat_id = message.from_user.id
#     # print(find_user_by_access_link())
#     msg = bot.send_message(chat_id,
# """
# Welcome to 'StudyEnglish with Bot'!
# List of commands:
# /addwords - add words to learn
# /delwords - delete words from your vocabulary
# /startpractice - start your exercises
# /finish - finish and see the result
# Type in words like this, e.g.:
# join
# amazing
# and write the command, e.g. /addwords
# """)
#     bot.register_next_step_handler(msg, process_word_step)


# class TBUser:
#     def __init__(self, words):
#         self.words = words


# def process_word_step(message):
#     try:
#         chat_id = message.from_user.id
#         word = message.text
#         tbuser = TBUser(word)
#         user_dict[chat_id] = tbuser
#         msg = bot.send_message(chat_id, next(list_answers, "the last one?"))
#         bot.register_next_step_handler(msg, process_word_step)
#     except Exception:
#         bot.reply_to(message, "oops")
       
# print(user_dict)
        



