import copy
import json
import unittest

from flask import Flask  # type: ignore
from flask_testing import TestCase  # type: ignore
from flask_jwt_extended import JWTManager  # type: ignore

from musicbingo import models
from musicbingo.options import Options
from musicbingo.models.db import DatabaseConnection
from musicbingo.models.group import Group
from musicbingo.models.user import User
from musicbingo.server.routes import add_routes

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        self.options = Options(database_provider='sqlite', database_name=':memory:')
        app = Flask(__name__)
        jwt = JWTManager(app)
        app.config.from_object('musicbingo.tests.config.AppConfig')
        add_routes(app, self.options)
        return app

    def setUp(self):
        DatabaseConnection.bind(self.options.database)

    def tearDown(self):
        DatabaseConnection.close()

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

class TestUserApi(BaseTestCase):
    def test_log_in_using_username(self):
        """Test log in of a registered user using username"""
        with models.db.session_scope() as dbs:
            user = User(
                username='user',
                password=User.hash_password('mysecret'),
                email='user@unit.test',
                groups_mask=Group.users.value
            )
            dbs.add(user)
        with self.client:
            response = self.login_user('user','mysecret')
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

if __name__ == '__main__':
    unittest.main()
