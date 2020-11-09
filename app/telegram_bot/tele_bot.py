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

greeting = "Welcome to 'StudyEnglish with Bot'!"

count_correct_answers = 0

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


def check_if_unique_code_exists(unique_code) -> bool:
    code = User.query.filter_by(access_link=unique_code).first()
    if code:
        return True
    return False


# does a query to the db, retrieving the associated username
def get_username_from_db(unique_code) -> str:
    username = find_user_by_access_link(unique_code)
    if username:
        return username.name if check_if_unique_code_exists(unique_code) else None


# save the chat_id>username to the db
def save_chat_id(chat_id):
    save_chat = TbotChatId(user_chat_id=chat_id)
    print(save_chat)
    db.session.add(save_chat)
    db.session.commit()


@bot.message_handler(commands=["start"])
def send_welcome(message):
    unique_code = extract_unique_code(message.text)
    chat_id = message.from_user.id
    if unique_code:
        get_username = get_username_from_db(unique_code)
        if get_username:
            save_chat_id(chat_id)
            reply = "Hello {0}! {1} Do you want to pass English knowledge test? yes/no".format(
                get_username,
                greeting
            )
            bot.register_next_step_handler(reply, process_test)
        else:
            no_id = "I have no clue who you are"
            bot.send_message(chat_id, no_id)
    else:
        mistake = "Oooops, something went wrong.."
        bot.send_message(chat_id, mistake)


def process_test(message):
    chat_id = message.from_user.id
    print(chat_id)
    text = message.text
    if text == "Yes":
        bot.register_next_step_handler(
"""You will be given 50 questions in this format:
Question:
1. Answer
2. Answer
3. Answer
Type in the number of the answer to go to the next question.
""", process_test2)
    else:
        bot.send_message(chat_id, "Please, choose your level of English knowledge" )


def process_test2(message):
    pass

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
        



