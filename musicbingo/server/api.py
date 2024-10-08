# pylint: disable=unused-argument

"""
HTTP REST API for accessing the database
"""
from collections.abc import Iterable
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from pathlib import Path
import random
import secrets
import smtplib
import ssl
import time
from typing import Any, Dict, List, Optional, Set, Type, Union, cast
from urllib.parse import urljoin

import fastjsonschema  # type: ignore
from flask import (  # type: ignore
    request, render_template, g,
    session, url_for,
    current_app, Response
)
from flask.views import MethodView  # type: ignore
from flask_jwt_extended import (  # type: ignore
    jwt_required, create_access_token,
    get_jwt_identity, current_user, get_jwt,
    create_refresh_token, decode_token,
)
from sqlalchemy import or_, select

from musicbingo import models, utils, workers
from musicbingo.models.modelmixin import JsonObject
from musicbingo.models.session import DatabaseSession
from musicbingo.models.token import TokenType
from musicbingo.mp3.factory import MP3Factory
from musicbingo.bingoticket import BingoTicket
from musicbingo.options import ExtraOptions, OptionField, Options
from musicbingo.options.enum_wrapper import EnumWrapper
from musicbingo.palette import Palette
from musicbingo.schemas import JsonSchema, validate_json

from .decorators import (
    db_session, uses_database, get_game, get_ticket,
    jsonify, jsonify_no_content,
    get_options, get_directory
)

def decorate_user_info(user):
    """
    Decorate the User model with additional information
    """
    retval = user.to_dict(exclude={"password", "groups_mask"})
    retval['groups'] = [g.name.lower() for g in user.groups]
    retval['options'] = {
        'colourScheme': g.current_options.colour_scheme.name.lower(),
        'colourSchemes': [name.lower() for name in Palette.names()],
        'maxTickets': g.current_options.max_tickets_per_user,
        'rows': g.current_options.rows,
        'columns': g.current_options.columns,
    }
    return retval


class UserApi(MethodView):
    """
    API for a user to login, logout, register
    """
    decorators = [get_options, jwt_required(optional=True), uses_database]

    def post(self) -> Response:
        """
        Attempt to log in.
        'username' can be either a username or an email address
        """
        data: JsonObject = cast(JsonObject, request.json)
        try:
            username: str = data['username']
            password: str = data['password']
        except KeyError:
            response: Response = jsonify(
                {'error': 'Invalid request'})
            response.status_code = 400
            return response

        rememberme: bool = data.get('rememberme', False)  # type: ignore
        user: models.User | None = cast(
            models.User | None,
            models.User.get(cast(DatabaseSession, db_session), username=username))
        if user is None:
            user = cast(models.User | None, models.User.get(db_session, email=username))
        if user is None:
            response = jsonify(
                {'error': 'Unknown username or wrong password'})
            response.status_code = 401
            return response
        if not user.check_password(password):
            response = jsonify({'error': 'Unknown username or wrong password'})
            response.status_code = 401
            return response
        user.last_login = datetime.datetime.now()
        user.reset_expires = None
        user.reset_token = None
        result = decorate_user_info(user)
        session.clear()
        result['accessToken'] = create_access_token(identity=user.username)
        if isinstance(result['accessToken'], bytes):
            result['accessToken'] = str(result['accessToken'], 'utf-8')
        expires: Optional[datetime.timedelta] = None
        if rememberme:
            expires = cast(datetime.timedelta,
                           current_app.config['REMEMBER_ME_REFRESH_TOKEN_EXPIRES'])
        result['refreshToken'] = create_refresh_token(identity=user.username,
                                                      expires_delta=expires)  # type: ignore
        if isinstance(result['refreshToken'], bytes):
            result['refreshToken'] = str(result['refreshToken'], 'utf-8')
        models.Token.add(decode_token(result['refreshToken']),
                         current_app.config['JWT_IDENTITY_CLAIM'],
                         False, db_session)
        return jsonify(result)

    def put(self) -> Response:
        """
        Register a new user
        """
        try:
            req_json = cast(JsonObject, request.json)
            email = req_json['email']
            password = req_json['password']
            username = req_json['username']
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
                           groups_mask=models.Group.USERS.value,
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
            'user': decorate_user_info(user),
            'accessToken': create_access_token(identity=user.username),
            'refreshToken': refresh_token,
        })

    def get(self) -> Response:
        """
        If user is logged in, return the information about the user
        """
        username = get_jwt_identity()
        if not username:
            return jsonify({'error': 'Login required'}, 401)
        user = models.User.get(db_session, username=username)
        if user is None:
            # TODO: revoke access token
            response = jsonify({'error': 'Login required'})
            response.status_code = 401
            return response
        return jsonify(decorate_user_info(user))

    def delete(self) -> Response:
        """
        Log out the current user
        """
        username = get_jwt_identity()
        user = None
        if username:
            user = cast(models.User, models.User.get(db_session, username=username))
        if user:
            access: Optional[models.Token] = None
            for token in db_session.query(models.Token).filter_by(user_pk=user.pk, revoked=False):
                token.revoked = True
                if token.token_type == models.TokenType.ACCESS.value:
                    access = token
            if access is None:
                decoded_token = get_jwt()
                models.Token.add(decoded_token, current_app.config['JWT_IDENTITY_CLAIM'],
                                 revoked=True, session=db_session)
        return jsonify('Logged out')


class CheckUserApi(MethodView):
    """
    API to check if a username or email has already been
    registered
    """
    decorators = [uses_database]

    def post(self) -> Response:
        """
        check if username or email is already registered
        """
        response = {
            "username": False,
            "email": False
        }
        username = request.json.get('username', None)  # type: ignore
        email = request.json.get('email', None)  # type: ignore
        if not username and not email:
            return jsonify_no_content(400)
        if username:
            response['username'] = models.User.exists(
                db_session, username=username)
        if email:
            response['email'] = models.User.exists(db_session, email=email)
        return jsonify(response)


class GuestAccountApi(MethodView):
    """
    API to check if a guest token is valid and create
    guest accounts
    """
    decorators = [get_options, jwt_required(optional=True), uses_database]

    def get(self) -> Response:
        """
        Get list of tokens
        """
        username = get_jwt_identity()
        if not username:
            return jsonify_no_content(401)
        user = cast(models.User, models.User.get(db_session, username=username))
        if user is None or not user.is_admin:
            return jsonify_no_content(401)
        tokens = models.Token.search(db_session, token_type=TokenType.GUEST.value,
                                     revoked=False)
        return jsonify([token.to_dict() for token in tokens])

    def post(self) -> Response:
        """
        check if a guest token is valid
        """
        if not request.json:
            return jsonify_no_content(400)
        jti = request.json.get('token', None)
        if not jti:
            return jsonify_no_content(400)
        token = cast(models.Token, models.Token.get(
            db_session, jti=jti, token_type=TokenType.GUEST.value))
        result = {
            "success": token is not None and not token.revoked
        }
        return jsonify(result)

    def put(self) -> Response:
        """
        Create a guest account
        """
        if not request.json:
            return jsonify_no_content(400)
        jti = request.json.get('token', None)
        if not jti:
            return jsonify_no_content(400)
        token = cast(models.Token, models.Token.get(
            db_session, jti=jti, token_type=TokenType.GUEST.value))
        result: JsonObject = {
            "success": token is not None,
        }
        if token is None:
            result["error"] = "Guest token missing"
            return jsonify(result)
        username: Optional[str] = None
        while username is None:
            guest_id = random.randint(100, 999)
            username = f'guest{guest_id}'
            user = models.User.get(db_session, username=username)
            if user is not None:
                username = None
        password = secrets.token_urlsafe(14)
        user = models.User(username=username,
                           password=models.User.hash_password(password),
                           email=username,
                           groups_mask=models.Group.GUESTS.value,
                           last_login=datetime.datetime.now())
        db_session.add(user)
        db_session.commit()
        result.update(decorate_user_info(user))
        result['accessToken'] = create_access_token(identity=username)
        result['password'] = password
        expires = current_app.config['GUEST_REFRESH_TOKEN_EXPIRES']
        result['refreshToken'] = create_refresh_token(identity=username,
                                                      expires_delta=expires)
        models.Token.add(decode_token(result['refreshToken']),
                         current_app.config['JWT_IDENTITY_CLAIM'],
                         False, db_session)
        return jsonify(result)


class CreateGuestTokenApi(MethodView):
    """
    Create a guest token
    """

    decorators = [jwt_required(), uses_database]

    def put(self) -> Response:
        """
        Create a guest token
        """
        if not current_user.is_admin:
            return jsonify_no_content(401)
        jti = secrets.token_urlsafe(7)
        expires = datetime.datetime.now() + datetime.timedelta(days=7)
        token = models.Token(jti=jti,
                             token_type=TokenType.GUEST.value,
                             username=jti,
                             expires=expires,
                             revoked=False)
        db_session.add(token)
        db_session.commit()
        return jsonify({"success": True, "token": token.to_dict()})


class DeleteGuestTokenApi(MethodView):
    """
    API to delete a guest token is valid and create
    guest accounts
    """
    decorators = [jwt_required(optional=True), uses_database]

    def delete(self, token: str) -> Response:
        """
        Delete a guest token
        """
        if not current_user.is_admin:
            return jsonify_no_content(401)
        db_token: models.Token | None = cast(models.Token | None, models.Token.get(
            db_session, jti=token, token_type=TokenType.GUEST.value))
        if db_token is None:
            return jsonify_no_content(404)
        db_token.revoked = True
        return jsonify_no_content(204)

class ResetPasswordUserApi(MethodView):
    """
    API to allow a user to request a password reset and to
    use the password reset link to choose a new password
    """
    decorators = [get_options, uses_database]

    def post(self) -> Response:
        """
        Either request a password reset or confirm a password reset.
        """
        if not request.json:
            return jsonify_no_content(400)
        email = request.json.get('email', None)
        if not email:
            return jsonify_no_content(400)
        user = cast(models.User, models.User.get(db_session, email=email))
        if not user:
            # we don't divulge if the user really exists
            response = {
                "email": email,
                "success": True,
            }
            return jsonify(response)
        if 'token' in request.json:
            return self.check_password_update(user)
        return self.create_password_reset_token(user)

    def check_password_update(self, user: models.User) -> Response:
        """
        Check request to change password.
        """
        response = {
            "email": user.email,
            "debug": "check_password_update",
            "success": True,
        }
        try:
            token: str = cast(JsonObject, request.json)['token']
            password: str = cast(JsonObject, request.json)['password']
            confirm: str = cast(JsonObject, request.json)['confirmPassword']
            # TODO: use UTC
            now = datetime.datetime.now()
            if password != confirm:
                response['error'] = 'Passwords do not match'
                response['success'] = False
            elif (
                    token != user.reset_token or
                    user.reset_expires is None or
                    user.reset_expires < now):
                response['error'] = 'Incorrect email address or the password reset link has expired'
                response['success'] = False
            else:
                user.reset_expires = None
                user.reset_token = None
                user.set_password(password)
                db_session.commit()
        except KeyError as err:
            response['success'] = False
            response['error'] = f'Missing field {err}'
        return jsonify(response)

    def create_password_reset_token(self, user: models.User) -> Response:
        """
        Create a random token and email a link using this token to
        the registered email address. The email will contain both a
        plain text and an HTML version.
        """
        response = {
            "email": user.email,
            "success": True,
        }
        token_lifetime = current_app.config['PASSWORD_RESET_TOKEN_EXPIRES']
        if isinstance(token_lifetime, int):
            token_lifetime = datetime.timedelta(seconds=token_lifetime)
        user.reset_expires = datetime.datetime.now() + token_lifetime
        user.reset_token = secrets.token_urlsafe(16)
        # pylint: disable=broad-except
        try:
            self.send_reset_email(user, token_lifetime)
        except Exception as err:
            response['error'] = type(err).__name__ + ": " + str(err)
            response['success'] = False
        return jsonify(response)

    def send_reset_email(self, user: models.User, token_lifetime: datetime.timedelta) -> None:
        """
        Send an email to the user to allow them to reset their password.
        The email will contain both a plain text and an HTML version.
        """
        settings = g.current_options.email_settings()
        for option in ['server', 'port', 'sender', 'username', 'password']:
            if not getattr(settings, option, None):
                raise ValueError(f"Invalid SMTP settings: {option} is not set")
        token_lifetime = current_app.config['PASSWORD_RESET_TOKEN_EXPIRES']
        reply_to = settings.reply_to
        if reply_to is None:
            reply_to = settings.sender
        context = {
            'subject': 'Musical Bingo password reset request',
            'time_limit': f'{token_lifetime.days} days',
            'url': request.url_root,
            'reply_to': reply_to,
            'reset_link': urljoin(request.url_root,
                                  url_for('reset_password', path=user.reset_token)),
        }
        message = MIMEMultipart("alternative")
        message["Subject"] = context["subject"]
        message["From"] = settings.sender
        message["To"] = user.email
        part1 = MIMEText(render_template(
            'password-reset.txt', **context), "plain")
        part2 = MIMEText(render_template(
            'password-reset.html', **context), "html")
        message.attach(part1)
        message.attach(part2)
        ssl_context = ssl.create_default_context()
        if settings.starttls:
            with smtplib.SMTP(settings.server, settings.port) as server:
                #server.set_debuglevel(2)
                server.ehlo_or_helo_if_needed()
                server.starttls(context=ssl_context)  # type: ignore
                server.ehlo_or_helo_if_needed()
                if settings.username:
                    assert settings.password is not None
                    server.login(settings.username, settings.password)
                server.send_message(message, settings.sender, user.email)
        else:
            with smtplib.SMTP_SSL(settings.server, settings.port, context=ssl_context) as server:
                # server.set_debuglevel(2)
                server.ehlo_or_helo_if_needed()
                if settings.username:
                    assert settings.password is not None
                    server.login(settings.username, settings.password)
                server.send_message(message, settings.sender, user.email)


class ModifyUserApi(MethodView):
    """
    API to allow a user to modifier their own account
    """
    decorators = [jwt_required(), uses_database]

    def post(self) -> Response:
        """
        Modify the user's own password or email
        """
        if not request.json:
            return jsonify_no_content(400)
        response = {
            "email": current_user.email,
            "success": True,
        }
        try:
            email = request.json['email']
            current_password = request.json['existingPassword']
            password = request.json['password']
            confirm = request.json['confirmPassword']
            if not current_user.check_password(current_password):
                response["success"] = False
                response["error"] = "Existing password did not match"
            elif password != confirm:
                response["success"] = False
                response["error"] = "New passwords do not match"
            else:
                current_user.set_password(password)
                current_user.email = email
                response["email"] = email
                db_session.commit()
        except KeyError as err:
            response['success'] = False
            response['error'] = f'Missing field {err}'
        return jsonify(response)


class UserManagmentApi(MethodView):
    """
    Admin API to view and modify all users
    """
    decorators = [jwt_required(), uses_database]

    def get(self) -> Response:
        """
        Get the list of registered users
        """
        if not current_user.is_admin:
            jsonify_no_content(401)
        users = []
        for user in cast(Iterable[models.User], models.User.all(db_session)):
            item = user.to_dict(exclude={'password', 'groups_mask'})
            item['groups'] = [g.name.lower() for g in user.groups]
            users.append(item)
        return jsonify(users)

    def post(self) -> Response:
        """
        Add, modify or delete users
        """
        if not current_user.is_admin:
            jsonify_no_content(401)
        if not request.json:
            return jsonify_no_content(400)
        result: JsonObject = {
            "errors": [],
            "added": [],
            "modified": [],
            "deleted": []
        }
        for idx, item in enumerate(request.json):
            self.modify_user(result, idx, item)
        return jsonify(result)

    @staticmethod
    def modify_user(result: JsonObject, idx: int, item: JsonObject) -> None:
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
        password = item.get('password', None)
        if item.get('newUser', False):
            user = models.User(email=email, username=username)
            user.set_password(password)
            user.set_groups(groups)
            db_session.add(user)
            db_session.flush()
            pk = user.pk
            result["added"].append({'username': username, 'pk': pk})
            return
        user = cast(models.User, models.User.get(db_session, pk=pk))
        if user is None:
            result["errors"].append(f"{idx}: Unknown user {pk}")
            return
        if deleted:
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
        if password:
            user.set_password(password)
            modified = True
        if modified:
            result['modified'].append(pk)


class RefreshApi(MethodView):
    """
    API to request a new access token from a refresh token
    """
    decorators = [jwt_required(refresh=True), uses_database]

    def post(self):
        """
        generate a new access token from a refresh token
        """
        username = get_jwt_identity()
        if not models.db.User.exists(db_session, username=username):
            return jsonify_no_content(401)
        ret = {
            'accessToken': create_access_token(identity=username)
        }
        return jsonify(ret, 200)

def decorate_game(game: models.Game, with_count: bool = False) -> models.JsonObject:
    """
    Convert game into a dictionary and add extra fields
    """
    js_game = game.to_dict()
    if with_count:
        # pylint: disable=no-member
        js_game['userCount'] = cast(models.DatabaseSession, db_session).query(
            models.BingoTicket).filter(
                models.BingoTicket.user == current_user,
                models.BingoTicket.game_pk == game.pk).count()
    assert g.current_options is not None
    opts = game.game_options(cast(Options, g.current_options))
    js_game['options'] = opts
    palette = Palette.from_string(opts['colour_scheme'])
    btk = BingoTicket(palette=palette, columns=opts['columns'])
    backgrounds: List[str] = []
    for row in range(opts['rows']):
        for col in range(opts['columns']):
            backgrounds.append(btk.box_colour_style(col, row).css())
    js_game['options']['backgrounds'] = backgrounds
    return js_game

class WorkerMultipartResponse:
    """
    Provides streamed response with current progress of the
    worker thread.
    This must be used with a multipart/mixed content type.
    It will generate a application/json entity at regular
    intervals that contains the current progress of this
    import.
    """
    def __init__(self, worker_type: Type[workers.BackgroundWorker], filename: str,
                 data: JsonObject):
        self.done = False
        self.first_response = True
        self.result: Optional[workers.DbIoResult] = None
        args = (Path(filename), data,)
        # pylint: disable=no-member
        options = Options(**cast(Options, g.current_options).to_dict())
        self.worker = worker_type(args, options, self.import_done)
        self.boundary = secrets.token_urlsafe(16).replace('-', '')
        self.errors: List[str] = []

    def add_error(self, error: str) -> None:
        """
        Add an error message
        This error will be included in the next progress report
        """
        self.errors.append(error)

    def generate(self):
        """
        Generator that yields the current import progress
        """
        if not self.done:
            self.worker.start()
        min_pct = 1.0
        while not self.done and not self.worker.progress.abort:
            time.sleep(0.5)
            if not self.worker.bg_thread.is_alive():
                self.worker.bg_thread.join()
                self.worker.finalise(self.worker.result)
                self.done = True
                continue
            progress = {
                "errors": self.errors,
                "text": self.worker.progress.text,
                "pct": self.worker.progress.total_percentage,
                "phase": self.worker.progress.current_phase,
                "numPhases": self.worker.progress.num_phases,
                "done": False,
            }
            if self.worker.progress.total_percentage <= min_pct and not self.done:
                continue
            self.errors = []
            min_pct = self.worker.progress.total_percentage + 1.0
            yield self.create_response(progress)
        progress = {
            "errors": self.errors,
            "text": self.worker.progress.text,
            "pct": 100.0,
            "phase": self.worker.progress.current_phase,
            "numPhases": self.worker.progress.num_phases,
            "done": True,
            "success": False
        }
        if self.worker.result:
            progress["added"] = self.worker.result.added
            progress["keys"] = {}
            for table, count in self.worker.result.added.items():
                progress["keys"][table] = self.worker.result.pk_maps[table]
                if count > 0:
                    progress["success"] = True
        yield self.create_response(progress, True)

    def create_response(self, data, last=False):
        """
        Create a multipart response
        """
        encoded = bytes(json.dumps(data, default=utils.flatten), 'utf-8')
        leng = len(encoded)
        closed = b'Connection: close\r\n' if last else b''
        lines = [
            b'',
            bytes(f'--{self.boundary}', 'ascii'),
            b'Content-Type: application/json',
            bytes(f'Content-Length: {leng}', 'ascii'),
            closed,
            encoded,
        ]
        if self.first_response:
            self.first_response = False
            lines.pop(0)
        if last:
            lines.append(bytes(f'--{self.boundary}--\r\n', 'ascii'))
        return b'\r\n'.join(lines)

    def import_done(self, result: workers.DbIoResult) -> None:
        """
        Called when import has completed
        """
        self.result = result
        self.done = True

class ExportDatabaseGenerator:
    """
    Yields output of the export process without loading entire database into memory
    """

    def generate(self, opts: JsonObject):
        """
        Generator that yields the output of the export process
        """
        assert opts is not None
        yield b'{\n"Options":'
        yield bytes(
            json.dumps(opts, indent='  ', default=utils.flatten, sort_keys=True),
            'utf-8')
        yield b',\n'
        tables = [models.User, models.Artist, models.Album, models.Directory,
                  models.Song, models.Game, models.Track, models.BingoTicket]
        for table in tables:
            yield bytes(f'"{table.__plural__}":', 'utf-8')  # type: ignore
            contents = []
            with models.db.session_scope() as dbs:
                for item in table.all(dbs):  # type: ignore
                    data = item.to_dict(with_collections=True)
                    contents.append(data)  # type: ignore
            yield bytes(
                json.dumps(contents, indent='  ', default=utils.flatten, sort_keys=True),
                'utf-8')
            if table != tables[-1]:
                yield b','
            yield b'\n'
        yield b'}\n'

class DatabaseApi(MethodView):
    """
    API for importing and exporting entire database
    """
    decorators = [get_options, jwt_required(), uses_database]

    def get(self) -> Response:
        """
        Export database to a JSON file.
        The data is streamed to the client to avoid having to
        create the entire database JSON object in memory
        """
        gen = ExportDatabaseGenerator()
        opts = g.current_options.to_dict(
            exclude={'command', 'exists', 'jsonfile', 'database', 'debug',
                     'game_id', 'title', 'mp3_editor', 'mode', 'smtp',
                     'secret_key'})
        clips = g.current_options.clips()
        try:
            opts['clip_directory'] = cast(Path, clips).resolve().as_posix()
        except AttributeError:
            # PurePosixPath and PureWindowsPath don't have the resolve() function
            opts['clip_directory'] = clips.as_posix()
        return Response(gen.generate(opts),
                        direct_passthrough=True,
                        mimetype='application/json; charset=utf-8')

    def put(self) -> Response:
        """
        Import database
        """
        if not request.json:
            return jsonify_no_content(400)
        if not current_user.is_admin:
            return jsonify_no_content(401)
        try:
            data = request.json['data']
            filename = request.json['filename']
        except KeyError:
            return jsonify_no_content(400)
        imp_resp = WorkerMultipartResponse(workers.ImportDatabase, filename, data)
        try:
            validate_json(JsonSchema.DATABASE, data)
        except fastjsonschema.JsonSchemaException as err:
            imp_resp.add_error('Not a valid database file')
            # pylint: disable=no-member
            imp_resp.add_error(err.message)
            imp_resp.done = True
        return Response(imp_resp.generate(),
                        direct_passthrough=True,
                        mimetype=f'multipart/mixed; boundary={imp_resp.boundary}')

class ListDirectoryApi(MethodView):
    """
    API for listing all directories
    """
    decorators = [get_options, jwt_required(), uses_database]

    def get(self) -> Response:
        """
        Returns a list of all directories
        """
        if not current_user.has_permission(models.Group.CREATORS):
            return jsonify_no_content(401)
        result = []
        for mdir in cast(Iterable[models.Directory], models.Directory.all(db_session)):
            item = mdir.to_dict(with_collections=True)
            item['exists'] = Path(mdir.name).exists()
            result.append(item)
        return jsonify(result)


class DirectoryDetailsApi(MethodView):
    """
    API for listing all directories
    """
    decorators = [get_directory, get_options, jwt_required(), uses_database]

    def get(self, dir_pk: int) -> Response:
        """
        Returns details of the specified directory
        """
        if not current_user.has_permission(models.Group.CREATORS):
            return jsonify_no_content(401)
        retval = g.current_directory.to_dict(with_collections=True, exclude={'songs'})
        retval['exists'] = Path(g.current_directory.name).exists()
        songs = []
        for song in g.current_directory.songs:
            item = song.to_dict(exclude={'artist', 'album'}, with_collections=False)
            item['artist'] = song.artist.name if song.artist is not None else ''
            item['album'] = song.album.name if song.album is not None else ''
            item['exists'] = song.absolute_path().exists()
            songs.append(item)
        retval['songs'] = songs
        return jsonify(retval)

class ListGamesApi(MethodView):
    """
    API for listing all games
    """
    decorators = [get_options, jwt_required(), uses_database]

    def get(self) -> Response:
        """
        Returns a list of all past and upcoming games
        """
        now = datetime.datetime.now()
        today = now.replace(hour=0, minute=0)
        end = now + datetime.timedelta(days=7)
        statement = select(models.Game)
        if not current_user.is_admin:
            statement = statement.filter(models.Game.start <= end)
        statement = statement.order_by(models.Game.start)
        future: list[JsonObject] = []
        past: list[JsonObject] = []
        for row in db_session.execute(statement):
            game: models.Game = row[0]
            if isinstance(game.start, str):
                game.start = cast(datetime.datetime | None, utils.parse_date(game.start))
            if isinstance(game.end, str):
                game.end = cast(datetime.datetime | None, utils.parse_date(game.end))
            js_game: JsonObject = decorate_game(game, with_count=True)
            if (
                    game.start is not None and
                    game.end is not None and
                    game.start >= today and
                    game.end > now
                ):
                future.append(js_game)
            else:
                past.append(js_game)
        return jsonify({'games': future, 'past': past})

    def put(self) -> Response:
        """
        Import a game
        """
        if not request.json:
            return jsonify_no_content(400)
        if not current_user.is_admin:
            return jsonify_no_content(401)
        try:
            data = request.json['data']
            filename = request.json['filename']
        except KeyError:
            return jsonify_no_content(400)
        imp_resp = WorkerMultipartResponse(workers.ImportGameTracks, filename, data)
        try:
            validate_json(JsonSchema.GAME_TRACKS, data)
        except fastjsonschema.JsonSchemaException as err:
            imp_resp.add_error('Not a valid gameTracks file')
            # pylint: disable=no-member
            imp_resp.add_error(err.message)
            imp_resp.done = True
        return Response(imp_resp.generate(),
                        direct_passthrough=True,
                        mimetype=f'multipart/mixed; boundary={imp_resp.boundary}')

class GameDetailApi(MethodView):
    """
    API for extended detail about a game and modification of a game
    """
    decorators = [get_game, get_options, jwt_required(), uses_database]

    def get(self, game_pk: int) -> Response:
        """
        Get the extended detail for a game.
        For a game host, this detail will include the complete track listing.
        """
        now = datetime.datetime.now()
        data = decorate_game(g.current_game)
        data['tracks'] = []
        if g.current_game.end < now or current_user.has_permission(
                models.Group.HOSTS):
            for track in g.current_game.tracks:  # .order_by(models.Track.number):
                trk = {
                    'artist': '',
                    'album': '',
                    'duration': track.song.duration,
                    'song': track.song.pk,
                    'title': track.song.title,
                }
                if track.song.artist is not None:
                    trk['artist'] = track.song.artist.name
                if track.song.album is not None:
                    trk['album'] = track.song.album.name
                trk.update(track.to_dict(only=['pk', 'number', 'start_time']))
                data['tracks'].append(trk)
        return jsonify(data)

    def post(self, game_pk: int) -> Response:
        """
        Modify a game
        """
        if not current_user.is_admin:
            return jsonify_no_content(401)
        if not request.json:
            return jsonify_no_content(400)

        result: JsonObject = {}
        try:
            start = utils.make_naive_utc(cast(
                datetime.datetime,
                utils.from_isodatetime(request.json['start'])))
            end = utils.make_naive_utc(cast(
                datetime.datetime,
                utils.from_isodatetime(request.json['end'])))
            changes = {
                'start': start,
                'end': end,
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
            game = g.current_game
            game.set(**changes)
            if 'options' in request.json:
                opts = game.game_options(g.current_options)
                opts.update(request.json['options'])
                game.options = opts
            # NOTE: deprecated, request should use an 'options' object
            if 'colour_scheme' in request.json:
                opts = game.game_options(g.current_options)
                opts['colour_scheme'] = request.json['colour_scheme']
                game.options = opts
            result['game'] = decorate_game(game, True)
        return jsonify(result)

    def delete(self, **kwargs) -> Response:
        """
        Delete a game
        """
        # TODO: decide which roles are allowed to delete a game
        if not current_user.is_admin:
            return jsonify_no_content(401)
        db_session.delete(g.current_game)
        return jsonify_no_content(204)

class ExportGameApi(MethodView):
    """
    Export a game to a JSON file
    """
    decorators = [get_game, get_options, jwt_required(), uses_database]

    def get(self, game_pk: int) -> Response:
        """
        Export a game to a JSON file
        """
        data = models.export_game_to_object(
            g.current_game.id, db_session)
        return jsonify(data)

class TicketsApi(MethodView):
    """
    API for information about one or more Bingo tickets
    """
    decorators = [get_options, get_game, jwt_required(), uses_database]

    def get(self, game_pk: int, ticket_pk: Optional[int] = None) -> Response:
        """
        get list of tickets for a game or detail for one ticket
        """
        if ticket_pk is not None:
            return self.get_ticket_detail(ticket_pk)
        return self.get_ticket_list()

    def get_ticket_list(self) -> Response:
        """
        Get the list of Bingo tickets for the specified game.
        """
        tickets: List[Dict[str, Any]] = []
        if current_user.is_admin:
            game_tickets = g.current_game.bingo_tickets.order_by(
                models.BingoTicket.number)
        else:
            game_tickets = g.current_game.bingo_tickets
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

    def get_ticket_detail(self, ticket_pk: int) -> Response:
        """
        Get the detailed information for a Bingo Ticket.
        """
        ticket = cast(models.BingoTicket, models.BingoTicket.get(
            db_session, game=g.current_game, pk=ticket_pk))
        if ticket is None:
            return jsonify({'error': 'Not found'}, 404)
        if ticket.user != current_user and not current_user.has_permission(
                models.Group.HOSTS):
            response = jsonify({'error': 'Not authorised'})
            response.status_code = 401
            return response
        tracks: List[JsonObject] = []
        for track in ticket.get_tracks(db_session):
            trk = {
                'artist': track.song.artist.name,
                'title': track.song.title
            }
            tracks.append(trk)
        card = ticket.to_dict(exclude={'order', 'tracks', 'fingerprint'})
        card['tracks'] = tracks
        return jsonify(card)

    def put(self, game_pk: int, ticket_pk: Optional[int] = None) -> Response:
        """
        claim a ticket for this user
        """
        ticket: Optional[models.BingoTicket] = None
        if ticket_pk is not None:
            ticket = cast(Optional[models.BingoTicket], models.BingoTicket.get(
                db_session, game=g.current_game, pk=ticket_pk))
        if ticket is None:
            return jsonify_no_content(404)
        if not ticket.user:
            ticket.user = current_user
            return jsonify_no_content(201)
        if ticket.user != current_user:
            # ticket already taken
            return jsonify_no_content(406)
        return jsonify_no_content(200)

    def delete(self, game_pk, ticket_pk=None) -> Response:
        """
        release a ticket for this user
        """
        ticket: Optional[models.BingoTicket] = None
        if ticket_pk is not None:
            ticket = cast(Optional[models.BingoTicket], models.BingoTicket.get(
                db_session, game=g.current_game, pk=ticket_pk))
        if ticket is None:
            return jsonify_no_content(404)
        if not ticket.user:
            return jsonify_no_content(204)
        if ticket.user.pk != current_user.pk and not current_user.has_permission(
                models.Group.HOSTS):
            return jsonify_no_content(401)
        ticket.user = None
        return jsonify_no_content(204)


class TicketsStatusApi(MethodView):
    """
    Get information on which tickets have already been claimed and which
    ones are still available.
    """

    decorators = [get_game, jwt_required(), uses_database]

    def get(self, game_pk: int) -> Response:
        """
        Get information on which tickets have already been claimed and which
        ones are still available.
        """
        claimed: Dict[int, Optional[int]] = {}
        for ticket in g.current_game.bingo_tickets:
            if ticket.user is not None:
                claimed[ticket.pk] = ticket.user.pk
            else:
                claimed[ticket.pk] = None
        return jsonify({"claimed": claimed})


class CheckCellApi(MethodView):
    """
    API to set and clear individual cells in a Bingo ticket
    """
    decorators = [get_options, get_ticket, get_game, jwt_required(), uses_database]

    def put(self, number: int, **kwargs) -> Response:
        """
        set the check mark on a ticket.
        Only the owner of the ticket or a host can change this.
        """
        if number < 0 or number >= (g.current_options.columns * g.current_options.rows):
            return jsonify_no_content(404)
        g.current_ticket.checked |= (1 << number)
        return jsonify_no_content(204)

    def delete(self, number: int, **kwargs) -> Response:
        """
        clear the check mark on a ticket.
        Only the owner of the ticket or a host can change this.
        """
        if number < 0 or number >= (g.current_options.columns * g.current_options.rows):
            return jsonify_no_content(404)
        g.current_ticket.checked &= ~(1 << number)
        return jsonify_no_content(204)

class SongApi(MethodView):
    """
    API to query songs in the database
    """
    decorators = [jwt_required(), uses_database]

    def get(self, dir_pk: Optional[int] = None, **kwargs) -> Response:
        """
        Search for songs in the database.
        If dir_pk is provided, only search within that directory
        """
        result: List[JsonObject] = []
        db_query = db_session.query(models.Song)
        if dir_pk is not None:
            db_query = db_query.filter_by(directory_pk=dir_pk)
        try:
            # if q CGI parameter is provided, it performs a
            # case insensitive search of both title and artist
            query = request.args['q']
            artists = db_session.query(models.Artist.pk).filter(
                models.Artist.name.ilike(f"%{query}%"))
            db_query = db_query.filter(or_(
                models.Song.title.ilike(f"%{query}%"),
                models.Song.artist_pk.in_(artists)
            ))
        except KeyError:
            pass
        for song in db_query:
            item = song.to_dict(exclude={'artist', 'album'})
            item['artist'] = song.artist.name
            item['album'] = song.album.name
            result.append(item)
        return jsonify(result)

class SettingsApi(MethodView):
    """
    Admin API to view and modify settings
    """
    decorators = [get_options, jwt_required(optional=True), uses_database]

    def is_admin(self) -> bool:
        """
        Check if a user is logged in, and is an admin
        """
        username = get_jwt_identity()
        if not username:
            return False
        user = cast(models.User, models.User.get(db_session, username=username))
        if user is None:
            return False
        return user.is_admin

    def get(self) -> Response:
        """
        Get the current settings
        """
        if not self.is_admin():
            result = {
                'privacy': self.translate_options(g.current_options.privacy)
            }
        else:
            result = {
                'app': self.translate_options(g.current_options),
            }
            for ext_cls in g.current_options.EXTRA_OPTIONS:
                ext_opts = cast(ExtraOptions,
                                getattr(g.current_options, ext_cls.LONG_PREFIX))
                result[ext_cls.LONG_PREFIX] = self.translate_options(ext_opts)
        return jsonify(result)

    @staticmethod
    def translate_options(options: Union[Options, ExtraOptions]) -> List[JsonObject]:
        """
        Convert the specifies options into a JSON array using
        JavaScript types for each field
        """
        opts = options.to_dict()
        result: List[JsonObject] = []
        for field in options.OPTIONS:
            item = {
                'help': field.help,
                'name': field.name,
                'title': field.name.replace('_', ' ').title(),
                'value': opts[field.name]
            }
            # pylint: disable=comparison-with-callable
            if field.name == 'mp3_editor':
                # TODO: Find a more generic solution
                item['choices'] = MP3Factory.available_editors()
                item['type'] = 'enum'
            elif field.ftype == bool:
                item['type'] = 'bool'
            elif field.ftype == int:
                item['type'] = 'int'
                item['minValue'] = field.min_value
                item['maxValue'] = field.max_value
            elif field.ftype == str:
                item['type'] = 'text'
            elif field.ftype == json.loads:
                item['type'] = 'json'
                if item['value'] is not None:
                    item['value'] = json.dumps(item['value'])
            elif isinstance(field.ftype, EnumWrapper):
                item['type'] = 'enum'
                item['choices'] = field.ftype.names()
                item['value'] = item['value'].name
            result.append(item)
        return result

    def post(self) -> Response:
        """
        Modify the current settings
        """
        if not self.is_admin():
            return jsonify_no_content(401)
        if not request.json:
            return jsonify_no_content(400)
        modified_fields: Set[str] = set()
        changes: JsonObject = {}
        for section, items in request.json.items():
            try:
                sch = self.process_section_changes(section, items)
                if section == 'app':
                    changes.update(sch)
                else:
                    changes[section] = sch
                for field in sch:
                    modified_fields.add(f'{section}.{field}')
            except ValueError as err:
                return jsonify({
                    'success': False,
                    'error': str(err)
                })
        g.current_options.update(**changes)
        return jsonify({
            'success': True,
            'changes': sorted(list(modified_fields))
        })

    def process_section_changes(self, section: str, items: JsonObject) -> JsonObject:
        """
        Process the requested changes for the given settings section
        """
        changes: JsonObject = {}
        opt_map: Dict[str, OptionField] = {}
        if section == 'app':
            opts: List[OptionField] = Options.OPTIONS
        else:
            opts = cast(ExtraOptions, getattr(g.current_options, section)).OPTIONS
        for field in opts:
            opt_map[field.name] = field
        for name, value in items.items():
            try:
                field = opt_map[name]
            except KeyError as err:
                raise ValueError(f'Invalid field {name}') from err
            if field.ftype == int:
                if value is None:
                    raise ValueError(f'Invalid None value for field {name}')
                if not isinstance(value, int):
                    raise ValueError(f'Invalid type {type(value)} for field {name}')
                if field.min_value is not None and value < field.min_value:
                    raise ValueError(
                        (f'Invalid value {value} for field {name} '+
                         f'(min={field.min_value})'))
                if field.max_value is not None and value > field.max_value:
                    raise ValueError(
                        (f'Invalid value {value} for field {name} '+
                         f'(max={field.max_value})'))
            changes[name] = value
        return changes
