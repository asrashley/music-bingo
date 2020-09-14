"""
Test user managerment server APIs
"""

import copy
import ctypes
from datetime import datetime, timedelta
from enum import IntEnum
from functools import wraps
import json
import logging
from pathlib import Path
import multiprocessing
import shutil
import tempfile
from typing import Optional
import unittest
from unittest import mock

from flask_testing import TestCase  # type: ignore
from freezegun import freeze_time  # type: ignore
import requests
from sqlalchemy import create_engine  # type: ignore

from musicbingo import models
from musicbingo.options import DatabaseOptions, Options
from musicbingo.progress import Progress
from musicbingo.models.db import DatabaseConnection
from musicbingo.models.group import Group
from musicbingo.models.importer import Importer
from musicbingo.models.modelmixin import JsonObject
from musicbingo.models.user import User
# from musicbingo.server.routes import add_routes
from musicbingo.server.app import create_app

from .config import AppConfig
from .fixture import fixture_filename
from .liveserver import LiveServerTestCase
from .test_models import ModelsUnitTest

DatabaseOptions.DEFAULT_FILENAME = None
Options.INI_FILENAME = None

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        log_format = "%(thread)d %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=log_format)
        # logging.getLogger().setLevel(logging.DEBUG)
        # logging.getLogger(models.db.__name__).setLevel(logging.DEBUG)
        options = Options(database_provider='sqlite',
                          database_name=':memory:',
                          debug=False,
                          smtp_server='unit.test',
                          smtp_sender='sender@unit.test',
                          smtp_reply_to='reply_to@unit.test',
                          smtp_username='email',
                          smtp_password='secret',
                          smtp_starttls=False)
        fixtures = Path(__file__).parent / "fixtures"
        return create_app('musicbingo.tests.config.AppConfig',
                          options,
                          static_folder=fixtures,
                          template_folder=fixtures)

    def setUp(self):
        # self.freezer = freeze_time("2020-01-02 03:04:05")
        # self.freezer.start()
        DatabaseConnection.bind(self.options().database)

    def tearDown(self):
        DatabaseConnection.close()
        # self.freezer.stop()

    def options(self):
        """
        get the Options object associated with the Flask app
        """
        return self.app.config['GAME_OPTIONS']

    @staticmethod
    def add_user(session, username, email, password, groups_mask=Group.users.value):
        """
        Add a user to database
        """
        user = User(
            username=username,
            password=User.hash_password(password),
            email=email,
            groups_mask=groups_mask,
        )
        session.add(user)
        session.flush()
        return user

    def login_user(self, username, password, rememberme=False):
        """
        Call login REST API
        """
        return self.client.post(
            '/api/user',
            data=json.dumps({
                'username': username,
                'password': password,
                'rememberme': rememberme
            }),
            content_type='application/json',
        )

    def register_user(self, username, email, password):
        """
        Call register user REST API
        """
        return self.client.put(
            '/api/user',
            data=json.dumps({
                'username': username,
                'password': password,
                'email': email,
            }),
            content_type='application/json',
        )

    def refresh_access_token(self, refresh_token):
        """
        Get a new access token using the refresh token
        """
        return self.client.post(
            '/api/refresh',
            headers={
                "Authorization": f'Bearer {refresh_token}',
            }
        )


def freeze(time_str: str):
    """
    Decorator for mocking datetime using freezegun
    """
    def wrapper(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            with freeze_time(time_str) as frozen_time:
                return func(*args, frozen_time, **kwargs)
        return decorated_function
    return wrapper


class TestUserApi(BaseTestCase):
    """
    Test user managerment server APIs
    """

    render_templates = True

    @freeze("2020-01-02 03:04:05")
    @models.db.db_session
    def test_log_in_using_username(self, frozen_time, dbs):
        """Test log in of a registered user using username"""
        self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        with self.client:
            response = self.login_user('user', 'mysecret')
            data = response.json
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertEqual(data['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', data)
            options = self.options()
            self.assertEqual(data['options']['colourScheme'], options.colour_scheme)
            self.assertEqual(data['options']['maxTickets'], options.max_tickets_per_user)
            self.assertEqual(data['options']['rows'], options.rows)
            self.assertEqual(data['options']['columns'], options.columns)
            access_token = data['accessToken']
            refresh_token = data['refreshToken']
        frozen_time.tick(delta=timedelta(seconds=(AppConfig.JWT_ACCESS_TOKEN_EXPIRES / 2)))
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
        # check that a 401 response is returned once the access token has expired
        frozen_time.tick(delta=timedelta(seconds=(AppConfig.JWT_ACCESS_TOKEN_EXPIRES / 2)))
        frozen_time.tick(delta=timedelta(seconds=1))
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(response.status_code, 401)
        with self.client:
            response = self.client.post(
                '/api/refresh',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(response.status_code, 401)
        with self.client:
            response = self.refresh_access_token(refresh_token)
            self.assert200(response)
            self.assertIn('accessToken', response.json)
            access_token = response.json['accessToken']
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            data = response.json
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertEqual(data['groups'], ['users'])

    @models.db.db_session
    def test_log_in_using_email(self, dbs):
        """Test log in of a registered user using email"""
        self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        with self.client:
            response = self.login_user('user@unit.test', 'mysecret')
            data = json.loads(response.data.decode())
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertEqual(data['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', data)
            self.assertEqual(data['options']['colourScheme'], self.options().colour_scheme)
            self.assertEqual(data['options']['maxTickets'], self.options().max_tickets_per_user)
            self.assertEqual(data['options']['rows'], self.options().rows)
            self.assertEqual(data['options']['columns'], self.options().columns)

    def test_log_in_wrong_password(self):
        """Test log in of a registered user but wrong password"""
        with models.db.session_scope() as dbs:
            self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        with self.client:
            response = self.login_user('user', 'wrong-password')
            self.assert401(response)

    def test_log_in_unknown_user(self):
        """
        Test attempt to log in with unknown user
        """
        with models.db.session_scope() as dbs:
            self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        with self.client:
            response = self.login_user('notregistered', 'mysecret')
            self.assertEqual(response.status_code, 401)

    def test_log_register_new_user(self):
        """Test creation of a new user"""
        with self.client:
            response = self.register_user('newuser', 'user@unit.test', 'mysecret')
            data = json.loads(response.data.decode())
            self.assertTrue(data['success'])
            user = data['user']
            self.assertEqual(user['username'], 'newuser')
            self.assertEqual(user['email'], 'user@unit.test')
            self.assertEqual(user['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', user)
            self.assertEqual(user['options']['colourScheme'], self.options().colour_scheme)
            self.assertEqual(user['options']['maxTickets'], self.options().max_tickets_per_user)
            self.assertEqual(user['options']['rows'], self.options().rows)
            self.assertEqual(user['options']['columns'], self.options().columns)

    def test_log_register_new_user_missing_field(self):
        """Test creation of a new user where request missing data"""
        # email address is missing
        data = {
            'username': 'newuser',
            'password': 'secure',
            'email': 'user@unit.test'
        }
        for field in ['username', 'password', 'email']:
            data2 = copy.copy(data)
            del data2[field]
            with self.client:
                response = self.client.put(
                    '/api/user',
                    data=json.dumps(data2),
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, 400)

    @freeze("2020-01-02 03:04:05")
    @models.db.db_session
    def test_logout(self, frozen_time, dbs):
        """
        Test log out of a registered user
        """
        user = self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        user_pk = user.pk
        del user
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertIn('accessToken', data)
            access_token = data['accessToken']
            refresh_token = data['refreshToken']
            self.assertEqual(user_pk, data['pk'])
            # check that only the refresh token has been added to the database
            tokens = dbs.query(models.Token).filter_by(user_pk=user_pk)
            self.assertEqual(tokens.count(), 1)
            self.assertEqual(tokens[0].token_type, models.TokenType.refresh.value)
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
        with self.client:
            response = self.client.delete(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(response.status_code, 200)
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(response.status_code, 401)
        tokens = dbs.query(models.Token).filter_by(user_pk=user_pk)
        self.assertEqual(tokens.count(), 2)
        for token in tokens:
            self.assertTrue(token.revoked)
        # check that refresh token is no longer usable
        with self.client:
            response = self.refresh_access_token(refresh_token)
            self.assertEqual(response.status_code, 401)
        models.Token.prune_database(dbs)
        tokens = dbs.query(models.Token).filter_by(user_pk=user_pk)
        self.assertEqual(tokens.count(), 2)
        frozen_time.tick(delta=timedelta(seconds=(AppConfig.JWT_ACCESS_TOKEN_EXPIRES + 1)))
        models.Token.prune_database(dbs)
        # access token should have been removed from db
        tokens = dbs.query(models.Token).filter_by(user_pk=user_pk)
        self.assertEqual(tokens.count(), 1)
        frozen_time.tick(delta=timedelta(days=1, seconds=2))
        models.Token.prune_database(dbs)
        # refresh token should have been removed from db
        tokens = dbs.query(models.Token).filter_by(user_pk=user_pk)
        self.assertEqual(tokens.count(), 0)

    @freeze("2020-01-02 03:04:05")
    @mock.patch('musicbingo.server.api.smtplib.SMTP_SSL', autospec=True)
    def test_password_reset(self, frozen_time, mock_smtp):
        """
        Test password reset of a registered user.
        It should send an email to the requested user that contains
        a reset link. The email will contain both a plain text and
        an HTML version.
        """
        with models.db.session_scope() as dbs:
            self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        with self.client:
            response = self.client.post(
                '/api/user/reset',
                data=json.dumps({
                    'email': 'user@unit.test',
                }),
                content_type='application/json',
            )
            data = response.json
            self.assertEqual(data['success'], True, data)
        smtp_opts = self.options().smtp
        mock_smtp.assert_called_once_with(smtp_opts.server, smtp_opts.port, context=mock.ANY)
        context = mock_smtp.return_value.__enter__.return_value
        context.ehlo_or_helo_if_needed.assert_called()
        context.login.assert_called_once_with(smtp_opts.username, smtp_opts.password)
        context.send_message.assert_called_once_with(mock.ANY, smtp_opts.sender, 'user@unit.test')
        args, _ = context.send_message.call_args
        message = args[0]
        self.assertTrue(message.is_multipart())
        self.assertEqual(message.get("To"), 'user@unit.test')
        self.assertEqual(message.get("From"), smtp_opts.sender)
        plain = message.get_payload(0)
        html = message.get_payload(1)
        with self.assertRaises(IndexError):
            _ = message.get_payload(2)
        self.assertEqual(plain.get_content_type(), 'text/plain')
        self.assertEqual(html.get_content_type(), 'text/html')
        token_lifetime = self.app.config['PASSWORD_RESET_TOKEN_EXPIRES']
        with models.db.session_scope() as dbs:
            user = models.User.get(dbs, email='user@unit.test')
            self.assertIsNotNone(user.reset_expires)
            self.assertIsNotNone(user.reset_token)
            self.assertEqual(user.reset_expires, datetime.now() + token_lifetime)
            reset_token = user.reset_token
        reset_url = f'http://localhost/user/reset/{reset_token}'
        self.assertIn(reset_url, str(plain))
        self.assertIn(smtp_opts.reply_to, str(plain))
        self.assertIn(reset_url, str(html))
        self.assertIn(smtp_opts.reply_to, str(html))
        frozen_time.tick(timedelta(seconds=(token_lifetime.total_seconds() - 10)))
        with self.client:
            response = self.client.post(
                '/api/user/reset',
                data=json.dumps({
                    'email': 'user@unit.test',
                    'token': reset_token,
                    'password': 'newpassword',
                    'confirmPassword': 'newpassword',
                }),
                content_type='application/json',
            )
            data = response.json
            self.assertEqual(data['success'], True)
        with models.db.session_scope() as dbs:
            user = models.User.get(dbs, email='user@unit.test')
            self.assertTrue(user.check_password('newpassword'))
            self.assertIsNone(user.reset_expires)
            self.assertIsNone(user.reset_token)


    @models.db.db_session
    def test_password_reset_missing_smtp_settings(self, dbs):
        """
        Test password reset where SMTP settings have not been provided.
        It should detect the missing setting and include it in an
        error message to the client.
        """
        self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        orig_opts = self.options().smtp.to_dict()
        smtp_settings = ['server', 'port', 'sender', 'username', 'password']
        for option in smtp_settings:
            # restore SMTP settings before test
            for opt in smtp_settings:
                setattr(self.options().smtp, opt, orig_opts[opt])
            setattr(self.options().smtp, option, None)
            with self.client:
                response = self.client.post(
                    '/api/user/reset',
                    data=json.dumps({
                        'email': 'user@unit.test',
                    }),
                    content_type='application/json',
                )
                data = response.json
                msg = f'Should fail if {option} setting is missing'
                self.assertEqual(data['success'], False, msg)
                self.assertIn('Invalid SMTP settings', data['error'], msg)

    @models.db.db_session
    @mock.patch('musicbingo.server.api.smtplib.SMTP_SSL', autospec=True)
    def test_password_reset_unknown_email_address(self, dbs, mock_smtp):
        """
        Test password reset using an unknown email address.
        It should return "success: True" to the client but not
        send an email.
        """
        self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        with self.client:
            response = self.client.post(
                '/api/user/reset',
                data=json.dumps({
                    'email': 'unknown@unit.test',
                }),
                content_type='application/json',
            )
            data = response.json
            self.assertEqual(data['success'], True)
            mock_smtp.assert_not_called()

    @freeze("2020-01-02 03:04:05")
    def test_password_reset_link_expires(self, frozen_time):
        """
        Test that password reset link stops working when token has expired
        """
        with models.db.session_scope() as dbs:
            user = self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
            user.reset_token = 'abc123'
            user.reset_expires = datetime.now() + timedelta(seconds=60)
        frozen_time.tick(delta=timedelta(seconds=61))
        with self.client:
            response = self.client.post(
                '/api/user/reset',
                data=json.dumps({
                    'email': 'user@unit.test',
                    'token': 'abc123',
                    'password': 'newpassword',
                    'confirmPassword': 'newpassword',
                }),
                content_type='application/json',
            )
            data = response.json
            self.assertEqual(data['success'], False)
        with models.db.session_scope() as dbs:
            user = models.User.get(dbs, email='user@unit.test')
            self.assertTrue(user.check_password('mysecret'))
            self.assertIsNotNone(user.reset_expires)
            self.assertIsNotNone(user.reset_token)

    def test_password_reset_link_cleared_after_login(self):
        """
        Test that password reset token is removed after successful login
        """
        with models.db.session_scope() as dbs:
            user = self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
            user.reset_token = 'abc123'
            user.reset_expires = datetime.now() + timedelta(seconds=60)
        response = self.login_user('user', 'mysecret')
        self.assert200(response)
        with models.db.session_scope() as dbs:
            user = models.User.get(dbs, email='user@unit.test')
            self.assertTrue(user.check_password('mysecret'))
            self.assertIsNone(user.reset_expires)
            self.assertIsNone(user.reset_token)

class TestListGamesApi(BaseTestCase):
    """
    Test game list server APIs
    """
    def setUp(self):
        super().setUp()
        json_filename = fixture_filename("tv-themes-v4.json")
        with models.db.session_scope() as dbs:
            imp = Importer(self.options(), dbs, Progress())
            imp.import_database(json_filename)

    @freeze("2020-04-24 03:04:05")
    def test_game_list(self, frozen_time):
        """
        Test get list of past and present games
        """
        with self.client:
            response = self.login_user('user', 'mysecret')
            access_token = response.json['accessToken']
        expected = {
            "games": [
                {
                    "pk": 1,
                    "id": "20-04-24-2",
                    "title": "TV Themes",
                    "start": "2020-04-24T18:05:44.048300Z",
                    "end": "2020-08-02T18:05:44.048300Z",
                    "options": {
                        'colour_scheme': 'blue',
                        'number_of_cards': 24,
                        'include_artist': True,
                        'columns': 5,
                        'rows': 3,
                        'backgrounds': [
                            '#daedff', '#f0f8ff', '#daedff', '#f0f8ff', '#daedff',
                            '#f0f8ff', '#daedff', '#f0f8ff', '#daedff', '#f0f8ff',
                            '#daedff', '#f0f8ff', '#daedff', '#f0f8ff', '#daedff'
                        ]
                    },
                    "userCount": 0
                }
            ],
            "past": []
        }
        with self.client:
            response = self.client.get(
                '/api/games',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            # self.maxDiff = None
            self.assertDictEqual(response.json, expected)
        frozen_time.move_to(datetime(year=2020, month=8, day=3))
        expected["past"] = expected["games"]
        expected["games"] = []
        # login required as both access token and refresh token will have expired
        with self.client:
            response = self.login_user('user', 'mysecret')
            access_token = response.json['accessToken']
        with self.client:
            response = self.client.get(
                '/api/games',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            # self.maxDiff = None
            self.assertDictEqual(response.json, expected)


class MultipartMixedParser:
    """
    Parser to a multipart/mixed stream
    """
    class State(IntEnum):
        """
        State of parsing
        """
        BOUNDARY = 0
        HEADERS = 1
        BODY = 2

    def __init__(self, boundary, source):
        self.source = source
        self.mid_boundary = b'--' + boundary
        self.end_boundary = b'--' + boundary + b'--'

    def parse(self):
        """
        Parse the stream
        """
        headers = {}
        body = []
        todo = 0
        state = self.State.BOUNDARY
        for data in self.source.iter_lines():
            if state == self.State.BOUNDARY:
                if data == b'':
                    continue
                if len(data) < len(self.mid_boundary):
                    return
                if data == self.end_boundary:
                    return
                if data != self.mid_boundary:
                    raise ValueError(b'Expected boundary: "' + self.mid_boundary +
                                     b'" but got "' + data + b'"')
                headers = {}
                state = self.State.HEADERS
            elif state == self.State.HEADERS:
                if data == b'':
                    state = self.State.BODY
                    todo = int(headers['Content-Length'], 10)
                    body = []
                    continue
                name, value = str(data, 'utf-8').split(':')
                headers[name] = value.strip()
            elif state == self.State.BODY:
                assert todo > 0
                body.append(data)
                todo -= len(data)
                if todo < 1:
                    yield b''.join(body)
                    todo = 0
                    state = self.State.BOUNDARY


class ServerTestCaseBase(LiveServerTestCase, ModelsUnitTest):
    """
    Base class for test cases that need to use a live HTTP server
    """
    LIVESERVER_TIMEOUT: int = 15
    FIXTURE: Optional[str] = "tv-themes-v5.sql"

    _temp_dir = multiprocessing.Array(ctypes.c_char, 1024)

    def create_app(self):
        log_format = "%(thread)d %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=log_format)
        # logging.getLogger().setLevel(logging.DEBUG)
        # logging.getLogger(models.db.__name__).setLevel(logging.DEBUG)
        tempdir = tempfile.mkdtemp()
        self._temp_dir.value = bytes(tempdir, 'utf-8')
        options = Options(database_provider='sqlite',
                          database_name=f'{tempdir}/bingo.db3',
                          debug=False,
                          smtp_server='unit.test',
                          smtp_sender='sender@unit.test',
                          smtp_reply_to='reply_to@unit.test',
                          smtp_username='email',
                          smtp_password='secret',
                          smtp_starttls=False)
        engine = create_engine(options.database.connection_string())
        if self.FIXTURE is not None:
            self.load_fixture(engine, self.FIXTURE)
            #json_filename = fixture_filename(self.FIXTURE)
            #with models.db.session_scope() as dbs:
            #    imp = Importer(options, dbs, Progress())
            #    imp.import_database(json_filename)
        DatabaseConnection.bind(options.database, create_tables=False,
                                engine=engine)
        fixtures = Path(__file__).parent / "fixtures"
        return create_app(AppConfig, options, static_folder=fixtures,
                          template_folder=fixtures)

    def setUp(self):
        self.session = requests.Session()

    def tearDown(self):
        self.session.close()
        self._terminate_live_server()
        DatabaseConnection.close()
        if self._temp_dir.value:
            shutil.rmtree(self._temp_dir.value)

    def login_user(self, username, password, rememberme=False):
        """
        Call login REST API
        """
        api_url = self.get_server_url()
        return self.session.post(
            f'{api_url}/api/user',
            data=json.dumps({
                'username': username,
                'password': password,
                'rememberme': rememberme
            }),
            headers={
                "content-type": 'application/json',
            }
        )

class TestImportGame(ServerTestCaseBase):
    """
    Test importing games into database
    """
    def test_import_not_admin(self):
        """
        Test import of gameTracks file when not an admin
        """
        response = self.login_user('user', 'mysecret')
        self.assertEqual(response.status_code, 200)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("gameTracks-v3.json")
        with json_filename.open('rt') as src:
            data = json.load(src)
        api_url = self.get_server_url()
        response = self.session.put(
            f'{api_url}/api/games',
            json={
                "filename": "game-20-01-02-1.json",
                "data": data
            },
            headers={
                "Authorization": f'Bearer {access_token}',
                "content-type": 'application/json',
            }
        )
        self.assertEqual(response.status_code, 401)
        # force reading of data from server
        response.raw.read()

    def test_import_v3_game(self):
        """
        Test import of a v3 gameTracks file
        """
        response = self.login_user('admin', 'adm!n')
        self.assertEqual(response.status_code, 200)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("gameTracks-v3.json")
        with json_filename.open('rt') as src:
            data = json.load(src)
        api_url = self.get_server_url()
        response = self.session.put(
            f'{api_url}/api/games',
            json={
                "filename": "game-20-01-02-1.json",
                "data": data
            },
            headers={
                "Authorization": f'Bearer {access_token}',
                "Accept": 'application/json',
                "content-type": 'application/json',
            },
            stream=True
        )
        self.assertEqual(response.status_code, 200)
        content_type = response.headers['Content-Type']
        self.assertTrue(content_type.startswith('multipart/'))
        pos = content_type.index('; boundary=')
        boundary = content_type[pos + len('; boundary='):]
        parser = MultipartMixedParser(bytes(boundary, 'utf-8'), response)
        for part in parser.parse():
            data = json.loads(part)
            if data['done']:
                expected = {
                    'done': True,
                    'errors': [],
                    'success': True,
                    'added': {
                        "User": 0,
                        "Directory": 1,
                        "Artist": 34,
                        "Song": 40,
                        "Track": 40,
                        "BingoTicket": 24,
                        "Game": 1
                    },
                    'keys': data['keys'],
                    'text': 'Import complete',
                    'pct': 100.0,
                    'phase': 6,
                    'numPhases': 7,
                }
                # print(data)
                # print(expected)
                self.assertDictEqual(data, expected)

    def test_import_not_gametracks_file(self):
        """
        Test import of a JSON file that is not a gameTracks file
        """
        response = self.login_user('admin', 'adm!n')
        self.assertEqual(response.status_code, 200)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("tv-themes-v4.json")
        with json_filename.open('rt') as src:
            data = json.load(src)
        api_url = self.get_server_url()
        response = self.session.put(
            f'{api_url}/api/games',
            json={
                "filename": "game-20-01-02-1.json",
                "data": data
            },
            headers={
                "Authorization": f'Bearer {access_token}',
                "Accept": 'application/json',
                "content-type": 'application/json',
            },
            stream=True
        )
        self.assertEqual(response.status_code, 200)
        content_type = response.headers['Content-Type']
        self.assertTrue(content_type.startswith('multipart/'))
        pos = content_type.index('; boundary=')
        boundary = content_type[pos + len('; boundary='):]
        parser = MultipartMixedParser(bytes(boundary, 'utf-8'), response)
        expected = {
            'errors': [
                'Not a valid gameTracks file',
                'data must be valid exactly by one of oneOf definition'
            ],
            'text': '',
            'pct': 100.0,
            'phase': 1,
            'numPhases': 1,
            'done': True,
            'success': False
        }
        for part in parser.parse():
            data = json.loads(part)
            if data['done']:
                # self.maxDiff = None
                self.assertDictEqual(expected, data)

class TestImportDatabase(ServerTestCaseBase):
    """
    Test importing database
    """
    FIXTURE: Optional[str] = None

    def create_app(self):
        app = super().create_app()
        with models.db.session_scope() as dbs:
            admin = User(username="admin",
                         password="$2b$12$H8xhXO1D1t74YL2Ya2s6O.Kw7jGvWQjKci1y4E7L8ZAgrFE2EAanW",
                         email="admin@music.bingo",
                         groups_mask=1073741825)
            dbs.add(admin)
            user = User(username="user",
                        password="$2b$12$CMqbfc75fgPwQYfAsUvqo.x/G7/5uqTAiKKU6/R/MS.6sfyXHmcI2",
                        email="user@unit.test",
                        groups_mask=1)
            dbs.add(user)
        return app

    def test_import_not_admin(self):
        """
        Test import of database file when not an admin
        """
        response = self.login_user('user', 'mysecret')
        self.assertEqual(response.status_code, 200)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("tv-themes-v4.json")
        with json_filename.open('rt') as src:
            data = json.load(src)
        api_url = self.get_server_url()
        response = self.session.put(
            f'{api_url}/api/database',
            json={
                "filename": "tv-themes-v4.json",
                "data": data
            },
            headers={
                "Authorization": f'Bearer {access_token}',
                "content-type": 'application/json',
            }
        )
        self.assertEqual(response.status_code, 401)
        # force reading of data from server
        response.raw.read()

    def test_import_v4_database(self):
        """
        Test import of a v4 database file
        """
        response = self.login_user('admin', 'adm!n')
        self.assertEqual(response.status_code, 200)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("tv-themes-v4.json")
        with json_filename.open('rt') as src:
            data = json.load(src)
        api_url = self.get_server_url()
        response = self.session.put(
            f'{api_url}/api/database',
            json={
                "filename": "tv-themes-v4.json",
                "data": data
            },
            headers={
                "Authorization": f'Bearer {access_token}',
                "Accept": 'application/json',
                "content-type": 'application/json',
            },
            stream=True
        )
        self.assertEqual(response.status_code, 200)
        content_type = response.headers['Content-Type']
        self.assertTrue(content_type.startswith('multipart/'))
        pos = content_type.index('; boundary=')
        boundary = content_type[pos + len('; boundary='):]
        parser = MultipartMixedParser(bytes(boundary, 'utf-8'), response)
        for part in parser.parse():
            data = json.loads(part)
            if data['done']:
                self.assertListEqual(data['errors'], [])
                self.assertEqual(data['success'], True)
                added = {
                    "User": 0,
                    "Directory": 1,
                    "Artist": 9,
                    "Song": 71,
                    "Track": 50,
                    "BingoTicket": 24,
                    "Game": 1
                }
                self.assertDictEqual(added, data['added'])

class TestExportDatabase(ServerTestCaseBase):
    """
    Test exporting database
    """
    def test_export_v5_database(self):
        """
        Test export of a v5 database file
        """
        response = self.login_user('admin', 'adm!n')
        self.assertEqual(response.status_code, 200)
        access_token = response.json()['accessToken']
        api_url = self.get_server_url()
        response = self.session.get(
            f'{api_url}/api/database',
            headers={
                "Authorization": f'Bearer {access_token}',
                "Accept": 'application/json',
            }
        )
        self.assertEqual(response.status_code, 200)
        content_type = response.headers['Content-Type']
        self.assertTrue(content_type.startswith('application/json'))
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            print(response.data)
            raise
        #with open("exported-tv-themes-v5.json", 'wt') as dst:
        #    json.dump(data, dst, indent='  ', default=utils.flatten)
        json_filename = fixture_filename("exported-tv-themes-v5.json")
        with json_filename.open('rt') as src:
            expected = json.load(src)
        admin: Optional[JsonObject] = None
        for user in data['Users']:
            if user['username'] == 'admin':
                admin = user
                break
        self.assertIsNotNone(admin)
        for user in expected['Users']:
            if user['username'] == 'admin':
                user['last_login'] = admin['last_login']
        self.maxDiff = None
        for table in ['Users', 'Artists', 'Directories', 'Songs',
                      'Games', 'Tracks', 'BingoTickets']:
            items = {}
            for item in data[table]:
                items[item['pk']] = item
            actual = []
            for item in expected[table]:
                actual.append(items[item['pk']])
            self.assertModelListEqual(actual, expected[table], table)

if __name__ == '__main__':
    unittest.main()
