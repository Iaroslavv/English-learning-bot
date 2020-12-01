from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_elasticsearch import FlaskElasticsearch


app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.config")
es = FlaskElasticsearch(app)
db = SQLAlchemy(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
db.init_app(app)
migrate = Migrate(app, db)
app.static_folder = "static"
app.template_folder = "templates"

from app import models
from app.tests import test_users
from app.users.routes import users
from app.handlers.error_handlers import errors
from app.telegram_bot.tele_bot import web
app.register_blueprint(users)
app.register_blueprint(web)
app.register_blueprint(errors)
