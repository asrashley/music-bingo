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
As a one-time step, create a directory that contains the virtual Python
environment (in this example called "virt"):

    python -m venv virt

Before installing any libraries and before each time you want to run the app,
active the virtual environment.

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

Running the application
-----------------------
Start the MusicBingo App

    python -m musicbingo

It will scan all of the clips in the "Clips" directory and show them in the
"Available Songs" window. You can use the "Add Selected Songs" and "Add 5 Random
Songs" buttons to add songs to the "Songs In This Game" window. For each Bingo
game you need at least 30 songs, ideally more than 40 songs.

Pressing the "Generate Bingo Game" will take the songs listed in the
"Songs In This Game" window, shuffle them and generate one MP3 file the
combines all of these clips. It will put a "5, 4, 3, 2, 1" count at the
beginning and a "swoosh" interstitial between clips.

After it has generated the MP3 file it will generate the Bingo cards, a track
listing and a list of when each card will win. All three of these are generated
as PDF files.

The PDF files and the MP3 file will be placed into a sub-directory of the
"Bingo Games" directory.


Database
========
Both the application and the server use a database to store the list of
available clips and details of each generated game. By default they use
a local file "bingo.db3" which contains an sqlite database.

Other databases can be used, such as mysql or SQL server. Any database
engine that is supported by [https://docs.sqlalchemy.org/en/13/] can be
used.

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
