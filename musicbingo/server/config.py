from datetime import timedelta
import os

srcdir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.dirname(os.path.dirname(srcdir))
STATIC_FOLDER = os.path.abspath(os.path.join(basedir, "client", "build", "static"))
TEMPLATE_FOLDER = os.path.abspath(os.path.join(basedir, "client", "build"))

AppConfig = {
    'DEBUG': False,
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'PERMANENT_SESSION_LIFETIME': 3600 * 24,
    'STATIC_FOLDER': STATIC_FOLDER,
    'TEMPLATE_FOLDER': TEMPLATE_FOLDER,
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=15),
    'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=1),
    'REMEMBER_ME_REFRESH_TOKEN_EXPIRES': timedelta(days=180),
    'JWT_BLACKLIST_ENABLED': True,
    'JWT_BLACKLIST_TOKEN_CHECKS': ['access', 'refresh'],
}
