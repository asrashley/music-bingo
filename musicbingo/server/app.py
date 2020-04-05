import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from pony.orm import db_session

#from .config import config
from musicbingo import models

from .options import options
from .routes import add_routes


if options.ui_version == 2:
    STATIC_FOLDER = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "client", "build", "static"))
    TEMPLATE_FOLDER = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "client", "build"))
else:
    STATIC_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static")
    TEMPLATE_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")

config = {
    'DEBUG': options.debug,
    'SECRET_KEY': options.get_secret_key(),
    'PONY': options.database_settings(),
    'SESSION_COOKIE_SECURE': False, # TODO: only set in dev mode
    'SESSION_COOKIE_HTTPONLY': False,
    'PERMANENT_SESSION_LIFETIME': 3600 * 24,
    'STATIC_FOLDER': STATIC_FOLDER,
    'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
}

app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
app.config.update(**config)
cors = CORS(app, resources={r"/api/*": {
    "origins": "http://ripley.home.lan:3000",
    "max_age": 3600,
    "send_wildcard": True,
    "supports_credentials": True,
    }})

models.bind(**app.config['PONY'])

login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.getLogger('flask_cors').level = logging.DEBUG

@login_manager.user_loader
def load_user(user_id):
    with db_session:
        return models.db.User.get(username=user_id)

#Pony(app)

def run():
    app.run(host='0.0.0.0')

add_routes(app, options)