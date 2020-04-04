#!/bin/sh
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_ENV=development
export FLASK_APP=musicbingo.server.app:app
#flask run --host=0.0.0.0
python -m musicbingo.server
