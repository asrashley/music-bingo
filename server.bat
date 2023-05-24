@echo off
set LC_ALL=C.UTF-8
set LANG=C.UTF-8
set FLASK_APP=musicbingo.server.app

flask run --host=0.0.0.0 --debug
