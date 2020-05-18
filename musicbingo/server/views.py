import datetime
import os
from pathlib import Path
import tempfile
from typing import Dict, Optional

from flask import (  # type: ignore
    Flask, request, render_template, redirect, make_response,
    flash, session, url_for, send_from_directory, jsonify,
    current_app,
)
from flask.views import MethodView  # type: ignore
import jinja2

from flask_jwt_extended import (  # type: ignore
    jwt_required, jwt_optional,
    get_jwt_identity, current_user
)

from musicbingo import models, utils
from musicbingo.docgen.factory import DocumentFactory
from musicbingo.generator import BingoTicket, GameGenerator
from musicbingo.options import Options
from musicbingo.mp3 import MP3Factory
from musicbingo.progress import Progress
from musicbingo.song import Song
from musicbingo.track import Track

from .decorators import (
    db_session, uses_database, get_game,
    get_ticket, current_game, current_ticket,
    get_options, current_options,
)

class ServeStaticFileView(MethodView):
    def get(self, path, folder=None):
        basedir = os.path.join(current_app.config['STATIC_FOLDER'], "..")
        if folder is not None:
            basedir = os.path.join(basedir, folder)
        return send_from_directory(basedir, path)


class SpaIndexView(MethodView):
    def get(self, path=None):
        return render_template('index.html')


class DownloadTicketView(MethodView):
    decorators = [get_ticket, get_game, jwt_required, uses_database]

    def get(self, **kwargs):
        if current_ticket.user != current_user and not current_user.has_permission(
                models.Group.host):
            response = make_response('Not authorised', 401)
            return response
        opts = current_options.to_dict()
        if current_game.options:
            opts.update(current_game.options)
        options = Options(**opts)
        card = BingoTicket(options, fingerprint=current_ticket.fingerprint,
                           number=current_ticket.number)
        for track in current_ticket.tracks_in_order():
            song = Song(parent=None, ref_id=track.pk,
                        **track.song.to_dict(exclude=['pk', 'directory_pk']))
            card.tracks.append(Track(prime=track.prime, song=song,
                                     start_time=track.start_time))

        with tempfile.TemporaryDirectory() as tmpdirname:
            filename = self.create_pdf(options, card, Path(tmpdirname))
            with filename.open('rb') as src:
                data = src.read()
        headers = {
            'Content-Disposition': f'attachment; filename="{filename.name}"',
            'Content-Type': 'application/pdf',
            'Content-Length': str(len(data)),
        }
        return make_response((data, 200, headers))

    def create_pdf(self, options: Options, ticket: BingoTicket, tmpdirname: Path) -> Path:
        assert len(ticket.tracks) == (options.rows * options.columns)
        filename = tmpdirname / f'Game {current_game.id} ticket {ticket.number}.pdf'  # type: ignore
        mp3editor = MP3Factory.create_editor(options.mp3_engine)
        pdf = DocumentFactory.create_generator('pdf')
        d_opts = options.to_dict()
        if current_game.options:
            d_opts.update(current_game.options)
        opts = Options(**d_opts)
        opts.checkbox = True
        opts.title = current_game.title  # type: ignore
        opts.game_id = current_game.id  # type: ignore
        gen = GameGenerator(opts, mp3editor, pdf, Progress())
        gen.render_bingo_ticket(str(filename), ticket)
        return filename
