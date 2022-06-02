"""
Flask views used by server
"""

import os
from pathlib import Path
import tempfile

from flask import (  # type: ignore
    render_template, make_response,
    send_from_directory,
    current_app,
)
from flask.views import MethodView  # type: ignore

from flask_jwt_extended import (  # type: ignore
    jwt_required,
    current_user
)

from musicbingo import models
from musicbingo.docgen.factory import DocumentFactory
from musicbingo.generator import BingoTicket, GameGenerator
from musicbingo.options import Options
from musicbingo.mp3 import MP3Factory
from musicbingo.progress import Progress
from musicbingo.song import Song
from musicbingo.track import Track

from .decorators import (
    uses_database, db_session, get_game,
    get_ticket, current_game, current_ticket,
    get_options, current_options,
)


class ServeStaticFileView(MethodView):
    """
    Serves files from the static folder.
    Used to serve files such as CSS and JavaScript files.
    """
    def get(self, path, folder=None):
        """
        serve static file
        """
        basedir = os.path.join(current_app.config['STATIC_FOLDER'], "..")
        if folder is not None:
            basedir = os.path.join(basedir, folder)
        return send_from_directory(basedir, path)


class SpaIndexView(MethodView):
    """
    Serves the index HTML page
    """
    # pylint: disable=unused-argument
    def get(self, path=None):
        """
        Serve the index HTML page
        """
        return render_template('index.html')


class DownloadTicketView(MethodView):
    """
    Allows a Bingo ticket to be downloaded as a PDF file
    """
    decorators = [get_ticket, get_game, get_options, jwt_required(), uses_database]

    # pylint: disable=unused-argument
    def get(self, **kwargs):
        """
        get a Bingo ticket as a PDF file
        """
        if current_ticket.user != current_user and not current_user.has_permission(
                models.Group.HOSTS):
            response = make_response('Not authorised', 401)
            return response
        opts = current_game.game_options(current_options)
        options = Options(**opts)
        options.checkbox = True
        options.title = current_game.title  # type: ignore
        options.game_id = current_game.id  # type: ignore
        card = BingoTicket(columns=options.columns, palette=options.palette,
                           fingerprint=current_ticket.fingerprint,
                           number=current_ticket.number)
        for track in current_ticket.get_tracks(db_session):
            trk = track.song.to_dict(exclude={'pk', 'directory_pk', 'artist', 'album'})
            trk['artist'] = track.song.artist.name if track.song.artist is not None else ''
            trk['album'] = track.song.album.name if track.song.album is not None else ''
            song = Song(parent=None, ref_id=track.pk, **trk)
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

    @staticmethod
    def create_pdf(options: Options, ticket: BingoTicket, tmpdirname: Path) -> Path:
        """
        Create a PDF file in the specified temporary directory
        """
        assert len(ticket.tracks) == (options.rows * options.columns)
        filename = tmpdirname / f'Game {current_game.id} ticket {ticket.number}.pdf'  # type: ignore
        mp3editor = MP3Factory.create_editor('mock')
        pdf = DocumentFactory.create_generator('pdf')
        gen = GameGenerator(options, mp3editor, pdf, Progress())
        gen.render_bingo_ticket(str(filename), ticket)
        return filename
