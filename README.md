Music Bingo
===========
Music Bingo is a variation on normal bingo where the numbers are replaced
with songs which the players must listen out for. This program allows
users to generate their own games of Music Bingo using their own music
clips.

This is a fork of the original code, which is available here:

    https://davidwhite478.github.io/portfolio/

It contains an app that can be run on your local computer, which allows
Bingo games and music quizzes to be created. It also allows clips to be
created from sections of songs.

It also contains a server that provides an HTML JavsScript application
that can be run from any web browser. This web app allows multiple people
to play Music Bingo together on-line.

Application
===========
See  [docs/app.md] for full details of installing and using the Music
Bingo app.

Installation
------------
MusicBingo is written in Python 3 [https://www.python.org/]. It requires
Python v3.6 or higher. It is recommended to install the 64bit version if your
operating system is 64bit. If the 32bit version of Python is used, you will
find that the application might run out of memory at about 40 clips in a game.

As a one-time step, create a directory that contains the virtual Python
environment (in this example called "virt"):

    python3 -m venv virt

Before installing any libraries and before each time you want to run the app,
activate the virtual environment.

On Unix:

    . ./virt/bin/activate

On Windows:

    virt\Scripts\activate

Install the Python libraries used by the app:

    pip3 install -r requirements.txt

Install ffmpeg [https://www.ffmpeg.org/] and make sure the ffmpeg executable is
in your PATH.

    ffmpeg -version

If you get a "file not found" or "not recognized as an internal or external
command" error for ffmpeg, you need to add it to your PATH.

Database
========
Both the application and the server use a database to store the list of
available clips and details of each generated game. By default they use
a file called "bingo.db3" which contains an sqlite database.

Other databases can be used, such as mariadb, mysql or SQL server. Any
database engine that is supported by [https://docs.sqlalchemy.org/en/13/]
can be used.

The simplest way to change which database engine is used is to edit
the "bingo.ini" file and look for the [database] section

    [database]
    provider = sqlite
    name = C:\Users\Alex\source\music-bingo\bingo.db3
    create_db = True
    ssl = null

The "provider" settings is the database engine to use. See
[https://docs.sqlalchemy.org/en/13/core/engines.html] for more information
on possible engines.

An example of using mysql:

    [database]
    provider = mysql
    host = localhost
    name = bingo
    create_db = True
    user = bingouser
    passwd = mysecret

You will also need to install the Python mysql driver:

    pip install PyMySQL

An example of using SQL server:

    [database]
    provider = mssql+pyodbc
    host = localhost
    name = bingo
    create_db = True
    user = bingouser
    passwd = mysecret
    driver = SQL Server Native Client 11.0

This needs the Python ODBC driver:

    pip install pyodbc


Development
===========
There is nothing particularly special required to develop the GUI code. You
just need to install tox [https://pypi.org/project/tox/] and check that
your changes doesn't reduce the 100% code quality score.

For developing the server code, [nodejs](https://nodejs.org/en/) needs to
be installed. The server-side code is pure Python, using the
[Flask Framework](https://flask.palletsprojects.com/en/1.1.x/). The client
code is a Redux-React app.  See [Create React App](https://create-react-app.dev/)
for more information about how to develop and test the React components.
