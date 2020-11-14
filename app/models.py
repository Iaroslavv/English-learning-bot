from app import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """User db model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    img_file = db.Column(db.String(20), nullable=False, default="static/default.png")
    password = db.Column(db.String(60), nullable=False)
    access_link = db.Column(db.String(70), nullable=False)
    words = db.relationship("NewWords", backref="user", lazy=True)
    user_chat = db.relationship("TbotChatId", uselist=False, lazy=True, backref="user")
    instagram = db.Column(db.String(30), nullable=False, default="Your instagram")
    facebook = db.Column(db.String(30), nullable=False, default="Your facebook")
    twitter = db.Column(db.String(30), nullable=False, default="Your twitter")
    telegram_info = db.Column(db.String(30), nullable=False, default="@Yourtelegram")

    def get_reset_token(self, expires_sec=1800):
        serial = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return serial.dumps({"user_id": self.id}).decode("utf-8")
   
    @staticmethod
    def verify_reset_token(token) -> str:
        serial = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serial.loads(token)["user_id"]
        except Exception:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.user_chat}', '{self.words}')"


class NewWords(db.Model):
    """User's words db model."""

    id = db.Column(db.Integer, primary_key=True)
    user_word = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  
    def __repr__(self):
        return f"Words('{self.user_word}')"


class TbotChatId(db.Model):
    """User's telegram chat id model."""

    id = db.Column(db.Integer, primary_key=True)
    user_chat_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    def __repr__(self):
        return f"TbotChatId('{self.user_chat_id}')"

# probably should add one more table to store the example exersises
