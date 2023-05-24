#!/bin/sh
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=musicbingo.server.app

flask run --host=0.0.0.0 --debug
#python -m musicbingo.server
#watchgod musicbingo.server.__main__.main
