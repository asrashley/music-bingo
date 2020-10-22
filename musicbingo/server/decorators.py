"""
Function decorators used for views and REST APIs.
"""

from functools import wraps
import json

from flask import (  # type: ignore
    make_response,
    current_app, _request_ctx_stack,
)
from werkzeug.local import LocalProxy

from musicbingo import models, utils


def jsonify(data, status=None, indent=None):
    """
    Replacement for Flask jsonify that uses flatten to convert non-json objects
    """
    if status is None:
        status = 200
    response = make_response(json.dumps(data, default=utils.flatten,
                                        indent=indent), status)
    response.mimetype = current_app.config['JSONIFY_MIMETYPE']
    return response


def jsonify_no_content(status):
    """
    Used to return a JSON response with no body
    """
    response = make_response('', status)
    response.mimetype = current_app.config['JSONIFY_MIMETYPE']
    return response


db_session = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'db_session', None))


def uses_database(func):
    """
    Decorator that creates a database session into db_session
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        with models.db.session_scope() as session:
            _request_ctx_stack.top.db_session = session
            return func(*args, **kwargs)
    return decorated_function


current_directory = LocalProxy(lambda: getattr(_request_ctx_stack.top,
                                               'current_directory', None))
def get_directory(func):
    """
    Decorator that finds Directory from database
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        directory = models.Directory.get(db_session, pk=kwargs['dir_pk'])
        if directory is None:
            return jsonify(dict(error='Unknown directory'), 404)
        _request_ctx_stack.top.current_directory = directory
        return func(*args, **kwargs)
    return decorated_function

current_game = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_game', None))

def get_game(func):
    """
    Decorator that finds Game from database
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        game = models.Game.get(db_session, pk=kwargs['game_pk'])
        if game is None:
            return jsonify(dict(error='Unknown game'), 404)
        _request_ctx_stack.top.current_game = game
        return func(*args, **kwargs)
    return decorated_function


current_ticket = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_ticket', None))


def get_ticket(func):
    """
    Decorator that finds Ticket from database
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        ticket_pk = kwargs['ticket_pk']
        ticket = models.BingoTicket.get(session=db_session, game_pk=current_game.pk, pk=ticket_pk)
        if ticket is None:
            return jsonify(dict(error='Unknown ticket'), 404)
        _request_ctx_stack.top.current_ticket = ticket
        return func(*args, **kwargs)
    return decorated_function


current_options = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_options', None))


def get_options(func):
    """
    Decorator that populates current_options with the Options used by ths app
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        _request_ctx_stack.top.current_options = current_app.config['GAME_OPTIONS']
        return func(*args, **kwargs)
    return decorated_function
