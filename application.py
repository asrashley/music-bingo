import os, sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from musicbingo.server.app import create_app

app = create_app()
