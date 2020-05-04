import logging
import os

from flask import Flask # type: ignore
from flask_login import LoginManager # type: ignore

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
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'PERMANENT_SESSION_LIFETIME': 3600 * 24,
    'STATIC_FOLDER': STATIC_FOLDER,
    'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
}

app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
app.config.update(**config)

assert options.database is not None
models.db.DatabaseConnection.bind(options.database)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    print('load user', user_id)
    with models.db.session_scope() as session:
        return models.db.User.get(session, username=user_id)

def run():
    app.run(host='0.0.0.0')

add_routes(app, options)

login_manager.init_app(app)
