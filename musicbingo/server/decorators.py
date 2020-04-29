from functools import wraps

from flask import Flask, request, render_template, redirect, make_response
from flask import flash, session, url_for, send_from_directory, jsonify
from flask import current_app
from pony.orm import count, db_session, flush, select, set_current_user # type: ignore

from musicbingo import models


def get_user(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            user = models.User.get(username=session['username'])
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
        user = kwargs['user']
        game = models.Game[kwargs['game_pk']]
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
        user = kwargs['user']
        game = kwargs['game']
        ticket_pk = kwargs['ticket_pk']
        ticket = models.BingoTicket.get(game=game, pk=ticket_pk)
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

