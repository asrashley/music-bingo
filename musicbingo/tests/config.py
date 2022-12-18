"""
Flask config for unit tests
"""
# pylint: disable=duplicate-code
from datetime import timedelta
from pathlib import Path


TESTDIR = Path(__file__).parent


class AppConfig:
    """
    Flask config for unit tests
    """

    DEBUG = True
    ENV = 'development'
    TESTING = True
    SECRET_KEY = 'very secure'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    EXPLAIN_TEMPLATE_LOADING = True
    JWT_ACCESS_TOKEN_EXPIRES = 900
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)
    REMEMBER_ME_REFRESH_TOKEN_EXPIRES = timedelta(days=180)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    PASSWORD_RESET_TOKEN_EXPIRES = timedelta(days=7)
    LIVESERVER_TIMEOUT = 10
