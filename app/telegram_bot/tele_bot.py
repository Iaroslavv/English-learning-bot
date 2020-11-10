import telebot
from config.config import TOKEN, NGROK_URI
from flask import Blueprint, request, abort
from app import db
from app.models import User, TbotChatId
from app.users.routes import find_user_by_access_link
from app.telegram_bot.count_user_points import TestCounter


bot = telebot.TeleBot(TOKEN)
web = Blueprint("Web", __name__)

BOT_URL = "https://api.telegram.org/bot{TOKEN}/setWebhook?url={NGROK_URI}/setweb".format(
    TOKEN=TOKEN,
    NGROK_URI=NGROK_URI,
    )

greeting = "Welcome to 'StudyEnglish with Bot'!"


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


def check_if_unique_code_exists(unique_code: str) -> bool:
    code = User.query.filter_by(access_link=unique_code).first()
    if code:
        return True
    return False


# does a query to the db, retrieving the associated username
def get_username_from_db(unique_code: str) -> str:
    username = find_user_by_access_link(unique_code)
    if username:
        return username.name if check_if_unique_code_exists(unique_code) else None


# save the chat_id>username to the db
def save_chat_id(chat_id):
    chat = TbotChatId(user_chat_id=chat_id)
    db.session.add(chat)
    User.user_chat = chat
    user = User.query.first()
    print("USER INFO", user)



@bot.message_handler(commands=["start"])
def send_welcome(message):
    unique_code = extract_unique_code(message.text)
    chat_id = message.from_user.id
    if unique_code:
        print("CHAT ID", chat_id)
        get_username = get_username_from_db(unique_code)
        if get_username:
            save_chat_id(chat_id)
            reply = "Hello {0}! {1} Do you want to pass English knowledge test? yes/no".format(
                get_username,
                greeting
            )
            mes = bot.send_message(chat_id, reply)
            bot.register_next_step_handler(mes, process_test)
        else:
            no_id = "I have no clue who you are"
            bot.send_message(chat_id, no_id)
    else:
        mistake = "Oooops, something went wrong.."
        bot.send_message(chat_id, mistake)


def process_test(message):
    try:
        chat_id = message.from_user.id
        print("Process test chatid", chat_id)
        text = message.text
        if text == "Yes" or text == "yes":
            msg = bot.send_message(chat_id,
"""
You will be given 50 questions in this format:
Question:
1. Answer
2. Answer
3. Answer
Type in the number of the answer to go to the next question.
If you want to start now, type 'begin'
""")
            bot.register_next_step_handler(msg, process_test2)
        elif text == "No" or "no":
            bot.send_message(chat_id, "Please, choose your level of English knowledge")  # need to add buttons
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test2(message):
    try:
        chat_id = message.from_user.id
        print("Process test2 chatid", chat_id)
        text = message.text
        if text == "begin":
            msg = bot.send_message(chat_id,
"""
How many people ____ in your family?
1. are they
2. is it
3. are there
4. is
""")    
            bot.register_next_step_handler(msg, process_test3)
        else:
            bot.register_next_step_handler(msg, process_test)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test3(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 3", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test3)
            return
        if answer.isdigit() and answer == "3":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
What time is it? ____
1. Ten and a quarter
2. Ten minus the quarter
3. A quarter past ten
4. Fiften after ten o'clock
""")    
            bot.register_next_step_handler(msg, process_test4)
        elif answer != "3":
            bot.register_next_step_handler(msg, process_test4)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")

  
def process_test4(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 4", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test4)
            return
        if answer.isdigit() and answer == "3":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I get up at 8 o'clock ____ morning.
1. in the
2. in
3. the
4. at the
""")    
            bot.register_next_step_handler(msg, process_test5)
        elif answer != "3":
            bot.register_next_step_handler(msg, process_test5)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")
    

def process_test5(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 5", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test5)
            return
        if answer.isdigit() and answer == "1":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
How much ____ where you live?
1. do houses cost
2. does houses cost
3. does cost houses
4. do cost houses
""")  
            bot.register_next_step_handler(msg, process_test6)
        elif answer != "1":
            bot.register_next_step_handler(msg, process_test6)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test6(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 6", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test6)
            return
        if answer.isdigit() and answer == "1":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
Where are you going __ Friday?
1. at
2. in
3. on
4. the
""")    
            bot.register_next_step_handler(msg, process_test7)
        elif answer != "1":
            bot.register_next_step_handler(msg, process_test7)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test7(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 7", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test7)
            return
        if answer.isdigit() and answer == "3":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
____come to my party next Saturday?
1. Do you can
2. Can you to
3. Can you
4. Do you
""")    
            bot.register_next_step_handler(msg, process_test8)
        elif answer != "3":
            bot.register_next_step_handler(msg, process_test8)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test8(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 8", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test8)
            return
        if answer.isdigit() and answer == "3":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
What ___ in London last weekend?
1. you were doing
2. did you do
3. you did
4. did you
""")    
            bot.register_next_step_handler(msg, process_test9)
        elif answer != "3":
            bot.register_next_step_handler(msg, process_test9)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test9(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 9", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test9)
            return
        if answer.isdigit() and answer == "2":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
Is your English improving?____
1. I hope it
2. Hoping
3. I hope so
4. I hope
""")    
            bot.register_next_step_handler(msg, process_test10)
        elif answer != "2":
            bot.register_next_step_handler(msg, process_test10)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test10(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 10", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test10)
            return
        if answer.isdigit() and answer == "3":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I am going to Sainsbury's ___ some food.
1. buy
2. for buy
3. for buying
4. to buy
""")    
            bot.register_next_step_handler(msg, process_test11)
        elif answer != "3":
            bot.register_next_step_handler(msg, process_test11)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test11(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 11", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test11)
            return
        if answer.isdigit() and answer == "4":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
NY is the most attractive city _____
1. i've ever seen
2. that i see
3. that i saw already
4. i've never seen
""")    
            bot.register_next_step_handler(msg, process_test12)
        elif answer != "4":
            bot.register_next_step_handler(msg, process_test12)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test12(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 12", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test12)
            return
        if answer.isdigit() and answer == "1":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
Oxford isn't _____ Bath
1. as beautiful than
2. so beautiful than
3. so beautiful that
4. as beautiful as
""")    
            bot.register_next_step_handler(msg, process_test13)
        elif answer != "1":
            bot.register_next_step_handler(msg, process_test13)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test13(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 13", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test13)
            return
        if answer.isdigit() and answer == "4":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
He was mowling the lawn when i ____ him yesterday.
1. saw
2. had seen
3. have seen
4. was seeing
""")    
            bot.register_next_step_handler(msg, process_test14)
        elif answer != "4":
            bot.register_next_step_handler(msg, process_test14)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test14(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 14", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test14)
            return
        if answer.isdigit() and answer == "1":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
Last Tuesday I ____ to the Passport Office
1. must gone
2. must go
3. had to go
4. had gone
""")    
            bot.register_next_step_handler(msg, process_test15)
        elif answer != "1":
            bot.register_next_step_handler(msg, process_test15)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test15(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 15", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test15)
            return
        if answer.isdigit() and answer == "3":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
What were you doing at 7:30 on Wednesday evening?
I ____ TV
1. saw
2. watched
3. was watching
4. was watched
""")    
            bot.register_next_step_handler(msg, process_test16)
        elif answer != "3":
            bot.register_next_step_handler(msg, process_test16)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test16(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 16", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test16)
            return
        if answer.isdigit() and answer == "3":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
What time ___ to bed during the week?
1. do you go
2. do you going
3. are you going
4. do you going
""")    
            bot.register_next_step_handler(msg, process_test17)
        elif answer != "3":
            bot.register_next_step_handler(msg, process_test17)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test17(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 17", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test17)
            return
        if answer.isdigit() and answer == "1":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
Do you like Los Angeles?___
1. I like
2. I do
3. I does
4. So do I
""")    
            bot.register_next_step_handler(msg, process_test18)
        elif answer != "1":
            bot.register_next_step_handler(msg, process_test18)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test18(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 18", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test18)
            return
        if answer.isdigit() and answer == "2":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I am afraid i haven't got ___
1. any clothes
2. some clothes
3. clothes
4. no clothes
""")    
            bot.register_next_step_handler(msg, process_test19)
        elif answer != "2":
            bot.register_next_step_handler(msg, process_test19)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test19(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 19", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test19)
            return
        if answer.isdigit() and answer == "1":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
This book is mine and that one is ___
1. yours
2. your's
3. you're
4. your
""")    
            bot.register_next_step_handler(msg, process_test20)
        elif answer != "1":
            bot.register_next_step_handler(msg, process_test20)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test20(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        print("Test 20", answer)
        if not answer.isdigit():
            msg = bot.reply_to(message, "Your answer must be a digit!")
            bot.register_next_step_handler(msg, process_test20)
            return
        if answer.isdigit() and answer == "1":
            count_correct_answers = TestCounter()
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
This book is mine and that one is ___
1. yours
2. your's
3. you're
4. your
""")    
            bot.register_next_step_handler(msg, process_test20)
        elif answer != "1":
            bot.register_next_step_handler(msg, process_test20)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")