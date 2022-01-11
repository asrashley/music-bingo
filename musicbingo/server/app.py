"""
Factory for creating Flask app
"""

import atexit
from pathlib import Path
from typing import Optional, Union

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from flask import Flask  # type: ignore
from flask_jwt_extended import JWTManager  # type: ignore
from pytz import utc  # type: ignore

from musicbingo import models
from musicbingo.options import Options

from .decorators import db_session
from .routes import add_routes


def create_app(config: Union[object, str] = '',
               options: Optional[Options] = None,
               static_folder: Optional[Path] = None,
               template_folder: Optional[Path] = None) -> Flask:
    """
    Factory function for creating Flask app
    """

    def prune_database():
        with models.db.session_scope() as session:
            models.Token.prune_database(session)

    def bind_database():
        assert options.database is not None
        models.db.DatabaseConnection.bind(
            options.database, debug=options.debug,
            create_superuser=options.create_superuser)
        sched.add_job(prune_database, 'interval', hours=6)

    if options is None:
        options = Options()
        options.load_ini_file()
    if not config:
        config = 'musicbingo.server.config.AppConfig'
    sched = BackgroundScheduler(daemon=True, timezone=utc)
    atexit.register(sched.shutdown)
    sched.start()
    srcdir = Path(__file__).parent.resolve()
    basedir = srcdir.parent.parent
    if static_folder is None:
        static_folder = basedir / "client" / "build" / "static"
    if template_folder is None:
        template_folder = basedir / "client" / "build"
        if not template_folder.exists():
            template_folder = srcdir
    app = Flask(__name__, template_folder=str(template_folder), static_folder=str(static_folder))
    if options.debug:
        print('static_folder', str(static_folder))
        print('template_folder', str(template_folder))
    app.config.from_object(config)
    app.config.update(DEBUG=options.debug,
                      SECRET_KEY=options.get_secret_key(),
                      GAME_OPTIONS=options,
                      STATIC_FOLDER=str(static_folder),
                      TEMPLATE_FOLDER=str(template_folder))
    jwt = JWTManager(app)
    add_routes(app)
    app.before_first_request(bind_database)

    # pylint: disable=unused-variable
    @jwt.user_loader_callback_loader
    def user_loader_callback(identity):
        return models.db.User.get(db_session, username=identity)

    # pylint: disable=unused-variable
    @jwt.token_in_blacklist_loader
    def check_if_token_revoked(decoded_token):
        return models.Token.is_revoked(decoded_token, db_session)

    return app
