from app.models import User, TbotChatId
from app import db
from app.users.routes import find_user_by_access_link


class ProcessWelcome:
    """Save user chat > username to db."""
    # get the hash code from the link on the website where /start=user's hashcode
    # generated from his username
    @staticmethod
    def extract_unique_code(text: str) -> str:
        return text.split()[1] if len(text.split()) > 1 else None

    @staticmethod
    def check_if_unique_code_exists(unique_code: str) -> bool:
        code = User.query.filter_by(access_link=unique_code).first()
        if code:
            return True
        return False

    # does a query to the db, retrieving the associated username
    @staticmethod
    def get_username_from_db(unique_code: str) -> str:
        username = find_user_by_access_link(unique_code)
        if username:
            return username.name if ProcessWelcome.check_if_unique_code_exists(unique_code) else None

    # save the chat_id>username to the db
    @staticmethod
    def save_chat_id(chat_id: int, unique_code: str):
        get_username = ProcessWelcome.get_username_from_db(unique_code)
        if get_username:
            user = User.query.filter_by(name=get_username).first()
            chat = TbotChatId(user_chat_id=chat_id)
            db.session.add(chat)
            user.user_chat = chat
            db.session.commit()
