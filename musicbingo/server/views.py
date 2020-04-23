import datetime
from functools import wraps
import os
from pathlib import Path
import tempfile
from typing import Dict, Optional

from flask import Flask, request, render_template, redirect, make_response
from flask import flash, session, url_for, send_from_directory, jsonify
from flask import current_app
from flask.views import MethodView
from flask_cors import cross_origin
from flask_login import confirm_login, current_user, login_required, login_user, logout_user
import jinja2
from pony.orm import count, db_session, flush, select, set_current_user # type: ignore

from musicbingo import models, utils
from musicbingo.docgen.factory import DocumentFactory
from musicbingo.generator import BingoTicket, GameGenerator
from musicbingo.options import Options
from musicbingo.mp3 import MP3Factory
from musicbingo.progress import Progress
from musicbingo.track import Track

from .options import options

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

class NavigationSection:
    def __init__(self, item: str = '', link: str = ''):
        self.item = item
        self.link = link

def nav_sections(section: str, game: Optional[models.Game] = None) -> Dict[str, NavigationSection]:
    sections = {
        'home': NavigationSection(),
        'game': NavigationSection(),
        'play': NavigationSection(),
        'user': NavigationSection(),
    }
    sections[section].item = 'active'
    if game is None:
        sections['game'].link = 'disabled'
        sections['play'].link = 'disabled'
    return sections


class LoginView(MethodView):
    decorators = [db_session]

    def post(self):
        session['username'] = request.form['username']
        password = request.form['password']
        user = models.User.get(username=session['username'])
        if user is None:
            flash('Unknown username or wrong password')
            return redirect(url_for('login'))
        if user.check_password(password):
            user.last_login = datetime.datetime.now()
            login_user(user)
            return redirect(url_for('index'))
        flash('Unknown username or wrong password')
        return redirect(url_for('login'))

    def get(self):
        context = {
            'title': 'Log into Musical Bingo',
            'nav' : nav_sections('user'),
        }
        return render_template('login.html', **context)


class LogoutView(MethodView):
    decorators = [login_required, db_session]

    def get(self):
        logout_user()
        session.pop('username', None)
        flash('Logged out')
        return redirect(url_for('index'))

class RegisterView(MethodView):
    decorators = [login_required, db_session,]

    def post(self):
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        user = models.User.get(username=username)
        if user is not None:
            flash(f'Username {username} is already taken, choose another one')
            return redirect(url_for('register'))
        user = models.User.get(email=email)
        if user is not None:
            flash(f'Email {email} is already registered, please log in')
            return redirect(url_for('login'))
        user = models.User(username=username,
                           password=models.User.hash_password(password),
                           email=email,
                           last_login=datetime.datetime.now())
        flush()
        login_user(user)
        flash('Successfully registered')
        session['username'] = username
        return redirect(url_for('index'))

    def get(self):
        context = {
            'title': 'Register with Musical Bingo',
            'nav' : nav_sections('user'),
        }
        return render_template('register.html', **context)


class ServeStaticFileView(MethodView):
    def get(self, folder, path):
        basedir = os.path.join(current_app.config['STATIC_FOLDER'], "..", folder)
        return send_from_directory(basedir, path)

class SpaIndexView(MethodView):
    def get(self, path=None):
        return render_template('index.html')

class IndexView(MethodView):
    decorators = [get_user, db_session]

    def get(self, user):
        end = datetime.datetime.now() + datetime.timedelta(days=7)
        games = select(
            game for game in models.Game if game.end >= datetime.datetime.now() and
            game.start <= end
        ).order_by(models.Game.start)
        game_round = 1
        start = None
        for game in games:
            if game.start.date() != start:
                game_round = 1
                start = game.start.date()
            else:
                game_round += 1
            game.game_round = game_round
            game.user_count = count(
                t for t in models.BingoTicket if t.user==user and t.game==game)
        context = {
            'title': 'Musical Bingo',
            'user': user,
            'games': games,
            'nav' : nav_sections('home'),
        }
        return render_template('index.html', **context)


class GameView(MethodView):
    decorators = [get_game, get_user, login_required, db_session]

    def get(self, game_pk, user, game):
        tickets: List[Dict[str, Any]] = []
        selected: int = 0
        for ticket in game.bingo_tickets.order_by(models.BingoTicket.number):
            tck = ticket.to_dict()
            if not ticket.user:
                tck['status'] = 'available'
            elif ticket.user == user:
                tck['status'] = 'mine'
                selected += 1
            else:
                tck['status'] = 'taken'
            tickets.append(tck)
        if selected == options.max_tickets_per_user and user.is_admin:
            for index, ticket in enumerate(tickets):
                if ticket['status'] == 'available':
                    tickets[index]['status'] = 'disabled'
        max_tickets = options.max_tickets_per_user
        if user.is_admin:
            max_tickets = len(tickets)
        context = {
            'game': game,
            'selected': selected,
            'max_tickets': max_tickets,
            'nav' : nav_sections('game', game),
            'tickets': tickets,
            'title': f'Musical Bingo: {game.id} - {game.title}',
            'user': user,
        }
        return render_template('game.html', **context)


class ChooseTicketView(MethodView):
    decorators = [get_ticket, get_game, get_user, login_required,
                  db_session]

    def get(self, game_pk, ticket_pk, user, game, ticket):
        ticket.user = user
        return redirect(url_for('game', game_pk=game_pk))

#login_required,
class DownloadTicketView(MethodView):
    decorators = [get_ticket, get_game, get_user, 
                  db_session]

    def get(self, game_pk, ticket_pk, user, game, ticket):
        card = BingoTicket(options, fingerprint=ticket.fingerprint,
                           number=ticket.number)
        for track in ticket.tracks_in_order():
            args = track.to_dict(exclude=['pk', 'classtype', 'game', 'number'])
            args['prime'] = track.prime
            card.tracks.append(Track(parent=None, ref_id=track.pk, **args))

        with tempfile.TemporaryDirectory() as tmpdirname:
            filename = self.create_pdf(game, card, Path(tmpdirname))
            with filename.open('rb') as src:
                data = src.read()
        headers = {
            'Content-Disposition': f'attachment; filename="{filename.name}"',
            'Content-Type': 'application/pdf',
            'Content-Length': str(len(data)),
        }
        return make_response((data, 200, headers))

    def create_pdf(self, game: models.Game, ticket: BingoTicket,
                   tmpdirname: Path) -> Path:
        assert len(ticket.tracks) == (options.rows * options.columns)
        filename = tmpdirname / f'Game {game.id} ticket {ticket.number}.pdf'
        mp3editor = MP3Factory.create_editor(options.mp3_engine)
        pdf = DocumentFactory.create_generator('pdf')
        opts = Options(**options.to_dict())
        opts.checkbox = True
        opts.title = game.title
        opts.game_id = game.id
        gen = GameGenerator(opts, mp3editor, pdf, Progress())
        gen.render_bingo_ticket(str(filename), ticket)
        return filename


class TicketsView(MethodView):
    decorators = [get_game, get_user, login_required,
                  db_session]

    def get(self, game_pk, user, game):
        db_tickets = select(t for t in models.BingoTicket if t.game==game and t.user==user)
        if len(db_tickets) == 0:
            return redirect(url_for('game', game_pk=game_pk))
        tickets = []
        for ticket in db_tickets:
            btk = BingoTicket(options, fingerprint=int(ticket.fingerprint))
            rows: List[List[Track]] = []
            col: List[Track] = []
            for track in ticket.tracks:
                trk = track.to_dict()
                trk['background'] = btk.box_colour_style(len(col), len(rows))
                trk['row'] = len(rows)
                trk['column'] = len(col)
                col.append(trk)
                if len(col) == 5:
                    rows.append(col)
                    col = []
            if col:
                rows.append(col)
            args = ticket.to_dict()
            args['rows'] = rows
            tickets.append(args)
        context = {
            'title': game.title,
            'user': user,
            'game': game,
            'nav' : nav_sections('play', game),
            'tickets': tickets,
        }
        return render_template('view_tickets.html', **context)

def jsonify_no_content(status):
    response = make_response('', status)
    response.mimetype = current_app.config['JSONIFY_MIMETYPE']
    return response

class UserApi(MethodView):
    decorators = [db_session]

    def post(self):
        username = request.json['username']
        password = request.json['password']
        user = models.User.get(username=username)
        if user is None:
            response = jsonify(dict(error='Unknown username or wrong password'))
            response.status_code = 401
            return response
        if user.check_password(password):
            user.last_login = datetime.datetime.now()
            login_user(user)
            result = self.user_info(user)
            session.clear()
            session['username'] = username
            session.permanent = True
            return jsonify(result)
        response = jsonify(dict(error='Unknown username or wrong password'))
        response.status_code = 401
        return response

    def put(self):
        email = request.json['email']
        password = request.json['password']
        username = request.json['username']
        user = models.User.get(username=username)
        if user is not None:
            return jsonify({
                'error': f'Username {username} is already taken, choose another one',
                'success': False,
                'user': {
                    'username': username,
                    'email': email,
                }
            })
        user = models.User.get(email=email)
        if user is not None:
            return jsonify({
                'error': f'Email {email} is already registered, please log in',
                'success': False,
                'user': {
                    'username': username,
                    'email': email,
                }})
        user = models.User(username=username,
                           password=models.User.hash_password(password),
                           email=email,
                           groups_mask=models.Group.users.value,
                           last_login=datetime.datetime.now())
        flush()
        login_user(user)
        session.clear()
        session['username'] = username
        session.permanent = True
        return jsonify({
                'message': 'Successfully registered',
                'success': True,
                'user': self.user_info(user),
            })

    def get(self):
        try:
            user = models.User.get(username=session['username'])
        except KeyError:
            user = None
        if user is None:
            response=jsonify(dict(error='Login required'))
            response.status_code = 401
            return response
        #if not current_user.is_authenticated:
        #    response=jsonify(dict(error='Login required'))
        #    response.status_code = 401
        #    return response
        confirm_login()
        return jsonify(self.user_info(user))

    def user_info(self, user):
        rv = user.to_dict(exclude=["password", "groups_mask"])
        rv['groups'] = [g.name for g in user.groups]
        rv['options'] = {
            'colourScheme': options.colour_scheme,
            'maxTickets': options.max_tickets_per_user,
            'rows': options.rows,
            'columns': options.columns,
        }
        if user.is_admin:
            rv['users'] = {}
            for u in select(u for u in models.User if u.pk != user.pk):
                rv['users'][u.pk] = u.to_dict(only=['username', 'email', 'last_login'])
                rv['users'][u.pk]['groups'] = [g.name for g in u.groups]
        return rv

class CheckUserApi(MethodView):
    decorators = [db_session]

    def post(self):
        found = False
        try:
            username = request.json
            user = models.User.get(username=username)
            found = user is not None
        except KeyError:
            pass
        return jsonify(dict(username=username, found=found))

class LogoutUserApi(MethodView):
    decorators = [db_session]

    def post(self):
        logout_user()
        session.pop('username', None)
        return jsonify('Logged out')


class ListGamesApi(MethodView):
    decorators = [get_user, db_session]

    def get(self, user):
        today = datetime.datetime.now().replace(hour=0, minute=0)
        end = datetime.datetime.now() + datetime.timedelta(days=7)
        if user.is_admin:
            games = select(
                game for game in models.Game if game.end >= datetime.datetime.now() and
                game.start <= end
            ).order_by(models.Game.start)
        else:
            games = select(
                game for game in models.Game if game.end >= datetime.datetime.now() and
                game.start <= end and game.start >= today
            ).order_by(models.Game.start)
        game_round = 1
        start = None
        result = []
        for game in games:
            if game.start.date() != start:
                game_round = 1
                start = game.start.date()
            else:
                game_round += 1
            js_game = game.to_dict()
            js_game['gameRound'] = game_round
            js_game['userCount'] = count(
                t for t in models.BingoTicket if t.user==user and t.game==game)
            result.append(js_game)
        return jsonify(result)

class GameDetailApi(MethodView):
    decorators = [get_game, get_user, db_session]

    def get(self, user, game, game_pk):
        data = game.to_dict()
        data['tracks'] = []
        for track in game.tracks.order_by(models.Track.number):
            trk = track.to_dict(only=['pk', 'album', 'artist', 'start_time', 'number', 'title', 'duration'])
            data['tracks'].append(trk)
        return jsonify(data)


class TicketsApi(MethodView):
    decorators = [get_game, get_user, db_session]

    def get(self, game_pk, user, game, ticket_pk=None):
        if ticket_pk is not None:
            return self.get_ticket_detail(user, game, ticket_pk)
        return self.get_ticket_list(user, game)

    def get_ticket_list(self, user, game):
        tickets: List[Dict[str, Any]] = []
        selected: int = 0
        if user.is_admin:
            game_tickets = game.bingo_tickets.order_by(models.BingoTicket.number)
        else:
            game_tickets = game.bingo_tickets
        for ticket in game_tickets:
            tck = ticket.to_dict()
            if ticket.user is not None:
                tck['user'] = ticket.user.pk
            tickets.append(tck)
        return jsonify(tickets)

    def get_ticket_detail(self, user, game, ticket_pk):
        ticket = models.BingoTicket.get(game=game, pk=ticket_pk)
        if ticket is None:
            response = jsonify({'error': 'Not found'})
            response.status_code = 404
            return response
        if ticket.user != user:
            response = jsonify({'error': 'Not authorised'})
            response.status_code = 401
            return response
        btk = BingoTicket(options, fingerprint=int(ticket.fingerprint))
        rows: List[List[Track]] = []
        col: List[Track] = []
        for idx, track in enumerate(ticket.tracks_in_order()):
            trk = track.to_dict(only=['artist', 'title', 'album'])
            trk['background'] = btk.box_colour_style(len(col), len(rows)).css()
            trk['row'] = len(rows)
            trk['column'] = len(col)
            trk['checked'] = (ticket.checked & (1<<idx)) != 0
            col.append(trk)
            if len(col) == options.columns:
                rows.append(col)
                col = []
        if col:
            rows.append(col)
        card = ticket.to_dict(exclude=['checked', 'order', 'fingerprint'])
        card['rows'] = rows
        return jsonify(card)

    def put(self, game_pk, user, game, ticket_pk=None):
        """
        claim a ticket for this user
        """
        ticket = None
        if ticket_pk is not None:
            ticket = models.BingoTicket.get(game=game, pk=ticket_pk)
        if ticket is None:
            return jsonify_no_content(404)
        if not ticket.user:
            ticket.user = user
            return jsonify_no_content(201)
        if ticket.user != user:
            # ticket already taken
            return jsonify_no_content(406)
        return jsonify_no_content(200)

    def delete(self, game_pk, user, game, ticket_pk=None):
        """
        release a ticket for this user
        """
        ticket = None
        if ticket_pk is not None:
            ticket = models.BingoTicket.get(game=game, pk=ticket_pk)
        if ticket is None:
            return jsonify_no_content(404)
        if not ticket.user:
            return jsonify_no_content(204)
        if ticket.user != user and not user.is_admin:
            return jsonify_no_content(401)
        ticket.user = None
        return jsonify_no_content(204)

class CheckCellApi(MethodView):
    decorators = [get_ticket, get_game, get_user, db_session]
 
    def put(self, user, game, ticket, number, **kwargs):
        """
        set the check mark on a ticket
        """
        if number < 0 or number >= (options.columns * options.rows):
            return jsonify_no_content(404)
        ticket.checked |= (1 << number)
        return jsonify_no_content(200)

    def delete(self, user, game, ticket, number, **kwargs):
        """
        clear the check mark on a ticket
        """
        if number < 0 or number >= (options.columns * options.rows):
            return jsonify_no_content(404)
        ticket.checked &= ~(1 << number)
        return jsonify_no_content(200)


