![Music Bingo Logo](docs/images/logo_banner.png?raw=true)

# Music Bingo

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

## Application

This repository contains a local GUI application (written in Python and
Tcl/Tk) that allows song clips to be created, bingo games to be generated
and music quizzes to be generated.

![Image of GUI application](docs/images/app.png?raw=true)

See [app.md](docs/app.md) for full details of installing and using the Music
Bingo app.

## Server

This repository contains an HTML JavaScript application (written in Python and
JavaScript). This application is split into two parts:

* an HTTP server that provides a JSON REST API
* an HTML JavsScript application that can be run from any web browser

The server provides access to a database that contains information about which
users are allowed to access the server and to previously generated Bingo games.
To allow multiple people to play bingo on-line, this server needs to be accessible
on the Internet. Typically this is achieved by deploying the server to a cloud
service such as Azure or AWS.

The HTML JavsScript application uses the JSON REST API to access bingo games
stored in the database on the server. It allows multiple users to play musical
bingo together, and also provides the ability to administer the database, such as
importing previously created games or modifying the list of authorised users.

![Image of HTML application](docs/images/server_login.png?raw=true)

See [server.md](docs/server.md) for full details of installing and using the Music
Bingo server and HTML JavaScript application.

## Directory Layout

    .
    |-- Bingo Games
    |-- Clips
    |-- Extra-Files
    |-- NewClips
    |-- client
    |-- musicbingo

The "Bingo Games" directory is used to output each generated game. The name
of the directory is specified in the "Game ID" text box of MusicBingo.py.

The "Clips" directory is the default location where MusicBingo.py looks for
clips that can be selected when making a game. It is recommended to create a
sub-directory inside the Clips directory for each theme, as MusicBingo.py will
reflect that directory structure in the "Available Songs" window, making it
easier to select the clips you want.

For example:

    |-- Clips
    |   |-- 2000s
    |   |-- American
    |   |-- Christmas
    |   |-- Disco
    |   |-- Disney
    |   |-- Eighties
    |   |-- Fifties
    |   |-- House
    |   |-- Groove, Hip Hop & RnB
    |   |-- Ibiza
    |   |-- James Bond
    |   |-- Motown
    |   |-- Movies
    |   |-- Musicals
    |   |-- New Romantics
    |   |-- Number 1s
    |   |-- Pride
    |   |-- Rock
    |   |-- Seventies
    |   |-- Sing
    |   |-- Sixties
    |   |-- Soul
    |   `-- TV Themes


The "NewClips" directory is used to store clips that are generated using
MusicBingo.py.

The "client" directory contains the HTML JavaScript application. See
[docs/server.md] for full details of installing and using the HTML
Bingo application.

The "musicbingo" directory contains the Python source code used by both
the GUI application and the HTTP server application.

## Database

Both the application and the server use a database to store the list of
available clips and details of each generated game. By default they use
a file called "bingo.db3" which contains an sqlite database.

For more information for alternative database storage methods see
[database.md](docs/database.md).

## Development

There is nothing particularly special required to develop the GUI code. You
just need to install tox [https://pypi.org/project/tox/] and check that
your changes doesn't reduce the 100% code quality score.

For developing the server code, [nodejs](https://nodejs.org/en/) needs to
be installed. The server-side code is pure Python, using the
[Flask Framework](https://flask.palletsprojects.com/en/1.1.x/). The client
code is a Redux-React app.  See [Create React App](https://create-react-app.dev/)
for more information about how to develop and test the React components.
