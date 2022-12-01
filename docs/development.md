# Developing MusicBingo

## GUI development
There is nothing particularly special required to develop the GUI code. You
just need to install the development libraries:

```sh
pip install -r dev-requirements.txt
```

[tox](https://pypi.org/project/tox/) is used to run the unit, type and style
checks.

```sh
tox
```

It will run checks based upon all the available installed Python
versions.

To test all supported Python versions, there is a Docker dockerfile
that will create a container with every supported Python version
installed in it and then run `tox` across all of those versions.

First time setup:

```sh
docker build -t music-bingo -f tox-dockerfile .
```

To run all of the tests:

```sh
docker run -i -t -v ${PWD}/musicbingo:/home/bingo/musicbingo music-bingo -p 2
```

Before submitting a pull request, please make sure that all tests
pass on all supported versions of Python.

## Server 
The server-side code is pure Python, using the
[Flask Framework](https://flask.palletsprojects.com/en/1.1.x/). 

For developing the HTML JavsScript application code,
[nodejs](https://nodejs.org/en/) needs to be installed. The client
code is a Redux-React app.  See [Create React App](https://create-react-app.dev/)
for more information about how to develop and test the React components.

```sh
./server.sh &
cd client
npm install
npm run start
```

If you are unable to log in, as you don't know the admin login
password, you can change it:

```sh
python -m musicbingo.models change-password admin mynewpass
```

Where `mynewpass` is the new password for the `admin` account.
