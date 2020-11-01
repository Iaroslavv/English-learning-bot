from app import db, login_manager
from flask_login import UserMixin


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
    words = db.relationship("Words", backref="author", lazy=True)
    telegram_info = db.Column(db.String(30), nullable=False, default="@Yourtelegram")

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"


class Words(db.Model):
    """User's words db model."""

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
  
    def __repr__(self):
        return f"Words('{self.word}')"


# probably should add one more table to store the example exersises