from musicbingo.server.views import *
from musicbingo.server.app import app

from musicbingo.models import db

def main():
    app.run(host='0.0.0.0')
    
if __name__ == '__main__':
    main()
