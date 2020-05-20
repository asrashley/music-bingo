from datetime import timedelta
import os

AppConfig = {
    'DEBUG': False,
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'PERMANENT_SESSION_LIFETIME': 3600 * 24,
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=15),
    'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=1),
    'REMEMBER_ME_REFRESH_TOKEN_EXPIRES': timedelta(days=180),
    'JWT_BLACKLIST_ENABLED': True,
    'JWT_BLACKLIST_TOKEN_CHECKS': ['access', 'refresh'],
    'PASSWORD_RESET_TOKEN_EXPIRES': timedelta(days=7),
}
