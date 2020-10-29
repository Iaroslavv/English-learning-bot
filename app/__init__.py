from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config.config")
app.static_folder = "static"
app.template_folder = "templates"

from app import routes
