from pathlib import Path


TESTDIR = Path(__file__).parent

class AppConfig:
    DEBUG = True
    SECRET_KEY =  'very secure'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600 * 24
    STATIC_FOLDER = TESTDIR / "fixtures"
    TEMPLATE_FOLDER = TESTDIR / "fixtures"
    JWT_ACCESS_TOKEN_EXPIRES = 600
