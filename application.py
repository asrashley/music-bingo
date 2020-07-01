"""
Entry point for Musical Bingo server for WSGI and uWSGI environments
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# pylint: disable=wrong-import-position
from musicbingo.server.app import create_app

app = create_app()
