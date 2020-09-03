#!/bin/bash

service uwsgi stop
if [ -d /var/www/music-bingo/.venv ]; then
    rm -rf /var/www/music-bingo/.venv
fi
python3 -m venv /var/www/music-bingo/.venv
source /var/www/music-bingo/.venv/bin/activate
pip-3 install --prefix /var/www/music-bingo/.venv -r /var/www/music-bingo/requirements.txt
if [ ! -f /var/www/music-bingo/bingo.ini -a -f /home/ec2-user/bingo.ini ]; then
    cp /home/ec2-user/bingo.ini /var/www/music-bingo/
fi
chown -R ec2-user:nginx /var/www/music-bingo
chmod -R g+rX /var/www/music-bingo
service uwsgi start
