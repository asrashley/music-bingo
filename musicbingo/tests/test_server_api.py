"""
Test user managerment server APIs
"""
from collections.abc import Iterable
import copy
import ctypes
from datetime import datetime, timedelta
from functools import wraps
import json
import logging
from multiprocessing.sharedctypes import SynchronizedString
from pathlib import Path
import multiprocessing
import re
import shutil
import tempfile
from typing import ClassVar, List, Optional, Set, cast
import unittest
from unittest import mock

from flask import Flask
from flask.testing import FlaskClient
from flask_testing import TestCase  # type: ignore
from freezegun import freeze_time  # type: ignore
import requests
from sqlalchemy import Engine, create_engine
import tinycss2  # type: ignore
from werkzeug.test import TestResponse

from musicbingo import models
from musicbingo.options import DatabaseOptions, Options
from musicbingo.options.extra import ExtraOptions
from musicbingo.json_object import JsonObject
from musicbingo.palette import Palette
from musicbingo.progress import Progress
from musicbingo.models.db import DatabaseConnection
from musicbingo.models.group import Group
from musicbingo.models.importer import Importer
from musicbingo.models.user import User
from musicbingo.server.app import create_app
from musicbingo.server.api import SettingsApi

from .config import AppConfig
from .fixture import fixture_filename
from .liveserver import LiveServerTestCase
from .multipart_parser import MultipartMixedParser
from .test_models import ModelsUnitTest

DatabaseOptions.DEFAULT_FILENAME = None
Options.INI_FILENAME = None

class ServerBaseTestCase(TestCase):
    """ Base Tests """

    client: FlaskClient

    def create_app(self):
        log_format = "%(thread)d %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=log_format)
        #logging.getLogger().setLevel(logging.DEBUG)
        #logging.getLogger(models.db.__name__).setLevel(logging.DEBUG)
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
        templates = Path(__file__).parent / ".." / "server" / "templates"
        return create_app('musicbingo.tests.config.AppConfig',
                          options,
                          static_folder=fixtures.resolve(),
                          template_folder=templates.resolve())

    def setUp(self) -> None:
        # self.freezer = freeze_time("2020-01-02 03:04:05")
        # self.freezer.start()
        DatabaseConnection.bind(self.options().database)

    def tearDown(self) -> None:
        DatabaseConnection.close()
        # self.freezer.stop()

    def options(self) -> Options:
        """
        get the Options object associated with the Flask app
        """
        return self.app.config['GAME_OPTIONS']

    @staticmethod
    def add_user(session, username, email, password, groups_mask=Group.USERS.value) -> User:
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

    def login_user(self, username: str, password: str, rememberme: bool = False) -> TestResponse:
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

    def logout_user(self, access_token: str):
        """
        Call logout REST API
        """
        return self.client.delete(
            '/api/user',
            headers={
                "Authorization": f'Bearer {access_token}',
            }
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

    # pylint: disable=invalid-name
    def assertNoCache(self, response):
        """
        Assert that "do not cache" headers were set in response
        """
        self.assertEqual(response.cache_control.max_age, 0)
        self.assertTrue(response.cache_control.no_cache)
        self.assertTrue(response.cache_control.no_store)
        self.assertTrue(response.cache_control.must_revalidate)

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


class TestUserApi(ServerBaseTestCase):
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
            self.assertNoCache(response)
            data = response.json
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertEqual(data['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', data)
            options = self.options()
            self.assertEqual(data['options']['colourScheme'],
                             options.colour_scheme.name.lower())
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
            self.assertNoCache(response)
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
            self.assertNoCache(response)
        with self.client:
            response = self.client.post(
                '/api/refresh',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(response.status_code, 401)
            self.assertNoCache(response)
        with self.client:
            response = self.refresh_access_token(refresh_token)
            self.assert200(response)
            self.assertNoCache(response)
            self.assertIn('accessToken', response.json)
            # pylint: disable=no-member
            access_token = response.json['accessToken']
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            data = response.json
            options = self.options()
            expected = {
                'pk': 1,
                'username': 'user',
                'email': 'user@unit.test',
                'groups': ['users'],
                'options': {
                    'colourScheme': options.colour_scheme.name.lower(),
                    'colourSchemes': [name.lower() for name in Palette.names()],
                    'columns': options.columns,
                    'maxTickets': options.max_tickets_per_user,
                    'rows': options.rows
                },
                'last_login': '2020-01-02T03:04:05Z',
                'reset_expires': None,
                'reset_token': None
            }
            self.maxDiff = None # pylint: disable=attribute-defined-outside-init
            self.assertEqual(data, expected)

    @models.db.db_session
    def test_log_in_using_email(self, dbs):
        """Test log in of a registered user using email"""
        self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        with self.client:
            response = self.login_user('user@unit.test', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            data = json.loads(response.data.decode())
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertEqual(data['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', data)
            self.assertEqual(data['options']['colourScheme'],
                             self.options().colour_scheme.name.lower())
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
            self.assertNoCache(response)

    def test_log_in_unknown_user(self):
        """
        Test attempt to log in with unknown user
        """
        with models.db.session_scope() as dbs:
            self.add_user(dbs, 'user', 'user@unit.test', 'mysecret')
        with self.client:
            response = self.login_user('notregistered', 'mysecret')
            self.assertEqual(response.status_code, 401)
            self.assertNoCache(response)

    def test_log_register_new_user(self):
        """Test creation of a new user"""
        with self.client:
            response = self.register_user('newuser', 'user@unit.test', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            data = json.loads(response.data.decode())
            self.assertTrue(data['success'])
            user = data['user']
            self.assertEqual(user['username'], 'newuser')
            self.assertEqual(user['email'], 'user@unit.test')
            self.assertEqual(user['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', user)
            self.assertEqual(user['options']['colourScheme'],
                             self.options().colour_scheme.name.lower())
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
                self.assert400(response)
                self.assertNoCache(response)

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
            self.assert200(response)
            self.assertNoCache(response)
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
            self.assertEqual(tokens[0].token_type, models.TokenType.REFRESH.value)
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
        with self.client:
            response = self.client.delete(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(response.status_code, 401)
            self.assertNoCache(response)
        tokens = dbs.query(models.Token).filter_by(user_pk=user_pk)
        self.assertEqual(tokens.count(), 2)
        for token in tokens:
            self.assertTrue(token.revoked)
        # check that refresh token is no longer usable
        with self.client:
            response = self.refresh_access_token(refresh_token)
            self.assertEqual(response.status_code, 401)
            self.assertNoCache(response)
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
            self.assert200(response)
            self.assertNoCache(response)
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
            self.assert200(response)
            self.assertNoCache(response)
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
                self.assert200(response)
                self.assertNoCache(response)
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
            self.assert200(response)
            self.assertNoCache(response)
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
            self.assert200(response)
            self.assertNoCache(response)
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
        self.assertNoCache(response)
        with models.db.session_scope() as dbs:
            user = models.User.get(dbs, email='user@unit.test')
            self.assertTrue(user.check_password('mysecret'))
            self.assertIsNone(user.reset_expires)
            self.assertIsNone(user.reset_token)

class TestListGamesApi(ServerBaseTestCase):
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
            self.assert200(response)
            self.assertNoCache(response)
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
                        'cards_per_page': 3,
                        'checkbox': False,
                        'colour_scheme': 'blue',
                        'number_of_cards': 24,
                        'include_artist': True,
                        'columns': 5,
                        'rows': 3,
                        'page_size': 'A4',
                        'sort_order': 'interleave',
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
            self.assert200(response)
            self.assertNoCache(response)
            self.maxDiff = None # pylint: disable=attribute-defined-outside-init
            self.assertDictEqual(response.json, expected)
        frozen_time.move_to(datetime(year=2020, month=8, day=3))
        expected["past"] = expected["games"]
        expected["games"] = []
        # login required as both access token and refresh token will have expired
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            access_token = response.json['accessToken']
        with self.client:
            response = self.client.get(
                '/api/games',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            self.maxDiff = None # pylint: disable=attribute-defined-outside-init
            self.assertDictEqual(response.json, expected)


class TestQuerySongsApi(ServerBaseTestCase, ModelsUnitTest):
    """
    Test song list and query API
    """
    def setUp(self) -> None:
        engine: Engine = create_engine(self.options().database.connection_string())
        self.load_fixture(engine, "tv-themes-v5.sql")
        DatabaseConnection.bind(
            self.options().database, create_tables=False, engine=engine)

    def test_song_query(self) -> None:
        """
        Test get list of matching songs
        """
        with self.client:
            response: TestResponse = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            data = cast(JsonObject, response.json)
            assert data is not None
            access_token: str = data['accessToken']
        expected: list[JsonObject] = [{
            'pk': 1,
            'filename': '01-25- Ghostbusters.mp3',
            'title': 'Ghostbusters',
            'duration': 30016,
            'channels': 2,
            'sample_rate': 44100,
            'sample_width': 16,
            'bitrate': 256,
            'uuid': 'urn:uuid:7dcc81f2-5dbe-5973-9556-494d94cf0f77',
            'directory': 1,
            'artist': 'Ray Parker Jr',
            'album': '100 Hits 80s Essentials'
        }, {
            'pk': 24,
            'filename': '18 Blockbusters.mp3',
            'title': 'Blockbusters',
            'duration': 30016,
            'channels': 2,
            'sample_rate': 44100,
            'sample_width': 16,
            'bitrate': 256,
            'uuid': 'urn:uuid:ba5a0f66-e319-5dd3-ab3e-00f0ccd61cc8',
            'directory': 1,
            'artist': 'Gordon Lorenz Orchestra',
            'album': 'Your 101 All Time Favourite TV Themes'
        }]
        with self.client:
            response = self.client.get(
                '/api/song?q=bus',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            # self.maxDiff = None
            self.assertListEqual(response.json, expected)
        expected = [{
            'pk': 14,
            'filename': '10 The Six Million Dollar Man.mp3',
            'title': 'The Six Million Dollar Man',
            'duration': 30016,
            'channels': 2,
            'sample_rate': 44100,
            'sample_width': 16,
            'bitrate': 256,
            'uuid': 'urn:uuid:2b566ec7-f11b-5d96-82ad-f1bc6cb9b485',
            'directory': 1,
            'artist': 'Dusty Springfield',
            'album': 'All-Time Top 100 TV Themes [Disc 2]'
        }]
        with self.client:
            response = self.client.get(
                '/api/song?q=spring',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            self.assertListEqual(response.json, expected)


class TestDownloadTicketView(ServerBaseTestCase, ModelsUnitTest):
    """
    Test downloading PDF of a ticket
    """
    def setUp(self):
        sql_filename = fixture_filename("tv-themes-v5.sql")
        engine = create_engine(self.options().database.connection_string())
        self.load_fixture(engine, sql_filename)
        DatabaseConnection.bind(self.options().database, create_tables=False,
                                engine=engine)

    def test_download_claimed_ticket(self):
        """
        Test get a PDF of a ticket that has been claimed by the user
        """
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            access_token = response.json['accessToken']
        # assign ticket 23 to this user
        with models.db.session_scope() as dbs:
            game = models.Game.get(dbs, id='20-04-24-2')
            self.assertIsNotNone(game)
            game_pk = game.pk
            ticket = models.BingoTicket.get(dbs, game=game, number=23)
            ticket_pk = ticket.pk
            self.assertIsNotNone(ticket)
            user = models.User.get(dbs, username='user')
            self.assertIsNotNone(user)
            ticket.user = user
            dbs.flush()
        with self.client:
            response = self.client.get(
                f'/api/game/{game_pk}/ticket/ticket-{ticket_pk}.pdf',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            self.assertEqual(response.headers['Content-Type'], 'application/pdf')
            self.assertEqual(response.headers['Content-Disposition'],
                             'attachment; filename="Game 20-04-24-2 ticket 23.pdf"')

    def test_download_unclaimed_ticket(self):
        """
        Test that trying to get a PDF of a ticket that has not been claimed by the user
        fails.
        """
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            access_token = response.json['accessToken']
        with self.client:
            response = self.client.get(
                '/api/game/1/ticket/ticket-21.pdf',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert401(response)

    def test_host_download_ticket(self):
        """
        Test that a host can download any ticket
        """
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            access_token = response.json['accessToken']
        with models.db.session_scope() as dbs:
            user = models.User.get(dbs, username='user')
            self.assertIsNotNone(user)
            user.set_groups(['users', 'hosts'])
        with self.client:
            response = self.client.get(
                '/api/game/1/ticket/ticket-21.pdf',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            self.assertEqual(response.headers['Content-Type'], 'application/pdf')
            self.assertEqual(response.headers['Content-Disposition'],
                             'attachment; filename="Game 20-04-24-2 ticket 23.pdf"')


class LiveServerTestCaseWithModels(LiveServerTestCase, ModelsUnitTest):
    """
    Base class for test cases that need to use a live HTTP server
    """
    FIXTURE: ClassVar[Optional[str]] = "tv-themes-v5.sql"

    _temp_dir: SynchronizedString = multiprocessing.Array(ctypes.c_char, 1024)

    def create_app(self) -> Flask:
        log_format = "%(thread)d %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=log_format)
        # logging.getLogger().setLevel(logging.DEBUG)
        # logging.getLogger(models.db.__name__).setLevel(logging.DEBUG)
        tempdir = tempfile.mkdtemp()
        self._temp_dir.value = bytes(tempdir, 'utf-8')  # type: ignore
        options = Options(database_provider='sqlite',
                          database_name=f'{tempdir}/bingo.db3',
                          debug=False,
                          smtp_server='unit.test',
                          smtp_sender='sender@unit.test',
                          smtp_reply_to='reply_to@unit.test',
                          smtp_username='email',
                          smtp_password='secret',
                          smtp_starttls=False)
        engine: Engine = create_engine(options.database.connection_string())
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

    def setUp(self) -> None:
        self.session = requests.Session()

    def tearDown(self) -> None:
        self.session.close()
        self._terminate_live_server()
        DatabaseConnection.close()
        if self._temp_dir.value:  # type: ignore
            shutil.rmtree(self._temp_dir.value)  # type: ignore

    def create_test_users(self) -> None:
        """
        Add two users into the database for use in other tests
        """
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

    def login_user(
            self,
            username: str,
            password: str,
            rememberme: bool = False
            ) -> requests.Response:
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

class TestImportGame(LiveServerTestCaseWithModels):
    """
    Test importing games into database
    """
    def test_import_not_admin(self):
        """
        Test import of gameTracks file when not an admin
        """
        response = self.login_user('user', 'mysecret')
        self.assert200(response)
        self.assertNoCache(response)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("gameTracks-v3.json")
        with json_filename.open('rt', encoding='utf-8') as src:
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
        self.assertNoCache(response)
        # force reading of data from server
        response.raw.read()

    def test_import_v3_game(self):
        """
        Test import of a v3 gameTracks file
        """
        response = self.login_user('admin', 'adm!n')
        self.assert200(response)
        self.assertNoCache(response)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("gameTracks-v3.json")
        with json_filename.open('rt', encoding='utf-8') as src:
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
        self.assert200(response)
        self.assertNoCache(response)
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
                        "Directory": 2,
                        "Album": 1,
                        "Artist": 34,
                        "Song": 40,
                        "Track": 40,
                        "BingoTicket": 24,
                        "Game": 1
                    },
                    'keys': data['keys'],
                    'text': 'Import complete',
                    'pct': 100.0,
                    'phase': 7,
                    'numPhases': 8,
                }
                # print(data)
                # print(expected)
                self.assertDictEqual(data, expected)

    def test_import_not_gametracks_file(self):
        """
        Test import of a JSON file that is not a gameTracks file
        """
        response = self.login_user('admin', 'adm!n')
        self.assert200(response)
        self.assertNoCache(response)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("tv-themes-v4.json")
        with json_filename.open('rt', encoding='utf-8') as src:
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
        self.assert200(response)
        self.assertNoCache(response)
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
                self.assertIn('errors', data)
                self.assertEqual(data['errors'][0], expected['errors'][0])
                # avoid making assumptions about the exact text output from the
                # fastjson library
                expected['errors'] = data['errors']
                self.assertDictEqual(expected, data)

class TestImportDatabase(LiveServerTestCaseWithModels):
    """
    Test importing database
    """
    FIXTURE: ClassVar[Optional[str]] = None

    def create_app(self):
        app = super().create_app()
        self.create_test_users()
        return app

    def test_import_not_admin(self):
        """
        Test import of database file when not an admin
        """
        response = self.login_user('user', 'mysecret')
        self.assert200(response)
        self.assertNoCache(response)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("tv-themes-v4.json")
        with json_filename.open('rt', encoding='utf-8') as src:
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
        self.assertNoCache(response)
        # force reading of data from server
        response.raw.read()

    def test_import_v4_database(self):
        """
        Test import of a v4 database file
        """
        response = self.login_user('admin', 'adm!n')
        self.assert200(response)
        self.assertNoCache(response)
        access_token = response.json()['accessToken']
        json_filename = fixture_filename("tv-themes-v4.json")
        with json_filename.open('rt', encoding='utf-8') as src:
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
        self.assert200(response)
        self.assertNoCache(response)
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
                    "Album": 5,
                    "Artist": 9,
                    "Song": 71,
                    "Track": 50,
                    "BingoTicket": 24,
                    "Game": 1
                }
                self.assertDictEqual(added, data['added'])

class TestExportDatabase(LiveServerTestCaseWithModels):
    """
    Test exporting database
    """
    def test_export_v5_database(self) -> None:
        """
        Test export of a v5 database file
        """
        response = self.login_user('admin', 'adm!n')
        self.assert200(response)
        self.assertNoCache(response)
        access_token: str = response.json()['accessToken']
        api_url: str = self.get_server_url()
        response = self.session.get(
            f'{api_url}/api/database',
            headers={
                "Authorization": f'Bearer {access_token}',
                "Accept": 'application/json',
            }
        )
        self.assert200(response)
        self.assertNoCache(response)
        content_type = response.headers['Content-Type']
        self.assertTrue(content_type.startswith('application/json'))
        try:
            data : JsonObject = response.json()
        except json.decoder.JSONDecodeError:
            print(response.text)
            raise
        #with open("exported-tv-themes-v5.json", 'wt') as dst:
        #    json.dump(data, dst, indent='  ', default=utils.flatten)
        json_filename = fixture_filename("exported-tv-themes-v5.json")
        with json_filename.open('rt', encoding='utf-8') as src:
            expected = json.load(src)
        admin: Optional[JsonObject] = None
        for user in cast(List[JsonObject], data['Users']):
            if user['username'] == 'admin':
                admin = user
                break
        self.assertIsNotNone(admin)
        for user in cast(List[JsonObject], expected['Users']):
            if user['username'] == 'admin':
                user['last_login'] = cast(JsonObject, admin)['last_login']
        # self.maxDiff = None
        for table in ['Users', 'Artists', 'Directories', 'Songs',
                      'Games', 'Tracks', 'BingoTickets']:
            items = {}
            for item in data[table]:
                items[item['pk']] = item
            actual = []
            for item in expected[table]:
                actual.append(items[item['pk']])
            self.assertModelListEqual(actual, expected[table], table)

class TestSettingsApi(ServerBaseTestCase):
    """
    Test settings server APIs
    """
    def setUp(self) -> None:
        super().setUp()
        json_filename = fixture_filename("tv-themes-v4.json")
        with models.db.session_scope() as dbs:
            imp = Importer(self.options(), dbs, Progress())
            imp.import_database(json_filename)

    def test_translate_options(self) -> None:
        """
        Test translating options to JSON
        """
        class TestOptions(DatabaseOptions):
            """"
            Version of DatabaseOptions that doesn't try to load environment variables
            """
            def load_environment_settings(self) -> None:
                """
                Check environment for database settings
                """
                return

        db_opts = TestOptions(database_name="bingo.db3", database_provider="sqlite")
        expected: List[JsonObject] = [{
            "help": "Timeout (in seconds) when connecting to database",
            "name": "connect_timeout",
            "title": "Connect Timeout",
            "value": None,
            "type": "int",
            "minValue": 1,
            "maxValue": 3600
        }, {
            "help": "Create database if not found (sqlite only)",
            "name": "create_db",
            "title": "Create Db",
            "value": True,
            "type": "bool"
        }, {
            "help": "Database driver",
            "name": "driver",
            "title": "Driver",
            "value": None,
            "type": "text"
        }, {
            "help": "Database name (or filename for sqlite)",
            "name": "name",
            "title": "Name",
            "value": "bingo.db3",
            "type": "text"
        }, {
            "help": "Hostname of database server",
            "name": "host",
            "title": "Host",
            "value": None,
            "type": "text"
        }, {
            "help": "Password for connecting to database",
            "name": "passwd",
            "title": "Passwd",
            "value": None,
            "type": "text"
        }, {
            "help": "Port to use to connect to database",
            "name": "port",
            "title": "Port",
            "value": None,
            "type": "int",
            "minValue": 1,
            "maxValue": 65535
        }, {
            "help": "Database provider (sqlite, mysql) [%(default)s]",
            "name": "provider",
            "title": "Provider",
            "value": "sqlite",
            "type": "text"
        }, {
            "help": "TLS options",
            "name": "ssl",
            "title": "Ssl",
            "value": None,
            "type": "json"
        }, {
            "help": "Username for connecting to database",
            "name": "user",
            "title": "User",
            "value": None,
            "type": "text"
        }]
        actual = SettingsApi.translate_options(db_opts)
        self.assertListEqual(expected, actual)

    def test_get_settings(self) -> None:
        """
        Test get current settings
        """
        opts = self.options()
        # check request without bearer token only returns privacy policy
        with self.client:
            response: TestResponse = self.client.get('/api/settings')
            self.assert200(response)
            self.assertNoCache(response)
            expected = {
                'privacy': SettingsApi.translate_options(opts.privacy),
            }
            self.assertDictEqual(response.json, expected)
        # check request for non-admin user
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            data: JsonObject = cast(JsonObject, response.json)
            self.assertIsNotNone(data)
            self.assertIn('accessToken', data)
            access_token: str = data['accessToken']
            response = self.client.get('/api/settings')
            self.assert200(response)
            self.assertNoCache(response)
            expected = {
                'privacy': SettingsApi.translate_options(opts.privacy),
            }
            self.assertDictEqual(response.json, expected)
            self.logout_user(access_token)
        with self.client:
            response = self.login_user('admin', 'adm!n')
            self.assert200(response)
            self.assertNoCache(response)
            access_token = cast(JsonObject, response.json)['accessToken']
        expected = {
            'app': SettingsApi.translate_options(opts),
        }
        for ext_cls in opts.EXTRA_OPTIONS:
            ext_opts = cast(ExtraOptions,
                            getattr(opts, ext_cls.LONG_PREFIX))
            expected[ext_cls.LONG_PREFIX] = SettingsApi.translate_options(ext_opts)
        with self.client:
            response = self.client.get(
                '/api/settings',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            self.maxDiff = None # pylint: disable=attribute-defined-outside-init
            self.assertDictEqual(response.json, expected)

    def test_modify_settings(self) -> None:
        """
        Test modify current settings
        """
        before = self.options().to_dict()
        changes: JsonObject = {
            'app': {
                'bitrate': 128,
                'colour_scheme': 'PRIDE',
                'doc_per_page': True,
                'game_name_template': 'bingo-{game_id}.json',
                'max_tickets_per_user': 4,
            },
            'smtp': {
                'port': 123,
            },
            'database': {
                'driver': 'dbDriver',
            },
            'privacy': {
                'ico': 'https://ico.url',
            },
        }
        # check request without bearer token is rejected
        with self.client:
            response: TestResponse = self.client.post(
                '/api/settings',
                data=json.dumps(changes),
                content_type='application/json',
            )
            self.assert401(response)
            self.assertNoCache(response)
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            access_token: str = cast(JsonObject, response.json)['accessToken']
        # check request for non-admin user is rejected
        with self.client:
            response = self.client.post(
                '/api/settings',
                data=json.dumps(changes),
                headers={
                    "Authorization": f'Bearer {access_token}',
                },
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 401)
            self.logout_user(access_token)
        with self.client:
            response = self.login_user('admin', 'adm!n')
            self.assert200(response)
            self.assertNoCache(response)
            access_token = cast(JsonObject, response.json)['accessToken']
        # check request for admin user works correctly
        with self.client:
            response = self.client.post(
                '/api/settings',
                data=json.dumps(changes),
                headers={
                    "Authorization": f'Bearer {access_token}',
                },
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 200)
            expected_response = {
                'success': True,
                'changes': [
                    'app.bitrate',
                    'app.colour_scheme',
                    'app.doc_per_page',
                    'app.game_name_template',
                    'app.max_tickets_per_user',
                    'database.driver',
                    'privacy.ico',
                    'smtp.port',
                ]
            }
            self.assertDictEqual(response.json, expected_response)
        opts = self.options().to_dict()
        changes['app']['colour_scheme'] = Palette.from_string(changes['app']['colour_scheme'])
        for name, value in changes['app'].items():
            self.assertEqual(opts[name], value)
        self.maxDiff = None # pylint: disable=attribute-defined-outside-init
        for name, value in before.items():
            if name in changes['app']:
                continue
            if name in Options.EXTRA_OPTIONS_NAMES:
                continue
            self.assertEqual(value, opts[name])
        for section in Options.EXTRA_OPTIONS_NAMES:
            for name, value in changes[section].items():
                self.assertEqual(opts[section][name], value)
            for name, value in before[section].items():
                if name in changes[section]:
                    continue
                self.assertEqual(value, opts[section][name])

class TestDirectoryApi(ServerBaseTestCase, ModelsUnitTest):
    """
    Test directory server APIs
    """

    def setUp(self):
        sql_filename = fixture_filename("tv-themes-v5.sql")
        engine = create_engine(self.options().database.connection_string())
        self.load_fixture(engine, sql_filename)
        DatabaseConnection.bind(self.options().database, create_tables=False,
                                engine=engine)

    @mock.patch.object(Path, 'exists')
    def test_list_all_directories(self, mock_exists) -> None:
        """
        Test that directory API returns list of all directories
        """
        mock_exists.return_value = False
        expected: list[dict] = []
        with models.db.session_scope() as dbs:
            for mdir in cast(Iterable[models.Directory], models.Directory.all(dbs)):
                item = mdir.to_dict(with_collections=True)
                item['exists'] = Path(mdir.name).exists()
                expected.append(item)

        with self.client:
            response: TestResponse = self.client.get(
                '/api/directory',
            )
            self.assert401(response)
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            access_token: str = cast(JsonObject, response.json)['accessToken']
        with self.client:
            response = self.client.get(
                '/api/directory',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert401(response)
            self.logout_user(access_token)
        with self.client:
            response = self.login_user('admin', 'adm!n')
            self.assert200(response)
            self.assertNoCache(response)
            access_token = cast(JsonObject, response.json)['accessToken']
        with self.client:
            response = self.client.get(
                '/api/directory',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert200(response)
            self.assertNoCache(response)
            self.assertListEqual(expected, response.json)

    @mock.patch.object(Path, 'exists')
    def test_directory_detail(self, mock_exists) -> None:
        """
        test that directory detail API returns information about
        every song within a directory
        """
        mock_exists.return_value = False
        dir_pks: list[int] = []
        with models.db.session_scope() as dbs:
            for m_dir in cast(Iterable[models.Directory], models.Directory.all(dbs)):
                dir_pks.append(m_dir.pk)
        self.assertGreaterThan(len(dir_pks), 0)
        with self.client:
            response = self.client.get(f'/api/directory/{dir_pks[0]}')
            self.assert401(response)
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assert200(response)
            self.assertNoCache(response)
            access_token: str = cast(JsonObject, response.json)['accessToken']
            response = self.client.get(
                f'/api/directory/{dir_pks[0]}',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assert401(response)
            self.logout_user(access_token)

        with self.client:
            response = self.login_user('admin', 'adm!n')
            self.assert200(response)
            self.assertNoCache(response)
            access_token = cast(JsonObject, response.json)['accessToken']
            self.assert200(response)
            for dir_pk in dir_pks:
                with models.db.session_scope() as dbs:
                    mdir: models.Directory | None = cast(
                        models.Directory | None, models.Directory.get(dbs, pk=dir_pk))
                    assert mdir is not None
                    expected: JsonObject = mdir.to_dict(with_collections=True, exclude={'songs'})
                    expected['songs'] = []
                    expected['exists'] = False
                    for song in mdir.songs:
                        item = song.to_dict(exclude={'artist', 'album'}, with_collections=False)
                        item['artist'] = song.artist.name if song.artist is not None else ''
                        item['album'] = song.album.name if song.album is not None else ''
                        item['exists'] = False
                        expected['songs'].append(item)
                response = self.client.get(
                    f'/api/directory/{dir_pk}',
                    headers={
                        "Authorization": f'Bearer {access_token}',
                    }
                )
                self.assert200(response)
                actual: JsonObject | None = response.json
                assert actual is not None
                self.assertDictEqual(expected, actual)


class TestCssApi(ServerBaseTestCase):
    """
    Test CSS API
    """
    def test_get_themes_css(self) -> None:
        """
        Test getting the themes.css file and that it matches Palette
        """
        with self.client:
            response = self.client.get('/api/css/themes.css')
            self.assert200(response)
        charset_re = re.compile(r'charset=([^ ;$]+)')
        match = charset_re.search(response.headers['Content-Type'])
        self.assertIsNotNone(match)
        assert match is not None # tells mypy that value cannot be None
        rules, _ = tinycss2.parse_stylesheet_bytes(
            css_bytes=response.get_data(),
            protocol_encoding=match.group(1))
        found: Set[str] = set()
        for rule in rules:
            if rule.type == 'whitespace':
                continue
            for item in rule.prelude:
                if not isinstance(item, tinycss2.ast.IdentToken):
                    continue
                if not item.value.endswith(r'-theme'):
                    continue
                theme = item.value[:-len(r'-theme')].upper()
                self.assertIn(theme, Palette.names())
                # TODO: add check that RGB values match entries in Palette
                found.add(theme)
        for name in Palette.names():
            self.assertIn(name, found, f'Missing style entry for {name}')


if __name__ == '__main__':
    unittest.main()
