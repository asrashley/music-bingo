import datetime
from functools import wraps
import os
from pathlib import Path
import tempfile
from typing import Dict, Optional

from flask import Flask, request, render_template, redirect
from flask import flash, session, url_for, send_file
from flask.views import MethodView
from flask_login import login_required, login_user, logout_user
import jinja2
from pony.orm import count, db_session, flush, select, set_current_user

from musicbingo import models
from musicbingo.docgen.factory import DocumentFactory
from musicbingo.generator import BingoTicket, GameGenerator
from musicbingo.options import Options
from musicbingo.mp3 import MP3Factory
from musicbingo.progress import Progress
from musicbingo.track import Track

from .app import app, options

def get_user(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = models.User.get(username=session['username'])
        if user is None:
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
            return redirect(url_for('game', game_pk=game_pk))
        if ticket.user and ticket.user != user:
            return redirect(url_for('game', game_pk=game_pk))
        return func(*args, ticket=ticket, **kwargs)
    return decorated_function

class NavigationSection:
    def __init__(self, item: str = '', link: str = ''):
        self.item = item
        self.link = link

def nav_sections(section: str, game: Optional[models.Game] = None) -> Dict[str, str]:
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


#@app.route('/login', methods=['GET', 'POST'])
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


class DownloadTicketView(MethodView):
    decorators = [get_ticket, get_game, get_user, login_required,
                  db_session]

    def get(self, game_pk, ticket_pk, user, game, ticket):
        card = BingoTicket(options, fingerprint=ticket.fingerprint,
                           number=ticket.number)
        for track in ticket.tracks:
            args = track.to_dict(exclude=['pk', 'classtype', 'game'])
            args['prime'] = int(args['prime'])
            card.tracks.append(Track(parent=None, ref_id=track.pk, **args))

        with tempfile.TemporaryDirectory() as tmpdirname:
            filename = self.create_pdf(game, card, Path(tmpdirname))
            return send_file(str(filename), attachment_filename=filename.name,
                             as_attachment=True)

    def create_pdf(self, game: models.Game, ticket: BingoTicket,
                   tmpdirname: Path) -> Path:
        print(len(ticket.tracks), (options.rows * options.columns))
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

app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
app.add_url_rule('/register', view_func=RegisterView.as_view('register'))
app.add_url_rule('/game/<game_pk>', view_func=GameView.as_view('game'))
app.add_url_rule('/game/<game_pk>/add/<ticket_pk>',
                 view_func=ChooseTicketView.as_view('add_ticket'))
app.add_url_rule('/game/<game_pk>/get/<ticket_pk>',
                 view_func=DownloadTicketView.as_view('download_ticket'))
app.add_url_rule('/play/<game_pk>',
                 view_func=TicketsView.as_view('view_tickets'))
app.add_url_rule('/', view_func=IndexView.as_view('index'))
