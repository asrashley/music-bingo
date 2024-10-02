"""
Factory for creating Flask app
"""

from pathlib import Path
from typing import Optional, Union, cast

from flask import Flask  # type: ignore
from flask_apscheduler import APScheduler  # type: ignore
from flask_jwt_extended import JWTManager  # type: ignore

from musicbingo import models
from musicbingo.options import Options

from .decorators import db_session
from .routes import add_routes


def create_app(
    config: Union[object, str] = "",
    options: Optional[Options] = None,
    static_folder: Optional[Path] = None,
    template_folder: Optional[Path] = None,
) -> Flask:
    """
    Factory function for creating Flask app
    """
    if options is None:
        options = Options()
        options.load_ini_file()
    if not config:
        config = "musicbingo.server.config.AppConfig"
    srcdir = Path(__file__).parent.resolve()
    basedir = srcdir.parent.parent
    if static_folder is None:
        static_folder = basedir / "client" / "build" / "static"
    if template_folder is None:
        template_folder = basedir / "musicbingo" / "server" / "templates"
        if not template_folder.exists():
            template_folder = srcdir / "templates"

    scheduler = APScheduler()

    @scheduler.task("interval", id="prune_database", hours=3)
    def prune_database():
        with models.db.session_scope() as session:
            models.Token.prune_database(session)

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
    scheduler.init_app(app)
    scheduler.start()
    jwt = JWTManager(app)
    add_routes(app)

    @app.before_request
    def before_first_request() -> None:
        # The following line will remove this handler, making it
        # only run on the first request
        app.before_request_funcs[None].remove(before_first_request)
        assert options is not None
        assert options.database is not None
        models.db.DatabaseConnection.bind(
            options.database,
            debug=options.debug,
            create_superuser=options.create_superuser,
        )

    # pylint: disable=unused-variable
    @jwt.user_lookup_loader
    def user_loader_callback(_jwt_header, jwt_payload):
        identity = jwt_payload['sub']
        return models.db.User.get(db_session, username=identity)

    # pylint: disable=unused-variable
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(_jwt_header, jwt_payload: dict):
        return models.Token.is_revoked(jwt_payload, cast(models.DatabaseSession, db_session))

    return app
