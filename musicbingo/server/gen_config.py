"""
A function to generate an initial config file that
allows the server to start
"""

from pathlib import Path
import secrets

TEMPLATE="""import os

BASEDIR=os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))

config = {
    'DEBUG': True,
    'SECRET_KEY': {secret},
    'PONY': {
        'provider': 'sqlite',
        'filename': os.path.join(BASEDIR, 'bingo.db3'),
        'create_db': True
    },
}

MAX_TICKETS_PER_USER = 2

admins = [ ]

options = {}
"""

def create_config_file() -> bool:
    """
    generate a config.py file
    """
    here = Path(__name__)
    filename = here / "config.py"
    if filename.exists():
        return False
    conf = TEMPLATE.format(secret=secrets.token_url_safe(32))
    with filename.open('w') as cfile:
        cfile.write(conf)
