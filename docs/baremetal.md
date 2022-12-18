# "Bare metal" installation of music bingo

This walk-through uses
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) to run the
Python server code and [nginx](https://www.nginx.com/) to provide
the "front of house" HTTP server that serves all of the static files
and proxies requests to the server API.

## Installing HTTP Server

MusicBingo is written in [Python 3](https://www.python.org/). It requires
Python v3.6 or higher. It is recommended to install the 64bit version if your
operating system is 64bit. If the 32bit version of Python is used, you will
find that the application will run out of memory at about 40 clips in a game.

Check if [PIP](https://pypi.org/project/pip/) has been installed:

    pip3 help

If this says command not found, you will need to install PIP. See
[PIP install instructions](https://pip.pypa.io/en/stable/installing/). Make
sure to use Python v3 when installing PIP, otherwise it will install PIP into
the Python v2 installation directory.

If you still get a "file not found" or "not recognized as an internal or
external command" error for pip, you might need to add it to your PATH.

To avoid the Python libraries used by MusicBingo conflicting with other Python
libraries installed on your computer, it is recommended to use a virtual
environment for running MusicBingo.

As a one-time step, create a directory that contains the virtual Python
environment (in this example called "virt"):

    python -m venv virt

Before installing any libraries and before each time you want to run the app,
active the virtual environment.

    . ./virt/bin/activate

Note that this only activates in the current Unix shell / Windows command
prompt. You need to run the activate script every time you start a new
shell / command prompt.

Install the required Python libraries:

    pip3 install -r requirements.txt

## Running HTTP Server

Try running the server locally:

    python -m musicbingo.server

The server should start up:

    * Serving Flask app "musicbingo.server.app" (lazy loading)
    * Environment: development
    * Debug mode: on
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: 123-456-450
    * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

The server can be accessed on port 5000
[http://localhost:5000/](http://localhost:5000/).

![Server login page](images/server_login.png?raw=true)

You can now log into the admin account with the credentials:

Username | Password
---------|---------
admin | changeme

If there any bingo games in the database, they will show up in either
the "Now Playing" page or the "Previous Games" page.

When generating a Bingo game using the [GUI application](app.md) it will
create a JSON file in a directory of the "Bingo Games" directory. This JSON
file can be imported into the server using the "Import Game" button which
is available from the "Now Playing", "Previous Games" and "admin" pages.

## Deploying HTTP Server

To allow multiple people to play bingo on-line, this server needs to be accessible
on the Internet. Typically this is achieved by deploying the server to a cloud
service such as Azure or AWS.

### "Bare Metal" deployment
To run the server on a local or remote conventional Linux or Windows operating
system.

Install [UWSGI](https://uwsgi-docs.readthedocs.io/en/latest/)

```sh
sudo pip3 install -g uwsgi
```

Install [nginx](https://www.nginx.com/) (Debian based systems)

```sh
sudo apt install -y nginx
```

Install nginx (Fedora, CentOS based systems)

```sh
sudo yum install -y nginx
```

When deploying to a server, you will probably want to use something better than
sqlite to store the database. See [database.md](database.md) for information on how
to use one of the supported databases.

Create a UWSGI site file (typically /etc/uwsgi/sites/bingo.ini) that
tells uwsgi the settings for this Python application:

    [uwsgi]
    project = music-bingo
    uid = nginx
    base = /var/www
    chdir = %(base)/%(project)
    home = %(base)/%(project)
    virtualenv = %(base)/%(project)/.venv
    module = application:app
    master = true
    processes = 3
    socket = /run/uwsgi/%(project).sock
    chown-socket = %(uid):nginx
    chmod-socket = 666
    vacuum = true
    enable-threads = true

The above example assumes that your Unix distribution has used the
user "nginx" to run nginx and that /var/www is the HTML root directory.

Build the HTML JavaScript application and then copy the musicbingo and
client directories to /var/www/music-bingo:

```sh
cd client
npm run build
cd ..
tar xzvf musicbingo-prod.tar.gz -C /var/www/music-bingo
```

Create the Python virtual environment that will be used by the server:

```sh
cd /var/www/music-bingo
python3 -m venv .venv
. ./.venv/bin/activate
pip install -r requirements.txt
deactivate
```

The uwsgi server can now be tested:

```sh
uwsgi --http localhost:8123 --module application:app --enable-threads --virtualenv .venv
```

The uwsgi server should now respond to HTTP requests on port 8123:

```sh
curl http://localhost:8123/
```

If that works, kill the uwsgi process and now try starting the UWSGI
server using the bingo.ini site file:

```sh
uwsgi --emperor /etc/uwsgi/sites
```

This should cause a Unix socket /run/uwsgi/music-bingo.sock to be
created and there should not be any error messages.

To make the uwsgi service start at boot, a service file is needed.

### /etc/systemd/system/uwsgi.service

    [Unit]
    Description=uWSGI Emperor service

    [Service]
    ExecStartPre=/bin/bash -c 'mkdir -p /run/uwsgi; chown nginx:nginx /run/uwsgi'
    ExecStart=/usr/local/bin/uwsgi --emperor /etc/uwsgi/sites
    Restart=always
    KillSignal=SIGQUIT
    Type=notify
    NotifyAccess=all

    [Install]
    WantedBy=multi-user.target

To enable this service file:

```sh
systemctl enable uwsgi.service
```

You now need an nginx configuration file that will serve all the
static files and uses `/run/uwsgi/music-bingo.sock` to access the
JSON API from the uwsgi server.

This example assumes the unix distribution you are using has an
`/etc/nginx/sites-available/` directory to store the nginx config
files. Some distributions use the directory `/etc/nginx/default.d`
to store their nginx configuration files.

### /etc/nginx/sites-available/music-bingo

    location / {
        root /var/www/music-bingo/client/build;
        add_header Cache-Control "public, max-age=2678400";
        try_files $uri $uri/ /index.html;
    }
    location /api {
        include uwsgi_params;
        add_header Cache-Control "no-store";
        uwsgi_pass unix:/run/uwsgi/music-bingo.sock;
        uwsgi_buffering off;
    }

This configuration file needs to be enabled

```sh
sudo ln -s /etc/nginx/sites-available/music-bingo /etc/nginx/sites-enabled/
```

Check that the nginx configuration is correct

```sh
nginx -t
```

If the file is valid, nginx can be restarted.

```sh
sudo service nginx restart
```

This should now be a fully working service, using nginx to serve the
static files and the Python server application to provide the JSON
API.

To enable HTTPS support, install [Let's
encrypt](https://letsencrypt.org/) support using [Certbot](https://certbot.eff.org/).

Debian based systems:

```sh
sudo apt install -y certbot python-certbot-nginx
sudo certbot --nginx
```

Fedora, CentOS based systems:

```sh
sudo yum install -y certbot python2-certbot-nginx
sudo certbot --nginx
```
