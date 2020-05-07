import datetime
import json

from flask import Flask, request, render_template, redirect, make_response # type: ignore
from flask import flash, session, url_for, send_from_directory # type: ignore
from flask import current_app # type: ignore
from flask_login import confirm_login, current_user, login_required # type: ignore
from flask_login import login_user, logout_user # type: ignore
from pony.orm import count, db_session, flush, select, set_current_user # type: ignore

from flask.views import MethodView

from musicbingo import models, utils
from musicbingo.bingoticket import BingoTicket
from .decorators import get_user, get_game, get_ticket
from .options import options

def jsonify(data, status = None):
    if status is None:
        status = 200
    response = make_response(json.dumps(utils.flatten(data)), status)
    response.mimetype = current_app.config['JSONIFY_MIMETYPE']
    return response

def jsonify_no_content(status):
    response = make_response('', status)
    response.mimetype = current_app.config['JSONIFY_MIMETYPE']
    return response

class UserApi(MethodView):
    decorators = [db_session]

    def post(self):
        """
        Attempt to log in.
        'username' can be either a username or an email address
        """
        username = request.json['username']
        password = request.json['password']
        user = models.User.get(username=username)
        if user is None:
            user = models.User.get(email=username)
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
        """
        Register a new user
        """
        try:
            email = request.json['email']
            password = request.json['password']
            username = request.json['username']
        except KeyError as err:
            response = jsonify({err: "Is a required field"})
            response.status_code = 400
            return response
        if models.User.exists(username=username):
            return jsonify({
                'error': {
                    "username": f'Username {username} is already taken, choose another one',
                },
                'success': False,
                'user': {
                    'username': username,
                    'email': email,
                }
            })
        if models.User.exists(email=email):
            return jsonify({
                'error': {
                    "email": f'Email address "{email}" has already been registered',
                },
                'success': False,
                'user': {
                    'username': username,
                    'email': email,
                }
            })
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
        response = {
            "username": False,
            "email": False
        }
        username = request.json.get('username', None)
        email = request.json.get('email', None)
        user = None
        if not username and not email:
            return jsonify_no_content(400)
        if username:
            response['username'] = models.User.exists(username=username)
        if email:
            response['email'] = models.User.exists(email=email)
        return jsonify(response)

class LogoutUserApi(MethodView):
    decorators = [db_session]

    def post(self):
        logout_user()
        session.pop('username', None)
        return jsonify('Logged out')

class ResetPasswordUserApi(MethodView):
    decorators = [db_session]

    def post(self):
        try:
            if models.User.exists(username=session['username']):
                # don't allow reset if logged in
                return jsonify_no_content(400)
        except KeyError:
            pass
        email = request.json.get('email', None)
        if not email:
            return jsonify_no_content(400)
        user = models.User.get(email=email)
        if user:
            user.reset_request = True
        # we don't divulge if the user really exists
        response = {
            "email": email,
            "success": True,
        }
        return jsonify(response)

class UserManagmentApi(MethodView):
    decorators = [get_user, db_session]

    def get(self, user):
        """
        Get the list of registered users
        """
        if not user.is_admin:
            jsonify_no_content(401)
        users = []
        for user in models.User.select():
            usr = user.to_dict(exclude=['password', 'groups_mask'])
            usr['groups'] = [g.name for g in user.groups]
            users.append(usr)
        return jsonify(users)

    def post(self, user):
        """
        Modify or delete users
        """
        if not user.is_admin:
            jsonify_no_content(401)
        if not request.json:
            return jsonify_no_content(400)
        result = {
            "errors": [],
            "modified": [],
            "deleted": []
        }
        for idx, item in enumerate(request.json):
            try:
                pk = item['pk']
                deleted = item['deleted']
                username = item['username']
                email = item['email']
            except KeyError as err:
                result["errors"].append(f"{idx}: Missing field {err}")
                continue
            self.modify_user(result, idx, pk, username, email, deleted)
        return jsonify(result)

    @staticmethod
    def modify_user(result, idx, pk, username, email, deleted):
        user = models.User.get(pk=pk)
        if user is None:
            result["errors"].append(f"{idx}: Unknown user {pk}")
            return
        if deleted == True:
            user.delete()
            result['deleted'].append(pk)
            return
        modified = False
        if username != user.username:
            if models.User.exists(username=username):
                result["errors"].append(f"{idx}: Username {username} already present")
            else:
                user.username = username
                modified = True
        if email != user.email:
            if models.User.exists(email=email):
                result["errors"].append(f"{idx}: Email {email} already present")
            else:
                user.email = email
                modified = True
        if modified:
            result['modified'].append(pk)


class ListGamesApi(MethodView):
    decorators = [get_user, db_session]

    def get(self, user):
        """
        Returns a list of all past and upcoming games
        """
        now = datetime.datetime.now()
        today = now.replace(hour=0, minute=0)
        start = today - datetime.timedelta(days=365)
        end = now + datetime.timedelta(days=7)
        if user.is_admin:
            games = models.Game.select().order_by(models.Game.start)
        else:
            games = select(
                game for game in models.Game if game.start <= end and game.start >= start
            ).order_by(models.Game.start)
        start = None
        future = []
        past = []
        for game in games:
            if isinstance(game.start, str):
                print('bad start time', game.id, game.start)
                game.start = utils.parse_date(game.start)
            if isinstance(game.end, str):
                print('bad end time', game.id, game.end)
                game.end = utils.parse_date(game.end)
            js_game = game.to_dict()
            js_game['userCount'] = count(
                t for t in models.BingoTicket if t.user==user and t.game==game)
            if game.start >= today and game.end > now:
                future.append(js_game)
            else:
                past.append(js_game)
        return jsonify(dict(games=future, past=past))

class GameDetailApi(MethodView):
    decorators = [get_game, get_user, db_session]

    def get(self, user, game, game_pk):
        """
        Get the extended detail for a game.
        This detail will include the complete track listing.
        """
        now = datetime.datetime.now()
        if game.end > now and not user.has_permission(models.Group.host):
            # Don't allow a player to cheat and get the track list
            jsonify_no_content(401)
        data = game.to_dict()
        data['tracks'] = []
        for track in game.tracks.order_by(models.Track.number):
            trk = track.song.to_dict(only=['album', 'artist', 'title', 'duration'])
            trk.update(track.to_dict(only=['pk', 'number', 'start_time']))
            trk['song'] = track.song.pk
            data['tracks'].append(trk)
        return jsonify(data)

    def post(self, user, game, game_pk):
        """
        Modify a game
        """
        if not user.is_admin:
            return jsonify_no_content(401)
        if not request.json:
            return jsonify_no_content(400)
        try:
            changes = {
                'start': utils.make_naive_utc(utils.from_isodatetime(request.json['start'])),
                'end': utils.make_naive_utc(utils.from_isodatetime(request.json['end'])),
                'title': request.json['title'],
            }
        except (KeyError, ValueError) as err:
            result = {
                'success': False,
                'error': err
            }
            return jsonify(result, 400)
        if changes['start'] > changes['end']:
            result = {
                'success': False,
                'error': 'Start must be less than end'
            }
        else:
            result = {
                'success': True,
            }
            game.set(**changes)
        result['game']  = game.to_dict()
        return jsonify(result)

    def delete(self, user, game, **kwargs):
        """
        Delete a game
        """
        if not user.is_admin:
            return jsonify_no_content(401)
        game.delete()
        return jsonify_no_content(200)


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
        """
        Get the detailed information for a Bingo Ticket.
        """
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
            trk = track.song.to_dict(only=['artist', 'title', 'album'])
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

class TicketsStatusApi(MethodView):
    decorators = [get_game, get_user, db_session]

    def get(self, game_pk, user, game):
        claimed: Dict[int, Optional[int]] = {}
        for ticket in game.bingo_tickets:
            if ticket.user is not None:
                claimed[ticket.pk] = ticket.user.pk
            else:
                claimed[ticket.pk] = None
        return jsonify(dict(claimed=claimed))

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
