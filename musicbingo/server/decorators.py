from functools import wraps

from flask import request, redirect, make_response
from flask import session, url_for, jsonify
from flask_login import current_user # type: ignore

from musicbingo import models

def db_session(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        with models.db.session_scope() as db_session:
            return func(*args, db_session=db_session, **kwargs)
    return decorated_function

def get_user(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        db_session = kwargs['db_session']
        try:
            user = models.User.get(session=db_session, username=session['username'])
        except KeyError:
            print('username missing from session')
            user = None
        if user is None:
            if '/api/' in request.url:
                response = jsonify(dict(error='Not logged in'))
                response.status_code = 401
                return response
            return redirect(url_for('login'))
        set_current_user(user)
        rv = func(*args, user=user, **kwargs)
        set_current_user(None)
        return rv
    return decorated_function

def get_game(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        db_session = kwargs['db_session']
        user = kwargs['user']
        game = models.Game.get(session=db_session, pk=kwargs['game_pk'])
        if game is None:
            if '/api/' in request.url:
                response = jsonify(dict(error='Unknown game'))
                response.status_code = 404
                return response
            return redirect(url_for('index'))
        return func(*args, game=game, **kwargs)
    return decorated_function

def get_ticket(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        db_session = kwargs['db_session']
        user = kwargs['user']
        game = kwargs['game']
        ticket_pk = kwargs['ticket_pk']
        ticket = models.BingoTicket.get(session=db_session, game_pk=game.pk, pk=ticket_pk)
        if ticket is None:
            if '/api/' in request.url:
                response = jsonify(dict(error='Unknown ticket'))
                response.status_code = 404
                return response
            return redirect(url_for('game', game_pk=game_pk))
        if ticket.user and ticket.user != user:
            if '/api/' in request.url:
                response = jsonify(dict(error='Not authorised'))
                response.status_code = 401
                return response
            return redirect(url_for('game', game_pk=game_pk))
        return func(*args, ticket=ticket, **kwargs)
    return decorated_function
