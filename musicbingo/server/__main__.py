
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))


from musicbingo.server.app import app

def main():
    app.run(host='0.0.0.0')
    
if __name__ == '__main__':
    main()
