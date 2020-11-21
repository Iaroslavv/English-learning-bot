import telebot
from config.config import TOKEN
from flask import Blueprint, request, abort
from app import db
from app.models import User, NewWords
from app.telegram_bot.process_user_welcome import ProcessWelcome
from app.telegram_bot.synonyms import find_synonym
import random
from app.telegram_bot.count_poinst import UserPoints


bot = telebot.TeleBot(TOKEN)
web = Blueprint("Web", __name__)

commands = (
"""
/addwords - add words to your vocabulary
/getsynonyms - Get synonyms for words
/mywords - get your words
/myscore = get your points for correct answers
/stop - stop studying
/study - bot gives you a word and you must write the synonym for this word.
If the synonym you wrote is in the list of synonyms, you get one point.
Type in 'stop' to see the results.
The progress can be seen on your profile page on the website.
Enjoy!
""")


greeting = f"Welcome to 'StudyEnglish with Bot'! {commands}"


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
    send_welcome.unique_code = ProcessWelcome.extract_unique_code(message.text)
    chat_id = message.from_user.id
    if send_welcome.unique_code:
        send_welcome.get_username = ProcessWelcome.get_username_from_db(send_welcome.unique_code)
        if send_welcome.get_username:
            ProcessWelcome.save_chat_id(chat_id, send_welcome.unique_code)
            reply = "Hello {0}! {1} Let's add some new words into your vocabulary! Just type in any word. Press finish to stop.".format(
                send_welcome.get_username,
                greeting
            )
            mes = bot.send_message(chat_id, reply)
            bot.register_next_step_handler(mes, gather_words, send_welcome.unique_code)
        else:
            no_id = "I have no clue who you are"
            bot.send_message(chat_id, no_id)
    else:
        mistake = "Sorry, but i accept messages from registered users only.."
        bot.send_message(chat_id, mistake)


@bot.message_handler(commands=["addwords"])
def add_words(message):
    chat_id = message.from_user.id
    unique_code = send_welcome.unique_code
    msg = bot.send_message(chat_id,
    "Type in the word you want to add. Type in 'finish' to stop adding words and see the synonyms.")
    bot.register_next_step_handler(msg, gather_words, unique_code)


@bot.message_handler(commands=["study"])
def study(message):
    chat_id = message.from_user.id
    username = send_welcome.get_username
    if username:
        user = User.query.filter_by(name=username).first()
        words = NewWords.query.filter_by(person_id=user.id).all()
        choice = random.choice(words)
        msg = bot.send_message(chat_id, choice)
        bot.register_next_step_handler(msg, guess, choice)
    else:
        bot.send_message(chat_id, "Sorry, i have no clue who you are")


@bot.message_handler(commands=["mywords"])
def mywords(message):
    try:
        chat_id = message.from_user.id
        username = send_welcome.get_username
        if username:
            user = User.query.filter_by(name=username).first()
            words = NewWords.query.filter_by(person_id=user.id).all()
            get_words = '\n'.join(str(word) for word in words)
            bot.send_message(chat_id, f"Your list of words:\n{get_words}")
        else:
            bot.send_message(chat_id, "Sorry, i have no clue who you are")
    except Exception as e:
        print(str(e))
        bot.send_message(chat_id, "Ooops")


@bot.message_handler(commands=["myscore"])
def myscore(message):
    try:
        chat_id = message.from_user.id
        username = send_welcome.get_username
        if username:
            user = User.query.filter_by(name=username).first()
            total = user.user_points
            bot.send_message(chat_id, f"Your score is {total}")
        else:
            bot.send_message(chat_id, "I have no clue who you are..")
    except Exception as e:
        print(str(e))
        bot.send_message(chat_id, "Ops")


def add_words_to_vocab(word: str, unique_code: str):
    get_username = ProcessWelcome.get_username_from_db(unique_code)
    if get_username:
        user = User.query.filter_by(name=get_username).first()
        word_to_db = NewWords(user_word=word)
        db.session.add(word_to_db)
        user.new_user_words.append(word_to_db)
        db.session.commit()


answers = iter(["Come ooon", "Moooore words!", "One more!", "Don't be weak!", "One moore!!"])


def gather_words(message, unique_code: str):
    try:
        chat_id = message.from_user.id
        text = message.text
        if text == "finish":
            get_username = ProcessWelcome.get_username_from_db(unique_code)
            if get_username:
                user = User.query.filter_by(name=get_username).first()
                words = NewWords.query.filter_by(person_id=user.id).all()
                get_words = '\n'.join(str(word) for word in words)
                bot.send_message(chat_id, f"Your list of words:\n{get_words}")
            else:
                bot.send_message(chat_id, "Sorry, i don't know who you are..")      
        else:
            add_words_to_vocab(text, unique_code)
            msg = bot.send_message(chat_id, next(answers, "One more!"))
            bot.register_next_step_handler(msg, gather_words, unique_code)
    except Exception as e:
        print(str(e))
        bot.send_message(chat_id, "Ops, words havent been added..")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def other_text(message):
    try:
        chat_id = message.from_user.id
        username = send_welcome.get_username
        if username:
            bot.send_message(chat_id, "I don't understand:( Maybe try /help command?")
        else:
            bot.send_message(chat_id, "Sorry, i don't know who you are..")
    except Exception as e:
        print(str(e))
        bot.send_message(chat_id, "Ooops")


def guess(message, word):
    try:
        chat_id = message.from_user.id
        text = message.text
        synonyms = find_synonym(word)
        username = send_welcome.get_username
        if username:
            if text == "/stop":
                bot.send_message(chat_id, "Press /myscore to see your score!")
            else:
                user = User.query.filter_by(name=username).first()
                words = NewWords.query.filter_by(person_id=user.id).all()
                if text.lower() in synonyms:
                    points = UserPoints()
                    points.add_point(1)
                    print("if correct + 1 point")
                    total = points.show_points
                    print("total", total)
                    user.user_points = total
                    db.session.commit()
                    print("committed")
                    choice = random.choice(words)
                    msg = bot.send_message(chat_id, f"Correct! The next word is:\n {choice}",
                                           choice)
                    bot.register_next_step_handler(msg, guess, choice)
                if text.lower() not in synonyms:
                    print("incorrect!")
                    choice = random.choice(words)
                    msg = bot.send_message(chat_id, f"Incorrect! The next word is:\n{choice}",
                                           choice)
                    bot.register_next_step_handler(msg, guess, choice)  
        else:
            bot.send_message(chat_id, "Sorry, i have no clue who you are..")
    except Exception as e:
        print(str(e))
        bot.send_message(chat_id, "Ooooppss")
