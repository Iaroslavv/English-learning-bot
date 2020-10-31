import os

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
# CSRF_ENABLED = True
SECRET_KEY = 'gh3y4hgy48hghidbsla43gb'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'vocab.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
