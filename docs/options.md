# musicbingo command-line options

## musicbingo client options

The musicbingo client application is started using

```sh
python -m musicbingo
```

Additional options can be specified to modify the application. For
example:

```sh
python -m musicbingo --bitrate 384 --crossfade 250
```

### --games-dest `directory_name`

Bingo Game destination directory

### --game-id `id`

The identifier to use when generating a bingo game.

### --title `title`

Game Title

### --clip-start `mm`:`ss`

Clip start time, in minutes and seconds

### ---clip-duration `seconds`

Clip duration, in seconds

### --bingo

Start in Bingo game generation mode

### --clip

Start in clip generation mode

### --quiz

Start in music quiz generation mode

### --create-index

Create a song index file

### --bitrate `kbits_per_second`

Audio bitrate (KBit/sec) to use when creating clips and Bingo games

### --crossfade `milliseconds`

The amount to overlap each clip and "swoosh" during Bingo game
generation, in milliseconds. If set to zero, overlap is disabled.

### --mp3-editor `engine_name`

The MP3 engine to use for generating clips and creating Bingo games.

Currently the following engines are supported:

* pydub
* ffmpeg

# musicbingo options used by both client and server

### --game-name-template `id_template`

Template to use when creating game IDs. This option using the Python
templating syntax. The default is `Game-{game_id}`

### --game-info-filename `filename_template`

Template to used when generating game info JSON files. This option
using the Python templating syntax. The default is `game-{game_id}.json`

### --clip-directory `directory_name`

The directory containing clips. The default is `Clips`

### --new-clips-dest `directory_name`

The directory to use for new clips. The default is `NewClips`

### --colour-scheme `scheme_name`

The colour scheme to use when generating a Bingo game. The current
list of available colour schemes is:

* blue
* cyan
* green
* grey
* magenta
* orange
* pink
* pride
* purple
* red
* yellow

### --number-of-cards `number`

Number of cards to generate for a Bingo game

### --no-artist

If the `--no_artist` is provided, the artist names will be excluded
from Bingo cards.

### --ticket-order

By default, tickets are not placed in sequential order in the output
PDF file. When `--ticket_order` is specified, tickets are placed
sequentially in the PDF file.

### --columns `number`

Number of columns per Bingo ticket (between 3 and 7).

### --rows `number`

Number of rows per Bingo ticket (between 3 and 5).

### --checkbox

Adds a checkbox to each Bingo ticket cell in the PDF output. This is
useful when someone wishes to use the Bingo ticket on the computer or
smartphone without having to print the ticket.

### --cards-per-page `number`

Number of Bingo cards per page (0=auto).

### --doc-per-page

Put each page in its own PDF document

### --debug

Enable debuging messages

## Database Connection Options

### --db-connect-timeout `seconds`

Timeout (in seconds) when connecting to database before connection
is aborted.

Example:

```sh
--db-connect_timeout 30
```

### --db-create-db

Create the database if not found. Only applicable to sqlite

### --db-driver `driver`

The database driver to use. Some database providers (e.g. Microsoft
SQL Server) can be used with a variety of database drivers. Most
database providers do not need this option.

Example:

```sh
--db-driver "ODBC Driver 17 for SQL Server"
```

### --db-name `name`

The name of the database. When using sqlite, this will be the filename
of the database file.

Example:

```sh
--db-name bingo.db3
```

### --db-host `hostname`

Hostname of database server. Not required when using sqlite.

### --db-passwd `password`

The password to when when connecting to the database. Not required
when using sqlite.

### --db-port `port`

The TCP port to use to connect to the database.

Example when using MYSQL:

```sh
--db-port 3306
```

### --db-provider `engine_name`

Name of database engine. See [SQLAlchemy Supported
Databases](https://docs.sqlalchemy.org/en/13/core/engines.html) for
list of supported database types. These include:

* [postgresql](https://docs.sqlalchemy.org/en/13/dialects/postgresql.html)
* [mysql](https://docs.sqlalchemy.org/en/13/dialects/mysql.html)
* [oracle](https://docs.sqlalchemy.org/en/13/dialects/oracle.html)
* [mssql+pyodbc](https://docs.sqlalchemy.org/en/13/dialects/mssql.html)
* [mssql+pymssql](https://docs.sqlalchemy.org/en/13/dialects/mssql.html)
* [sqlite](https://docs.sqlalchemy.org/en/13/dialects/sqlite.html)

### --db-ssl `tsl_options_json`

When connecting to a database using TLS, some database connections
need additional TLS options to be provided. The `--db-ssl` option must
contain a JSON string of TLS options.

Example:

```sh
--db-ssl '{"ssl_mode":"preferred"}'
```

### --db-user `username`

The Username to use when connecting to the database

Example:

```sh
--db-user bingo
```

## musicbingo server options

### --no-create-superuser

Don't create a super user account if a blank database is detected.

### --max-tickets-per-user `number`

The maximum number tickets each user is allowed to claim per game.

## Email server connection options

To allow password reset emails to be sent, the musicbingo server needs
to be able to connect to an SMTP server to send emails.

### --smtp-port `port`

The TCP port of the SMTP server. The default port is 25

### --smtp-server `hostname`

THe hostname of the SMTP server

### --smtp-sender `email_address`

The email address to use for sending

Example:

```sh
--smtp-sender noreply@musicbingo.example.domain
```

### --smtp-reply-to `email_address`

The email address to use as the "reply to" address

### --smtp-username `username`

The username to use to authenticate when connecting to the SMTP
server.

### --smtp-password `password`

The password to use to authenticate when connecting to the SMTP
  server.

### --smtp-starttls

Normally the connection to the SMTP server will use a TLS connection
(typically to port 465) to connect to the SMTP server. If the
`--smtp-starttls` option is provided, a connection to the unprotected
TCP port (typically port 25) is used. Once the TCP connection is open,
the `STARTTLS` command is used to upgrade the connection to be
encrypted.

## Privacy policy options

The musicbingo web application provides a page describing the privacy
policy of the site. The privacy policy options allows configuring the
company name, address etc that is included in the privacy policy page.

### --privacy-name

Comapny name

### --privacy-email

Comapny email address

### --privacy-address

Comapny postal address

### --privacy-data-center

The location of the data center used to store the database.

### --privacy-ico

The HTTP or HTTPS location of the information commissioner in the
country where the company is based.

Example:

```sh
--privacy-ico https://ico.org.uk/
```
