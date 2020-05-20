"""
Test user managerment server APIs
"""

import copy
from datetime import datetime, timedelta
from functools import wraps
import json
from pathlib import Path
import unittest
from unittest import mock

from flask_testing import TestCase  # type: ignore
from freezegun import freeze_time  # type: ignore

from musicbingo import models
from musicbingo.options import DatabaseOptions, Options
from musicbingo.models.db import DatabaseConnection
from musicbingo.models.group import Group
from musicbingo.models.user import User
# from musicbingo.server.routes import add_routes
from musicbingo.server.app import create_app

from .config import AppConfig

DatabaseOptions.DEFAULT_FILENAME = None
Options.INI_FILENAME = None

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        options = Options(database_provider='sqlite',
                          database_name=':memory:',
                          smtp_server='unit.test',
                          smtp_sender='noreply@unit.test',
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
        session.commit()
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
        with self.client:
            response = self.login_user('user', 'mysecret')
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertIn('accessToken', data)
            access_token = data['accessToken']
            refresh_token = data['refreshToken']
            self.assertEqual(user.pk, data['pk'])
            # check that only the refresh token has been added to the database
            tokens = dbs.query(models.Token).filter_by(user_pk=user.pk)
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
        tokens = dbs.query(models.Token).filter_by(user_pk=user.pk)
        self.assertEqual(tokens.count(), 2)
        for token in tokens:
            self.assertTrue(token.revoked)
        # check that refresh token is no longer usable
        with self.client:
            response = self.refresh_access_token(refresh_token)
            self.assertEqual(response.status_code, 401)
        models.Token.prune_database(dbs)
        tokens = dbs.query(models.Token).filter_by(user_pk=user.pk)
        self.assertEqual(tokens.count(), 2)
        frozen_time.tick(delta=timedelta(seconds=(AppConfig.JWT_ACCESS_TOKEN_EXPIRES + 1)))
        models.Token.prune_database(dbs)
        # access token should have been removed from db
        tokens = dbs.query(models.Token).filter_by(user_pk=user.pk)
        self.assertEqual(tokens.count(), 1)
        frozen_time.tick(delta=timedelta(days=1, seconds=2))
        models.Token.prune_database(dbs)
        # refresh token should have been removed from db
        tokens = dbs.query(models.Token).filter_by(user_pk=user.pk)
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
            self.assertEqual(data['success'], True)
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
        self.assertIn(reset_url, str(html))
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

if __name__ == '__main__':
    unittest.main()
