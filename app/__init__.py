from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.config")
db = SQLAlchemy(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
db.init_app(app)
migrate = Migrate(app, db)
app.static_folder = "static"
app.template_folder = "templates"

from app import routes, models
