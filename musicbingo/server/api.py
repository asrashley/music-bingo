# pylint: disable=unused-argument

import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import smtplib
import ssl
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from flask import (
    request, render_template,  # type: ignore
    session, url_for,  # type: ignore
    current_app,
)
from flask.views import MethodView  # type: ignore
from flask_jwt_extended import (  # type: ignore
    jwt_required, jwt_optional, create_access_token,
    get_jwt_identity, current_user, get_raw_jwt,
    jwt_refresh_token_required, create_refresh_token,
    decode_token,
)

from musicbingo import models, utils
from musicbingo.models.modelmixin import JsonObject
from musicbingo.bingoticket import BingoTicket
from .decorators import (
    db_session, uses_database, get_game, current_game, get_ticket,
    current_ticket, jsonify, jsonify_no_content,
    get_options, current_options,
)


class UserApi(MethodView):
    decorators = [get_options, jwt_optional, uses_database]

    def post(self):
        """
        Attempt to log in.
        'username' can be either a username or an email address
        """
        username = request.json['username']
        password = request.json['password']
        rememberme = request.json.get('rememberme', False)
        user = models.User.get(db_session, username=username)
        if user is None:
            user = models.User.get(db_session, email=username)
        if user is None:
            response = jsonify(
                dict(error='Unknown username or wrong password'))
            response.status_code = 401
            return response
        if not user.check_password(password):
            response = jsonify(dict(error='Unknown username or wrong password'))
            response.status_code = 401
            return response
        user.last_login = datetime.datetime.now()
        user.reset_date = None
        user.reset_link = ''
        result = self.user_info(user)
        session.clear()
        result['accessToken'] = create_access_token(identity=user.username)
        expires = None
        if rememberme == True:
            expires = current_app.config['REMEMBER_ME_REFRESH_TOKEN_EXPIRES']
        result['refreshToken'] = create_refresh_token(identity=user.username,
                                                      expires_delta=expires)
        models.Token.add(decode_token(result['refreshToken']),
                         current_app.config['JWT_IDENTITY_CLAIM'],
                         False, db_session)
        return jsonify(result)

    def put(self):
        """
        Register a new user
        """
        try:
            email = request.json['email']
            password = request.json['password']
            username = request.json['username']
        except KeyError as err:
            return jsonify({str(err): "Is a required field"}, 400)
        if models.User.exists(db_session, username=username):
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
        if models.User.exists(db_session, email=email):
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
        db_session.add(user)
        db_session.commit()
        # TODO: put expiry information in a setting
        expires = datetime.timedelta(days=1)
        refresh_token = create_refresh_token(identity=user.username,
                                             expires_delta=expires)
        models.Token.add(decode_token(refresh_token),
                         current_app.config['JWT_IDENTITY_CLAIM'],
                         False, db_session)
        return jsonify({
            'message': 'Successfully registered',
            'success': True,
            'user': self.user_info(user),
            'accessToken': create_access_token(identity=user.username),
            'refreshToken': refresh_token,
        })

    def get(self):
        """
        If user is logged in, return the information about the user
        """
        username = get_jwt_identity()
        if not username:
            return jsonify(dict(error='Login required'), 401)
        user = models.User.get(db_session, username=username)
        if user is None:
            # TODO: revoke access token
            response = jsonify(dict(error='Login required'))
            response.status_code = 401
            return response
        return jsonify(self.user_info(user))

    def delete(self):
        """
        Log out the current user
        """
        username = get_jwt_identity()
        user = None
        if username:
            user = models.User.get(db_session, username=username)
        if user:
            access: Optional[models.Token] = None
            for token in db_session.query(models.Token).filter_by(user_pk=user.pk, revoked=False):
                token.revoked = True
                if token.token_type == models.TokenType.access.value:
                    access = token
            if access is None:
                decoded_token = get_raw_jwt()
                models.Token.add(decoded_token, current_app.config['JWT_IDENTITY_CLAIM'],
                                 revoked=True, session=db_session)
        return jsonify('Logged out')

    def user_info(self, user):
        rv = user.to_dict(exclude=["password", "groups_mask"])
        rv['groups'] = [g.name for g in user.groups]
        rv['options'] = {
            'colourScheme': current_options.colour_scheme,
            'maxTickets': current_options.max_tickets_per_user,
            'rows': current_options.rows,
            'columns': current_options.columns,
        }
        return rv


class CheckUserApi(MethodView):
    decorators = [uses_database]

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
            response['username'] = models.User.exists(
                db_session, username=username)
        if email:
            response['email'] = models.User.exists(db_session, email=email)
        return jsonify(response)


class ResetPasswordUserApi(MethodView):
    decorators = [get_options, uses_database]

    def post(self):
        """
        Either request a password reset or confirm a password reset.
        """
        # TODO: revoke access token
        email = request.json.get('email', None)
        if not email:
            return jsonify_no_content(400)
        user = models.User.get(db_session, email=email)
        response = {
            "email": email,
            "success": True,
        }
        if not user:
            # we don't divulge if the user really exists
            return jsonify(response)
        try:
            # process a password reset when a user has followed the link
            token = request.json['token']
            password = request.json['password']
            confirm = request.json['confirmPassword']
            # TODO: check for link expiry
            if password != confirm or token != user.reset_token:
                response['error'] = 'Incorrect email address or the password reset link has expired'
                response['success'] = False
                return jsonify(response)
            user.reset_date = None
            user.reset_token = None
            user.set_password(password)
            db_session.commit()
            return jsonify(response)
        except KeyError:
            pass
        # this is a password reset request, create a random token and
        # email a link using this token to the registered email address
        user.reset_date = datetime.datetime.now()
        user.reset_token = secrets.token_urlsafe(16)
        try:
            self.send_reset_email(user)
        except Exception as err:
            response['error'] = str(err)
            response['success'] = False
        return jsonify(response)

    def send_reset_email(self, user):
        """
        Send an email to the user to allow them to reset their password.
        The email will contain both a plain text and an HTML version.
        """
        settings = current_options.email_settings()
        for option in ['server', 'port', 'sender']:
            if not getattr(settings, option):
                raise ValueError(f"Invalid SMTP settings: {option} is not set")
        context = {
            'subject': 'Musical Bingo password reset request',
            'time_limit': '7 days',
            'url': request.url_root,
            'reset_link': urljoin(request.url_root, url_for('reset_password', token=user.reset_token)),
        }
        message = MIMEMultipart("alternative")
        message["Subject"] = context["subject"]
        message["From"] = settings.sender
        message["To"] = user.email
        part1 = MIMEText(render_template(
            'templates/password-reset.txt', **context), "plain")
        part2 = MIMEText(render_template(
            'templates/password-reset.html', **context), "html")
        message.attach(part1)
        message.attach(part2)
        context = ssl.create_default_context()
        if settings.starttls:
            with smtplib.SMTP(settings.server, settings.port) as server:
                server.set_debuglevel(2)
                server.ehlo_or_helo_if_needed()
                server.starttls(context=context)
                server.ehlo_or_helo_if_needed()
                if settings.username:
                    server.login(settings.username, settings.password)
                server.send_message(message, settings.sender, user.email)
        else:
            with smtplib.SMTP_SSL(settings.server, settings.port, context=context) as server:
                # server.set_debuglevel(2)
                server.ehlo_or_helo_if_needed()
                if settings.username:
                    server.login(settings.username, settings.password)
                server.send_message(message, settings.sender, user.email)


class UserManagmentApi(MethodView):
    decorators = [jwt_required, uses_database]

    def get(self):
        """
        Get the list of registered users
        """
        if not current_user.is_admin:
            jsonify_no_content(401)
        users = []
        for user in models.User.all(db_session):
            item = user.to_dict(exclude=['password', 'groups_mask'])
            item['groups'] = [g.name for g in user.groups]
            users.append(item)
        return jsonify(users)

    def post(self):
        """
        Modify or delete users
        """
        if not current_user.is_admin:
            jsonify_no_content(401)
        if not request.json:
            return jsonify_no_content(400)
        result = {
            "errors": [],
            "modified": [],
            "deleted": []
        }
        for idx, item in enumerate(request.json):
            self.modify_user(result, idx, item)
        return jsonify(result)

    @staticmethod
    def modify_user(result, idx, item):
        """
        Modify the settings of the specified user
        """
        try:
            pk = item['pk']
            deleted = item['deleted']
            username = item['username']
            email = item['email']
            groups = item['groups']
        except KeyError as err:
            result["errors"].append(f"{idx}: Missing field {err}")
            return
        user = models.User.get(db_session, pk=pk)
        if user is None:
            result["errors"].append(f"{idx}: Unknown user {pk}")
            return
        if deleted == True:
            db_session.delete(user)
            result['deleted'].append(pk)
            return
        modified = False
        if username != user.username:
            if models.User.exists(db_session, username=username):
                result["errors"].append(
                    f"{idx}: Username {username} already present")
            else:
                user.username = username
                modified = True
        if email != user.email:
            if models.User.exists(db_session, email=email):
                result["errors"].append(
                    f"{idx}: Email {email} already present")
            else:
                user.email = email
                modified = True
        group_mask = user.groups_mask
        user.set_groups(groups)
        if group_mask != user.groups_mask:
            modified = True
        if modified:
            result['modified'].append(pk)


class RefreshApi(MethodView):
    decorators = [jwt_refresh_token_required, uses_database]

    def post(self):
        username = get_jwt_identity()
        if not models.db.User.exists(db_session, username=username):
            return jsonify_no_content(401)
        ret = {
            'accessToken': create_access_token(identity=username)
        }
        return jsonify(ret, 200)


class ListGamesApi(MethodView):
    decorators = [get_options, jwt_required, uses_database]

    def get(self):
        """
        Returns a list of all past and upcoming games
        """
        now = datetime.datetime.now()
        today = now.replace(hour=0, minute=0)
        start = today - datetime.timedelta(days=365)
        end = now + datetime.timedelta(days=7)
        if current_user.is_admin:
            games = models.Game.all(db_session).order_by(models.Game.start)
        else:
            games = db_session.query(models.Game).\
                filter(models.Game.start <= end).\
                filter(models.Game.start >= start).\
                order_by(models.Game.start)
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
            js_game['userCount'] = db_session.query(
                models.BingoTicket).filter(
                    models.BingoTicket.user == current_user,
                    models.BingoTicket.game == game).count()
            assert current_options is not None
            opts = game.game_options(current_options)
            js_game['options'] = opts
            btk = BingoTicket(palette=opts['palette'], columns=opts['columns'])
            backgrounds: List[str] = []
            for row in range(opts['rows']):
                for col in range(opts['columns']):
                    backgrounds.append(btk.box_colour_style(col, row).css())
            js_game['options']['backgrounds'] = backgrounds
            del js_game['options']['palette']
            if game.start >= today and game.end > now:
                future.append(js_game)
            else:
                past.append(js_game)
        return jsonify(dict(games=future, past=past))


class GameDetailApi(MethodView):
    decorators = [get_game, get_options, jwt_required, uses_database]

    def get(self, game_pk):
        """
        Get the extended detail for a game.
        For a game host, this detail will include the complete track listing.
        """
        now = datetime.datetime.now()
        data = current_game.to_dict()
        data['tracks'] = []
        if current_game.end < now or current_user.has_permission(
                models.Group.host):
            for track in current_game.tracks:  # .order_by(models.Track.number):
                trk = track.song.to_dict(
                    only=['album', 'artist', 'title', 'duration'])
                trk.update(track.to_dict(only=['pk', 'number', 'start_time']))
                trk['song'] = track.song.pk
                data['tracks'].append(trk)
        opts = current_game.game_options(current_options)
        data['options'] = opts
        btk = BingoTicket(palette=opts['palette'], columns=opts['columns'])
        backgrounds: List[str] = []
        for row in range(opts['rows']):
            for col in range(opts['columns']):
                backgrounds.append(btk.box_colour_style(col, row).css())
        data['options']['backgrounds'] = backgrounds
        del data['options']['palette']
        return jsonify(data)

    def post(self, game_pk):
        """
        Modify a game
        """
        if not current_user.is_admin:
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
            current_game.set(**changes)
        result['game'] = current_game.to_dict()
        return jsonify(result)

    def delete(self, **kwargs):
        """
        Delete a game
        """
        # TODO: decide which roles are allowed to delete a game
        if not current_user.is_admin:
            return jsonify_no_content(401)
        db_session.delete(current_game)
        return jsonify_no_content(200)


class TicketsApi(MethodView):
    decorators = [get_options, get_game, jwt_required, uses_database]

    def get(self, game_pk, ticket_pk=None):
        if ticket_pk is not None:
            return self.get_ticket_detail(ticket_pk)
        return self.get_ticket_list()

    def get_ticket_list(self):
        """
        Get the list of Bingo tickets for the specified game.
        """
        tickets: List[Dict[str, Any]] = []
        if current_user.is_admin:
            game_tickets = current_game.bingo_tickets.order_by(
                models.BingoTicket.number)
        else:
            game_tickets = current_game.bingo_tickets
        for ticket in game_tickets:
            tck = {
                'pk': ticket.pk,
                'number': ticket.number,
                'game': ticket.game_pk,
                'checked': ticket.checked,
            }
            tck['user'] = ticket.user_pk if ticket.user is not None else None
            tickets.append(tck)
        return jsonify(tickets)

    def get_ticket_detail(self, ticket_pk):
        """
        Get the detailed information for a Bingo Ticket.
        """
        ticket = models.BingoTicket.get(
            db_session, game=current_game, pk=ticket_pk)
        if ticket is None:
            return jsonify({'error': 'Not found'}, 404)
        if ticket.user != current_user and not current_user.has_permission(
                models.Group.host):
            response = jsonify({'error': 'Not authorised'})
            response.status_code = 401
            return response
        tracks: List[JsonObject] = []
        for track in ticket.tracks_in_order():
            trk = track.song.to_dict(only=['artist', 'title'])
            tracks.append(trk)
        card = ticket.to_dict(exclude=['order', 'tracks', 'fingerprint'])
        card['tracks'] = tracks
        return jsonify(card)

    def put(self, game_pk, ticket_pk=None):
        """
        claim a ticket for this user
        """
        ticket = None
        if ticket_pk is not None:
            ticket = models.BingoTicket.get(
                db_session, game=current_game, pk=ticket_pk)
        if ticket is None:
            return jsonify_no_content(404)
        if not ticket.user:
            ticket.user = current_user
            return jsonify_no_content(201)
        if ticket.user != current_user:
            # ticket already taken
            return jsonify_no_content(406)
        return jsonify_no_content(200)

    def delete(self, game_pk, ticket_pk=None):
        """
        release a ticket for this user
        """
        ticket = None
        if ticket_pk is not None:
            ticket = models.BingoTicket.get(
                db_session, game=current_game, pk=ticket_pk)
        if ticket is None:
            return jsonify_no_content(404)
        if not ticket.user:
            return jsonify_no_content(204)
        if ticket.user.pk != current_user.pk and not current_user.has_permission(
                models.Group.host):
            return jsonify_no_content(401)
        ticket.user = None
        return jsonify_no_content(204)


class TicketsStatusApi(MethodView):
    decorators = [get_game, jwt_required, uses_database]

    def get(self, game_pk):
        """
        Get information on which tickets have already been claimed and which
        ones are still available.
        """
        claimed: Dict[int, Optional[int]] = {}
        for ticket in current_game.bingo_tickets:
            if ticket.user is not None:
                claimed[ticket.pk] = ticket.user.pk
            else:
                claimed[ticket.pk] = None
        return jsonify(dict(claimed=claimed))


class CheckCellApi(MethodView):
    decorators = [get_options, get_ticket, get_game, jwt_required, uses_database]

    def put(self, number, **kwargs):
        """
        set the check mark on a ticket.
        Only the owner of the ticket or a host can change this.
        """
        if number < 0 or number >= (current_options.columns * current_options.rows):
            return jsonify_no_content(404)
        current_ticket.checked |= (1 << number)
        return jsonify_no_content(204)

    def delete(self, number, **kwargs):
        """
        clear the check mark on a ticket.
        Only the owner of the ticket or a host can change this.
        """
        if number < 0 or number >= (current_options.columns * current_options.rows):
            return jsonify_no_content(404)
        current_ticket.checked &= ~(1 << number)
        return jsonify_no_content(204)
