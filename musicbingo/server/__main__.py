from .views import *
from .app import app

from musicbingo.models import db

if __name__ == '__main__':
    app.run(host='0.0.0.0')
