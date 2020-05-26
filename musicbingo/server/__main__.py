import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# pylint: disable=wrong-import-position
from musicbingo.server.app import create_app

def main():
    app = create_app()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
