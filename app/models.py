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
    password = db.Column(db.String(60), nullable=False)
    words = db.relationship("Words", backref="author", lazy=True)

    def get_reset_token(self, expires_sec=1800):
        serial = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return serial.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        serial = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serial.loads(token)["user_id"]
        except Exception:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

 
class Words(db.Model):
    """User's words db model."""

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    def __repr__(self):
        return f"AddWords('{self.word}')"

# probably should add one more table to store the example exersises
