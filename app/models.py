from app import db


class User(db.Model):
    """User db model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    words = db.relationship("Words", backref="author", lazy=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

 
class Words(db.Model):
    """User's words db model."""

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    def __repr__(self):
        return f"AddWords('{self.word}')"
