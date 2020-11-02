import os

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
CSRF_ENABLED = True
SECRET_KEY = 'gh3y4hgy48hghidbsla43gb'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'vocab.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "iaroslavmusic@gmail.com"
MAIL_PASSWORD = "yaroslavolga1972"
