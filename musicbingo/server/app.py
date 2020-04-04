from flask import Flask
#from pony.flask import Pony
from flask_login import LoginManager
from pony.orm import db_session

#from .config import config
from musicbingo import models
from musicbingo.options import Options

options = Options()
options.load_ini_file()

config = {
    'DEBUG': options.debug,
    'SECRET_KEY': options.get_secret_key(),
    'PONY': options.database_settings(),
}

app = Flask(__name__)
app.config.update(config)

models.bind(**app.config['PONY'])

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    with db_session:
        return models.db.User.get(username=user_id)

#Pony(app)
