"""
Function decorators used for views and REST APIs.
"""

from functools import wraps
from typing import cast

import flask  # type: ignore
from flask import Response, current_app  # type: ignore
from werkzeug.local import LocalProxy  # type: ignore

from musicbingo import models, utils
from musicbingo.options import Options
from musicbingo.models.session import DatabaseSession

def jsonify(data, status=None) -> Response:
    """
    Replacement for Flask jsonify that uses flatten to convert non-json objects
    """
    if status is None:
        status = 200
    if isinstance(data, dict):
        response = flask.json.jsonify(**utils.flatten(data))
    elif isinstance(data, list):
        response = flask.json.jsonify(utils.flatten(data))
    else:
        response = flask.json.jsonify(data)
    response.status = status
    return response


def jsonify_no_content(status) -> Response:
    """
    Used to return a JSON response with no body
    """
    response = flask.json.jsonify('')
    response.status = status
    return response


def uses_database(func):
    """
    Decorator that creates a database session into db_session
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        with models.db.session_scope() as session:
            flask.g.db_session = session
            return func(*args, **kwargs)
    return decorated_function

db_session = cast(DatabaseSession, LocalProxy(lambda: flask.g.db_session))


def get_directory(func):
    """
    Decorator that finds Directory from database
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        directory = models.Directory.get(db_session, pk=kwargs['dir_pk'])
        if directory is None:
            return jsonify({'error': 'Unknown directory'}, 404)
        flask.g.current_directory = directory
        return func(*args, **kwargs)
    return decorated_function

def get_game(func):
    """
    Decorator that finds Game from database
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        game = models.Game.get(db_session, pk=kwargs['game_pk'])
        if game is None:
            return jsonify({'error': 'Unknown game'}, 404)
        flask.g.current_game = game
        return func(*args, **kwargs)
    return decorated_function

def get_ticket(func):
    """
    Decorator that finds Ticket from database
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        ticket_pk = kwargs['ticket_pk']
        ticket = models.BingoTicket.get(
            session=db_session, game_pk=flask.g.current_game.pk,
            pk=ticket_pk)
        if ticket is None:
            return jsonify({'error': 'Unknown ticket'}, 404)
        flask.g.current_ticket = ticket
        return func(*args, **kwargs)
    return decorated_function

def get_options(func):
    """
    Decorator that populates current_options with the Options used by ths app
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        flask.g.current_options = current_app.config['GAME_OPTIONS']
        return func(*args, **kwargs)
    return decorated_function
