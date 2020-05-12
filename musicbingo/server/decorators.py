from functools import wraps

from flask import request, redirect, make_response
from flask import session, url_for, jsonify
from flask import current_app, _request_ctx_stack
from werkzeug.local import LocalProxy

from musicbingo import models

db_session = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'db_session', None))

def uses_database(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        with models.db.session_scope() as session:
            _request_ctx_stack.top.db_session = session
            return func(*args, **kwargs)
    return decorated_function


#def get_user(func):
#    @wraps(func)
#    def decorated_function(*args, **kwargs):
#        user = None
#        if current_user.is_authenticated:
#            try:
#                user = models.User.get(session=db_session, username=session['username'])
#            except KeyError:
#                print('username missing from session')
#                user = None
#        if user is None:
#            if '/api/' in request.url:
#                response = jsonify(dict(error='Not logged in'))
#                response.status_code = 401
#                return response
#            return redirect(url_for('login'))
#        rv = func(*args, user=user, **kwargs)
#        return rv
#    return decorated_function

current_game = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_game', None))

def get_game(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        game = models.Game.get(db_session, pk=kwargs['game_pk'])
        if game is None:
            response = jsonify(dict(error='Unknown game'))
            response.status_code = 404
            return response
        _request_ctx_stack.top.current_game = game
        return func(*args, **kwargs)
    return decorated_function

def get_ticket(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
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
        if not ticket.user or (
                ticket.user.pk != current_user.pk and
                not current_user.has_permission(models.Group.host)):
            if '/api/' in request.url:
                response = jsonify(dict(error='Not authorised'))
                response.status_code = 401
                return response
            return redirect(url_for('game', game_pk=game_pk))
        return func(*args, ticket=ticket, **kwargs)
    return decorated_function
