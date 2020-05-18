import copy
from datetime import datetime, timedelta
from functools import wraps
import json
import unittest
from unittest import mock

from flask import Flask  # type: ignore
from flask_testing import TestCase  # type: ignore
from flask_jwt_extended import JWTManager  # type: ignore
from freezegun import freeze_time  # type: ignore

from musicbingo import models
from musicbingo.options import Options
from musicbingo.models.db import DatabaseConnection
from musicbingo.models.group import Group
from musicbingo.models.user import User
# from musicbingo.server.routes import add_routes
from musicbingo.server.app import create_app

from .config import AppConfig

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        self.options = Options(database_provider='sqlite', database_name=':memory:')
        return create_app('musicbingo.tests.config.AppConfig', self.options)

    def setUp(self):
        # self.freezer = freeze_time("2020-01-02 03:04:05")
        # self.freezer.start()
        DatabaseConnection.bind(self.options.database)

    def tearDown(self):
        DatabaseConnection.close()
        # self.freezer.stop()

    def login_user(self, username, password, rememberme = False):
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
    def wrapper(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            with freeze_time(time_str) as frozen_time:
                return func(*args, frozen_time, **kwargs)
        return decorated_function
    return wrapper

class TestUserApi(BaseTestCase):

    @freeze("2020-01-02 03:04:05")
    @models.db.db_session
    def test_log_in_using_username(self, frozen_time, dbs):
        """Test log in of a registered user using username"""
        user = User(
            username='user',
            password=User.hash_password('mysecret'),
            email='user@unit.test',
            groups_mask=Group.users.value
        )
        dbs.add(user)
        dbs.commit()
        with self.client:
            response = self.login_user('user','mysecret')
            data = response.json
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertEqual(data['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', data)
            self.assertEqual(data['options']['colourScheme'], self.options.colour_scheme)
            self.assertEqual(data['options']['maxTickets'], self.options.max_tickets_per_user)
            self.assertEqual(data['options']['rows'], self.options.rows)
            self.assertEqual(data['options']['columns'], self.options.columns)
            access_token = data['accessToken']
            refresh_token = data['refreshToken']
        frozen_time.tick(delta=timedelta(seconds=(AppConfig.JWT_ACCESS_TOKEN_EXPIRES/2)))
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
        frozen_time.tick(delta=timedelta(seconds=(AppConfig.JWT_ACCESS_TOKEN_EXPIRES/2)))
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
            self.assertEqual(response.status_code, 200)
            self.assertIn('accessToken', response.json)
            access_token = response.json['accessToken']
        with self.client:
            response = self.client.get(
                '/api/user',
                headers={
                    "Authorization": f'Bearer {access_token}',
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertEqual(data['groups'], ['users'])


    def test_log_in_using_email(self):
        """Test log in of a registered user using email"""
        with models.db.session_scope() as dbs:
            user = User(
                username='user',
                password=User.hash_password('mysecret'),
                email='user@unit.test',
                groups_mask=Group.users.value
            )
            dbs.add(user)
        with self.client:
            response = self.login_user('user@unit.test','mysecret')
            data = json.loads(response.data.decode())
            self.assertEqual(data['username'], 'user')
            self.assertEqual(data['email'], 'user@unit.test')
            self.assertEqual(data['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', data)
            self.assertEqual(data['options']['colourScheme'], self.options.colour_scheme)
            self.assertEqual(data['options']['maxTickets'], self.options.max_tickets_per_user)
            self.assertEqual(data['options']['rows'], self.options.rows)
            self.assertEqual(data['options']['columns'], self.options.columns)

    def test_log_in_wrong_password(self):
        """Test log in of a registered user but wrong password"""
        with models.db.session_scope() as dbs:
            user = User(
                username='user',
                password=User.hash_password('mysecret'),
                email='user@unit.test',
                groups_mask=Group.users.value
            )
            dbs.add(user)
        with self.client:
            response = self.login_user('user','wrong-password')
            self.assertEqual(response.status_code, 401)

    def test_log_in_unknown_user(self):
        """Test attempt to log in with unknown user"""
        with models.db.session_scope() as dbs:
            user = User(
                username='user',
                password=User.hash_password('mysecret'),
                email='user@unit.test',
                groups_mask=Group.users.value
            )
            dbs.add(user)
        with self.client:
            response = self.login_user('notregistered', 'mysecret')
            self.assertEqual(response.status_code, 401)

    def test_log_register_new_user(self):
        """Test creation of a new user"""
        with self.client:
            response = self.register_user('newuser', 'user@unit.test','mysecret')
            data = json.loads(response.data.decode())
            self.assertTrue(data['success'])
            user = data['user']
            self.assertEqual(user['username'], 'newuser')
            self.assertEqual(user['email'], 'user@unit.test')
            self.assertEqual(user['groups'], ['users'])
            self.assertIn('accessToken', data)
            self.assertIn('refreshToken', data)
            self.assertIn('options', user)
            self.assertEqual(user['options']['colourScheme'], self.options.colour_scheme)
            self.assertEqual(user['options']['maxTickets'], self.options.max_tickets_per_user)
            self.assertEqual(user['options']['rows'], self.options.rows)
            self.assertEqual(user['options']['columns'], self.options.columns)

    def test_log_register_new_user_missing_field(self):
        """Test creation of a new user where request missing data"""
        # email address is missing
        data={
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
        user = User(
            username='user',
            password=User.hash_password('mysecret'),
            email='user@unit.test',
            groups_mask=Group.users.value
        )
        dbs.add(user)
        dbs.commit()
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

if __name__ == '__main__':
    unittest.main()
