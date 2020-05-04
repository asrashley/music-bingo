import datetime
import os
from pathlib import Path
import tempfile
from typing import Dict, Optional

from flask import Flask, request, render_template, redirect, make_response # type: ignore
from flask import flash, session, url_for, send_from_directory, jsonify # type: ignore
from flask import current_app # type: ignore
from flask.views import MethodView # type: ignore
from flask_cors import cross_origin # type: ignore
from flask_login import confirm_login, current_user, login_required # type: ignore
from flask_login import login_user, logout_user # type: ignore
import jinja2

from musicbingo import models, utils
from musicbingo.docgen.factory import DocumentFactory
from musicbingo.generator import BingoTicket, GameGenerator
from musicbingo.options import Options
from musicbingo.mp3 import MP3Factory
from musicbingo.progress import Progress
from musicbingo.song import Song
from musicbingo.track import Track

from .options import options
from .decorators import db_session, get_user, get_game, get_ticket

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

    def post(self, db_session):
        session['username'] = request.form['username']
        password = request.form['password']
        user = models.User.get(db_session, username=session['username'])
        if user is None:
            flash('Unknown username or wrong password')
            return redirect(url_for('login'))
        if user.check_password(password):
            user.last_login = datetime.datetime.now()
            login_user(user)
            return redirect(url_for('index'))
        flash('Unknown username or wrong password')
        return redirect(url_for('login'))

    def get(self, db_session):
        context = {
            'title': 'Log into Musical Bingo',
            'nav' : nav_sections('user'),
        }
        return render_template('login.html', **context)


class LogoutView(MethodView):
    decorators = [login_required, db_session]

    def get(self, db_session):
        logout_user()
        session.pop('username', None)
        flash('Logged out')
        return redirect(url_for('index'))

class RegisterView(MethodView):
    decorators = [login_required, db_session,]

    def post(self, db_session):
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        user = models.User.get(db_session, username=username)
        if user is not None:
            flash(f'Username {username} is already taken, choose another one')
            return redirect(url_for('register'))
        user = models.User.get(db_session, email=email)
        if user is not None:
            flash(f'Email {email} is already registered, please log in')
            return redirect(url_for('login'))
        user = models.User(username=username,
                           password=models.User.hash_password(password),
                           email=email,
                           last_login=datetime.datetime.now())
        db_session.add(user)
        login_user(user)
        flash('Successfully registered')
        session['username'] = username
        return redirect(url_for('index'))

    def get(self, db_session):
        context = {
            'title': 'Register with Musical Bingo',
            'nav' : nav_sections('user'),
        }
        return render_template('register.html', **context)


class ServeStaticFileView(MethodView):
    def get(self, path, folder=None):
        basedir = os.path.join(current_app.config['STATIC_FOLDER'], "..")
        if folder is not None:
            basedir = os.path.join(basedir, folder)
        return send_from_directory(basedir, path)

class SpaIndexView(MethodView):
    def get(self, path=None):
        return render_template('index.html')

class IndexView(MethodView):
    decorators = [get_user, db_session]

    def get(self, db_session, user):
        now = datetime.datetime.now()
        today = now.replace(hour=0, minute=0)
        start = today - datetime.timedelta(days=365)
        end = now + datetime.timedelta(days=7)
        if user.is_admin:
            games = models.Game.all(db_session).order_by(models.Game.start)
        else:
            games = db_session.query(models.Game).\
                filter(models.Game.start <= end).\
                filter(models.Game.start >= start).\
                order_by(models.Game.start)
        game_round = 1
        start = None
        for game in games:
            if game.start.date() != start:
                game_round = 1
                start = game.start.date()
            else:
                game_round += 1
            game.game_round = game_round
            game.user_count = db_session.query(
                models.BingoTicket).filter(
                    models.BingoTicket.user==user,
                    models.BingoTicket.game==game).count()
        context = {
            'title': 'Musical Bingo',
            'user': user,
            'games': games,
            'nav' : nav_sections('home'),
        }
        return render_template('index.html', **context)


class GameView(MethodView):
    decorators = [get_game, get_user, login_required, db_session]

    def get(self, game_pk, db_session, user, game):
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

    def get(self, game_pk, ticket_pk, db_session, user, game, ticket):
        if not ticket.user:
            ticket.user = user
        return redirect(url_for('game', game_pk=game_pk))

#login_required,
class DownloadTicketView(MethodView):
    decorators = [get_ticket, get_game, get_user,
                  db_session]

    def get(self, game, ticket, **kwargs):
        if ticket.user != user and not user.is_admin:
            response = make_response('Not authorised', 401)
            return response
        card = BingoTicket(options, fingerprint=ticket.fingerprint,
                           number=ticket.number)
        for track in ticket.tracks_in_order():
            song = Song(parent=None, ref_id=track.pk,
                        **track.song.to_dict(exclude=['pk', 'directory']))
            card.tracks.append(Track(prime=track.prime, song=song,
                                     start_time=track.start_time))

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
        filename = tmpdirname / f'Game {game.id} ticket {ticket.number}.pdf' # type: ignore
        mp3editor = MP3Factory.create_editor(options.mp3_engine)
        pdf = DocumentFactory.create_generator('pdf')
        opts = Options(**options.to_dict())
        opts.checkbox = True
        opts.title = game.title # type: ignore
        opts.game_id = game.id # type: ignore
        gen = GameGenerator(opts, mp3editor, pdf, Progress())
        gen.render_bingo_ticket(str(filename), ticket)
        return filename


class TicketsView(MethodView):
    decorators = [get_game, get_user, login_required,
                  db_session]

    def get(self, game_pk, db_session, user, game):
        db_tickets = db_session.query(models.BingoTicket).filter_by(
                game_pk=game.pk, user_pk=user.pk)
        if db_tickets.count() == 0:
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
