import telebot
from config.config import TOKEN
from flask import Blueprint, request, abort
from app import db
from app.models import User, TbotChatId
from app.users.routes import find_user_by_access_link
from telebot import types
from app.telegram_bot.count_user_points import TestCounter


bot = telebot.TeleBot(TOKEN)
web = Blueprint("Web", __name__)
count_correct_answers = TestCounter()

commands =(
"""
/test - start a test
/chooselevel - choose your level of English
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
    print(User.query.first())


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
            mes = bot.send_message(chat_id, reply)
            bot.register_next_step_handler(mes, process_test)
        else:
            no_id = "I have no clue who you are"
            bot.send_message(chat_id, no_id)
    else:
        mistake = "Sorry, but i accept messages from registered users only.."
        bot.send_message(chat_id, mistake)


@bot.message_handler(commands=["chooselevel"])
def choose_level(message):
    chat_id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='beginner', callback_data=1))
    markup.add(types.InlineKeyboardButton(text='elementary', callback_data=2))
    markup.add(types.InlineKeyboardButton(text='pre intermediate', callback_data=3))
    bot.send_message(chat_id, text="Please, specify you English level knowledge",
                     reply_markup=markup)


def process_test(message):
    try:
        chat_id = message.from_user.id
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
        elif text == "No" or text == "no":
            chat_id = message.from_user.id
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text='beginner',
                                                          callback_data=1))
            markup.add(telebot.types.InlineKeyboardButton(text='elementary',
                                                          callback_data=2))
            markup.add(telebot.types.InlineKeyboardButton(text='pre intermediate',
                                                          callback_data=3))
            bot.send_message(chat_id, text="Please, specify you English level knowledge",
                             reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


@bot.callback_query_handler(func=lambda call: True)
def query_menu(call):
    if call.data.lower() == "1":
        msg = "beginnerrr"
    elif call.data.lower() == "2":
        msg = "elementaryy"
    elif call.data.lower() == "3":
        msg = "pre intermediatee"
    bot.send_message(call.message.chat.id, msg)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


def process_test2(message):
    try:
        chat_id = message.from_user.id
        print("chat id from process test 2")
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
            print("before sending message process test 2")
            bot.register_next_step_handler(msg, process_test3)
        else:
            msg = bot.send_message(chat_id, "Sorry? Type 'begin' to start the test")
            bot.register_next_step_handler(msg, process_test2)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test3(message):
    try:
        chat_id = message.from_user.id
        print("process test3 chat id", chat_id)
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
What time is it? ____
1. Ten and a quarter
2. Ten minus the quarter
3. A quarter past ten
4. Fiften after ten o'clock
""")        
            print("before sending mess in process_test 3")
            bot.register_next_step_handler(msg, process_test4)
        else:
            msg = bot.send_message(chat_id,
"""
What time is it? ____
1. Ten and a quarter
2. Ten minus the quarter
3. A quarter past ten
4. Fiften after ten o'clock
""")     
            bot.register_next_step_handler(msg, process_test4)
    except Exception:
        print(Exception)
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test4(message):
    try:
        chat_id = message.from_user.id
        print("chat id test 4")
        answer = message.text
        if answer == "3":
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
        else:
            msg = bot.send_message(chat_id,
"""
I get up at 8 o'clock ____ morning.
1. in the
2. in
3. the
4. at the
""")  
            bot.register_next_step_handler(msg, process_test5)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")
    

def process_test5(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
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
        else:
            print("Point not added")
            msg = bot.send_message(chat_id,
"""
How much ____ where you live?
1. do houses cost
2. does houses cost
3. does cost houses
4. do cost houses
""") 
            bot.register_next_step_handler(msg, process_test6)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test6(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
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
        else:
            msg = bot.send_message(chat_id,
"""
Where are you going __ Friday?
1. at
2. in
3. on
4. the
""") 
            bot.register_next_step_handler(msg, process_test7)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test7(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
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
        else:
            msg = bot.send_message(chat_id,
"""
____come to my party next Saturday?
1. Do you can
2. Can you to
3. Can you
4. Do you
""") 
            bot.register_next_step_handler(msg, process_test8)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test8(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
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
        else:
            msg = bot.send_message(chat_id,
"""
What ___ in London last weekend?
1. you were doing
2. did you do
3. you did
4. did you
""")   
            bot.register_next_step_handler(msg, process_test9)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test9(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer.isdigit() and answer == "2":
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
        else:
            msg = bot.send_message(chat_id,
"""
Is your English improving?____
1. I hope it
2. Hoping
3. I hope so
4. I hope
""") 
            bot.register_next_step_handler(msg, process_test10)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test10(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
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
        else:
            msg = bot.send_message(chat_id,
"""
I am going to Sainsbury's ___ some food.
1. buy
2. for buy
3. for buying
4. to buy
""") 
            bot.register_next_step_handler(msg, process_test11)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test11(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "4":
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
        else:
            msg = bot.send_message(chat_id,
"""
NY is the most attractive city _____
1. i've ever seen
2. that i see
3. that i saw already
4. i've never seen
""") 
            bot.register_next_step_handler(msg, process_test12)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test12(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
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
        else:
            msg = bot.send_message(chat_id,
"""
Oxford isn't _____ Bath
1. as beautiful than
2. so beautiful than
3. so beautiful that
4. as beautiful as
""") 
            bot.register_next_step_handler(msg, process_test13)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test13(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "4":
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
        else:
            msg = bot.send_message(chat_id,
"""
He was mowling the lawn when i ____ him yesterday.
1. saw
2. had seen
3. have seen
4. was seeing
""")
            bot.register_next_step_handler(msg, process_test14)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test14(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
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
        else:
            msg = bot.send_message(chat_id,
"""
Last Tuesday I ____ to the Passport Office
1. must gone
2. must go
3. had to go
4. had gone
""")   
            bot.register_next_step_handler(msg, process_test15)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test15(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
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
        else:
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
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test16(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
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
        else:
            msg = bot.send_message(chat_id,
"""
What time ___ to bed during the week?
1. do you go
2. do you going
3. are you going
4. do you going
""")
            bot.register_next_step_handler(msg, process_test17)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test17(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
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
        else:
            msg = bot.send_message(chat_id,
"""
Do you like Los Angeles?___
1. I like
2. I do
3. I does
4. So do I
""")
            bot.register_next_step_handler(msg, process_test18)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test18(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
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
        else:
            msg = bot.send_message(chat_id,
"""
I am afraid i haven't got ___
1. any clothes
2. some clothes
3. clothes
4. no clothes
""")
            bot.register_next_step_handler(msg, process_test19)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test19(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
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
        else:
            msg = bot.send_message(chat_id,
"""
This book is mine and that one is ___
1. yours
2. your's
3. you're
4. your
""")
            bot.register_next_step_handler(msg, process_test20)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test20(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
Would you mind ___ me that pencil?
1. to pass to
2. pass
3. passing
4. that you should pass
""")        
            bot.register_next_step_handler(msg, process_test21)
        else:
            msg = bot.send_message(chat_id,
"""
Would you mind ___ me that pencil?
1. to pass to
2. pass
3. passing
4. that you should pass
""")
            bot.register_next_step_handler(msg, process_test21)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test21(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I live in Oxford now. I ___ to France for a long time.
1. doesn't been
2. didn't come
3. havent'been
4. don't come
""")        
            bot.register_next_step_handler(msg, process_test22)
        else:
            msg = bot.send_message(chat_id,
"""
I live in Oxford now. I ___ to France for a long time.
1. doesn't been
2. didn't come
3. havent'been
4. don't come
""")        
            bot.register_next_step_handler(msg, process_test22)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test22(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I don't understand. What language ____ ?
1. speak you
2. you speak
3. you are speaking
4. are you speaking
""")    
            bot.register_next_step_handler(msg, process_test23)
        else:
            msg = bot.send_message(chat_id,
"""
I don't understand. What language ____ ?
1. speak you
2. you speak
3. you are speaking
4. are you speaking
""")   
            bot.register_next_step_handler(msg, process_test23)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test23(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "4":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
She came to Britain ____.
1. four days ago
2. at four days
3. before four days
4. since four days
""")    
            bot.register_next_step_handler(msg, process_test24)
        else:
            msg = bot.send_message(chat_id,
"""
She came to Britain ____.
1. four days ago
2. at four days
3. before four days
4. since four days
""") 
            bot.register_next_step_handler(msg, process_test24)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test24(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
My father never ____ out in the evenings.
1. goes
2. go
3. is going
4. going
""")    
            bot.register_next_step_handler(msg, process_test25)
        else:
            msg = bot.send_message(chat_id,
"""
My father never ____ out in the evenings.
1. goes
2. go
3. is going
4. going
""") 
            bot.register_next_step_handler(msg, process_test25)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test25(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
______ Oxford?
1. Since when you live in
2. How much time you are living in
3. How long have you been living in
4. How long time are you living in
""")    
            bot.register_next_step_handler(msg, process_test26)
        else:
            msg = bot.send_message(chat_id,
"""
______ Oxford?
1. Since when you live in
2. How much time you are living in
3. How long have you been living in
4. How long time are you living in
""") 
            bot.register_next_step_handler(msg, process_test26)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test26(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
____car is the red Ford?
1. Whose
2. To whom
3. Who's
4. Of who
""")    
            bot.register_next_step_handler(msg, process_test27)
        else:
            msg = bot.send_message(chat_id,
"""
____car is the red Ford?
1. Whose
2. To whom
3. Who's
4. Of who
""")  
            bot.register_next_step_handler(msg, process_test27)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test27(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I'm sorry. I haven't done my report ___
1. yet
2. already
3. up to the now
4. untill the present
""")    
            bot.register_next_step_handler(msg, process_test28)
        else:
            msg = bot.send_message(chat_id,
"""
I'm sorry. I haven't done my report ___
1. yet
2. already
3. up to the now
4. untill the present
""")  
            bot.register_next_step_handler(msg, process_test28)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test28(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
My friend doesn't speak Enlgish. I don't ___
1. neither
2. also
3. either
4. too
""")    
            bot.register_next_step_handler(msg, process_test29)
        else:
            msg = bot.send_message(chat_id,
"""
My friend doesn't speak Enlgish. I don't ___
1. neither
2. also
3. either
4. too
""")  
            bot.register_next_step_handler(msg, process_test29)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test29(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
That's the house _____.
1. in the which he lives
2. in which he lives in that
3. he lives in
4. he lives in that
""")    
            bot.register_next_step_handler(msg, process_test30)
        else:
            msg = bot.send_message(chat_id,
"""
That's the house _____.
1. in the which he lives
2. in which he lives in that
3. he lives in
4. he lives in that
""")   
            bot.register_next_step_handler(msg, process_test30)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test30(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
If _____.
1. you come to my office, I'd pay you.
2. you should come to my office, I'll pay you.
3. you came to my office, I would to pay you.
4. you come to my office, I'll pay you.
""")    
            bot.register_next_step_handler(msg, process_test31)
        else:
            msg = bot.send_message(chat_id,
"""
If _____.
1. you come to my office, I'd pay you.
2. you should come to my office, I'll pay you.
3. you came to my office, I would to pay you.
4. you come to my office, I'll pay you.
""")    
            bot.register_next_step_handler(msg, process_test31)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test31(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
They asked me how big _____.
1. is your house
2. my house was
3. was my house
4. is my house
""")    
            bot.register_next_step_handler(msg, process_test33)
        else:
            msg = bot.send_message(chat_id,
"""
They asked me how big _____.
1. is your house
2. my house was
3. was my house
4. is my house
""")  
            bot.register_next_step_handler(msg, process_test33)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test33(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
My friend let ____ his bike yesterday.
1. me borrowing
2. to borrow
3. me to borrow
4. me borrow
""")    
            bot.register_next_step_handler(msg, process_test34)
        else:
            msg = bot.send_message(chat_id,
"""
My friend let ____ his bike yesterday.
1. me borrowing
2. to borrow
3. me to borrow
4. me borrow
""")  
            bot.register_next_step_handler(msg, process_test34)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test34(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "4":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
_____, what would you spend it on?
1. When you had a lot of money
2. If you had a lot of money
3. If you have a lot of money
4. If you have had a lot of money
""")    
            bot.register_next_step_handler(msg, process_test35)
        else:
            msg = bot.send_message(chat_id,
"""
_____, what would you spend it on?
1. When you had a lot of money
2. If you had a lot of money
3. If you have a lot of money
4. If you have had a lot of money
""")  
            bot.register_next_step_handler(msg, process_test35)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test35(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I ____ smoking last year, but i didn't.
1. ought to give up
2. ought to have given up
3. ought give up
4. oughted to give up
""")    
            bot.register_next_step_handler(msg, process_test36)
        else:
            msg = bot.send_message(chat_id,
"""
I ____ smoking last year, but i didn't.
1. ought to give up
2. ought to have given up
3. ought give up
4. oughted to give up
""")   
            bot.register_next_step_handler(msg, process_test36)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test36(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I'm ____ the film on Friday.
1. looking forward to see
2. looking forward to seeing
3. look forward seeing
4. looking forward seeing
""")    
            bot.register_next_step_handler(msg, process_test37)
        else:
            msg = bot.send_message(chat_id,
"""
I'm ____ the film on Friday.
1. looking forward to see
2. looking forward to seeing
3. look forward seeing
4. looking forward seeing
""")   
            bot.register_next_step_handler(msg, process_test37)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test37(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I'm not ____ grammar.
1. interested to learn
2. interested in learning grammar.
3. interesting to learning
4. interesting in learning
""")    
            bot.register_next_step_handler(msg, process_test38)
        else:
            msg = bot.send_message(chat_id,
"""
I'm not ____ grammar.
1. interested to learn
2. interested in learning
3. interesting to learning
4. interesting in learning
""")  
            bot.register_next_step_handler(msg, process_test38)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test38(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
The film i watched was very nice. It's ______.
1. worth to see
2. worth seeing
3. worthwhile to see
4. worthwhile see
""")    
            bot.register_next_step_handler(msg, process_test39)
        else:
            msg = bot.send_message(chat_id,
"""
The film i watched was very nice. It's ______.
1. worth to see
2. worth seeing
3. worthwhile to see
4. worthwhile see
""")  
            bot.register_next_step_handler(msg, process_test39)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test39(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I have difficulty ___ English.
1. to write
2. writing
3. about writing
4. to writing
""")    
            bot.register_next_step_handler(msg, process_test40)
        else:
            msg = bot.send_message(chat_id,
"""
It is difficult for me ____ in English.
1. to write
2. writing
3. about writing
4. to writing
""")   
            bot.register_next_step_handler(msg, process_test40)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test40(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
When i lived in France, i _____ lots of wine.
1. was use to drinking
2. used to drink
3. used to drinking
4. was used to drink
""")    
            bot.register_next_step_handler(msg, process_test41)
        else:
            msg = bot.send_message(chat_id,
"""
When i lived in France, i _____ lots of wine.
1. was use to drinking
2. used to drink
3. used to drinking
4. was used to drink
""")    
            bot.register_next_step_handler(msg, process_test41)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test41(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I wish i ______ German.
1. i could speak
2. i would speak
3. i was able to speak
4. i would be able to speak
""")    
            bot.register_next_step_handler(msg, process_test42)
        else:
            msg = bot.send_message(chat_id,
"""
I wish i ______ German.
1. i could speak
2. i would speak
3. i was able to speak
4. i would be able to speak
""")     
            bot.register_next_step_handler(msg, process_test42)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test42(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
What dill you do when ____ studying?
1. you're finishing
2. you'll have finished 
3. you've finished
4. you're going to finish
""")    
            bot.register_next_step_handler(msg, process_test43)
        else:
            msg = bot.send_message(chat_id,
"""
What will you do when ____ studying?
1. you're finishing
2. you'll have finished 
3. you've finished
4. you're going to finish
""")     
            bot.register_next_step_handler(msg, process_test43)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test43(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
The Chancellor ____ the new wing yesterday, but it still isn't finished.
1. had to open
2. has to have opened
3. was to have opened
4. had to have opened
""")    
            bot.register_next_step_handler(msg, process_test44)
        else:
            msg = bot.send_message(chat_id,
"""
The Chancellor ____ the new wing yesterday, but it still isn't finished.
1. had to open
2. has to have opened
3. was to have opened
4. had to have opened
""")    
            bot.register_next_step_handler(msg, process_test44)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test44(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I'd rather _____ English than Swedish.
1. you should learn
2. you learnt 
3. that you might learn
4. you learn
""")    
            bot.register_next_step_handler(msg, process_test45)
        else:
            msg = bot.send_message(chat_id,
"""
I'd rather _____ English than Swedish.
1. you should learn
2. you learnt 
3. that you might learn
4. you learn
""")     
            bot.register_next_step_handler(msg, process_test45)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test45(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "4":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
No sooner ____ in through the door than the phone rang.
1. I had walked
2. was i walking 
3. had i walked
4. i was walking
""")    
            bot.register_next_step_handler(msg, process_test46)
        else:
            msg = bot.send_message(chat_id,
"""
No sooner ____ in through the door than the phone rang.
1. I had walked
2. was i walking 
3. had i walked
4. i was walking
""")     
            bot.register_next_step_handler(msg, process_test46)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test46(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
We're having party at ______
1. the house of Deborah
2. Deborah's
3. the Deborah's house
4. house of Deborah
""")        
            bot.register_next_step_handler(msg, process_test47)
        else:
            msg = bot.send_message(chat_id,
"""
We're having party at ______
1. the house of Deborah
2. Deborah's
3. the Deborah's house
4. house of Deborah
""")     
            bot.register_next_step_handler(msg, process_test47)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test47(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
If he hadn't known the boss, he_____ the job
1. wouldn't get
2. hadn't got
3. wouldn't have got
4. wouldnt' had got
""")    
            bot.register_next_step_handler(msg, process_test48)
        else:
            msg = bot.send_message(chat_id,
"""
If he hadn't known the boss, he_____ the job
1. wouldn't get
2. hadn't got
3. wouldn't have got
4. wouldnt' had got
""")    
            bot.register_next_step_handler(msg, process_test48)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test48(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "4":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
I'd sooner ____ a car than a motorbike.
1. him to buy
2. that he buys
3. he bought
4. he should buy
""")        
            bot.register_next_step_handler(msg, process_test49)
        else:
            msg = bot.send_message(chat_id,
"""
I'd sooner ____ a car than a motorbike.
1. him to buy
2. that he buys
3. he bought
4. he should buy
""")     
            bot.register_next_step_handler(msg, process_test49)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test49(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            print("MISTAKE HERE")
            msg = bot.send_message(chat_id,
"""
I need to go to ___ toilet.
1. the
2. -
3. a
4. some
""")    
            bot.register_next_step_handler(msg, process_test50)
        else:
            msg = bot.send_message(chat_id,
"""
I need to go to ___ toilet.
1. the
2. -
3. a
4. some
""")        
            bot.register_next_step_handler(msg, process_test50)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test50(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "1":
            count_correct_answers.add_point(1)
            print("MISTAKE HERE")
            msg = bot.send_message(chat_id,
"""
It's time ____ some work.
1. for to do
2. she would do
3. she did
4. she were to do
""")        
            bot.register_next_step_handler(msg, process_test51)
        else:
            msg = bot.send_message(chat_id,
"""
It's time ____ some work.
1. for to do
2. she would do
3. she did
4. she were to do
""")    
            bot.register_next_step_handler(msg, process_test51)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test51(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
It's now 10 o'clock and the train ___ arrive at 9.15.
1. had to 
2. must
3. was due to
4. is going to
""")        
            bot.register_next_step_handler(msg, process_test52)
        else:
            msg = bot.send_message(chat_id,
"""
It's now 10 o'clock and the train ___ arrive at 9.15.
1. had to 
2. must
3. was due to
4. is going to
""")     
            bot.register_next_step_handler(msg, process_test52)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")


def process_test52(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "3":
            count_correct_answers.add_point(1)
            msg = bot.send_message(chat_id,
"""
We regret ____ that the course has been cancelled.
1. to tell
2. telling
3. to have said
4. to say
""")    
            bot.register_next_step_handler(msg, show_test_result)
        else:
            msg = bot.send_message(chat_id,
"""
We regret ____ that the course has been cancelled.
1. to tell
2. telling
3. to have said
4. to say
""")     
            bot.register_next_step_handler(msg, show_test_result)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")

def show_test_result(message):
    try:
        chat_id = message.from_user.id
        answer = message.text
        if answer == "2":
            count_correct_answers.add_point(1)
            bot.send_message(chat_id, count_correct_answers.show_total)
        else:
            bot.send_message(chat_id,count_correct_answers.show_total)
            # bot.register_next_step_handler(msg, main_menu)
    except Exception:
        bot.send_message(chat_id, "Oooops, smth went wrong..")