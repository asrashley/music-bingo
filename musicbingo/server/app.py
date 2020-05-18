import atexit
import logging
import os
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from flask import Flask  # type: ignore
from flask_jwt_extended import JWTManager  # type: ignore

from musicbingo import models
from musicbingo.options import Options

from .decorators import db_session
from .routes import add_routes


def create_app(config: str = '', options: Optional[Options] = None) -> Flask:

    def prune_database():
        with models.db.session_scope() as session:
            models.Token.prune_database(session)

    def bind_database():
        assert options.database is not None
        models.db.DatabaseConnection.bind(options.database)
        sched.add_job(prune_database, 'interval', hours=12)

    if options is None:
        options = Options()
        options.load_ini_file()
    if not config:
        config = 'musicbingo.server.config'
    sched = BackgroundScheduler(daemon=True)
    atexit.register(lambda: sched.shutdown())
    sched.start()
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.update(DEBUG=options.debug,
                      SECRET_KEY=options.get_secret_key(),
                      SCHED=sched,
                      GAME_OPTIONS=options)
    jwt = JWTManager(app)
    add_routes(app)
    app.before_first_request(bind_database)

    @jwt.user_loader_callback_loader
    def user_loader_callback(identity):
        return models.db.User.get(db_session, username=identity)

    @jwt.token_in_blacklist_loader
    def check_if_token_revoked(decoded_token):
        return models.Token.is_revoked(decoded_token, db_session)

    return app
