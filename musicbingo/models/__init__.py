"""
This file contains all of the database models.

"""
import copy
import io
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, TextIO, Type, cast

from sqlalchemy import create_engine, inspect, MetaData  # type: ignore

from musicbingo.options import DatabaseOptions, Options
from musicbingo.utils import flatten
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.progress import Progress

from musicbingo.models import db
from .album import Album
from .artist import Artist
from .bingoticket import BingoTicket, BingoTicketTrack
from .directory import Directory
from .game import Game
from .group import Group
from .importer import Importer
from .modelmixin import JsonObject, ModelMixin
from .session import DatabaseSession
from .song import Song
from .token import Token, TokenType
from .track import Track
from .user import User


def select_tables(req_tables: Set[str]) -> List[Type[ModelMixin]]:
    """
    convert string of table names into a list of Table classes
    """
    req_tables = {t.lower() for t in req_tables}
    sel_tables = []
    tables = [User, Album, Artist, Directory, Song, Game, Track,
              BingoTicket]
    for table in tables:
        if (table.__name__.lower() in req_tables or # type: ignore
            table.__plural__.lower() in req_tables): # type: ignore
            sel_tables.append(table)
    if (Token.__name__.lower() in req_tables or # type: ignore
        Token.__plural__.lower() in req_tables): # type: ignore
        sel_tables.append(Token)
    return sel_tables

def show_database(session: DatabaseSession,
                  req_tables: Optional[Set[str]] = None):
    """
    Display entire contents of database
    """
    tables = [User, Artist, Album, Directory, Song,
              Game, Track, BingoTicket, Token]
    if req_tables is not None:
        tables = select_tables(req_tables)
    for table in tables:
        table.show(session)

def export_database(filename: Path, options: Options,
                    progress: Progress,
                    session: DatabaseSession,
                    req_tables: Optional[Set[str]] = None) -> None:
    """
    Output entire contents of database as JSON
    """
    with filename.open('w') as output:
        export_database_to_file(output, options, progress, session, req_tables)

def export_database_to_file(output: TextIO, options: Options,
                            progress: Progress,
                            session: DatabaseSession,
                            req_tables: Optional[Set[str]]) -> None:
    """
    Output entire contents of database as JSON to specified file
    """
    log = logging.getLogger('musicbingo.models')
    output.write('{\n')
    log.info("Options")
    output.write('"Options":')  # type: ignore
    opts = options.to_dict(
        exclude={'command', 'exists', 'jsonfile', 'database', 'debug', 'game_id',
                 'title', 'mp3_editor', 'mode', 'smtp', 'secret_key', 'tables'})
    for enum in ['colour_scheme', 'page_size']:
        opts[enum] = opts[enum].name.lower()
    clips = options.clips()
    try:
        opts['clip_directory'] = cast(Path, clips).resolve().as_posix()
    except AttributeError:
        # PurePosixPath and PureWindowsPath don't have the resolve() function
        opts['clip_directory'] = clips.as_posix()
    json.dump(opts, output, indent='  ')
    output.write(',\n')
    tables = [User, Album, Artist, Directory, Song, Game, Track,
              BingoTicket]
    if req_tables is not None:
        tables = select_tables(req_tables)
    progress.num_phases = len(tables)
    for phase, table in enumerate(tables):
        progress.current_phase = phase
        log.info("%s", table.__name__)  # type: ignore
        progress.text = f'Exporting {table.__plural__}'  # type: ignore
        contents: List[JsonObject] = []
        num_items = float(table.total_items(session))
        index = 0
        for item in table.all(session):  # type: ignore
            progress.pct = 100.0 * index / num_items
            data = item.to_dict(with_collections=True)
            contents.append(data)
            index += 1
        progress.pct = 100.0
        output.write(f'"{table.__plural__}":')  # type: ignore
        json.dump(contents, output, indent='  ', default=flatten)
        if table != tables[-1]:
            output.write(',')
        output.write('\n')
    output.write('}\n')


def export_game(game_id: str, filename: Path) -> bool:
    """
    Output one game as a JSON file
    """
    with db.session_scope() as session:
        data = export_game_to_object(game_id, session)
    if data is None:
        return False
    with filename.open('w') as output:
        # pylint: disable=no-value-for-parameter
        json.dump(data, output, indent=2, default=flatten)
    return True

def export_game_to_object(game_id: str,
                          session: DatabaseSession) -> Optional[JsonObject]:
    """
    Output one game in JSON format to specified file
    """
    game = Game.get(session, id=game_id)
    if game is None:
        print(f'Failed to find game "{game_id}". Available games:')
        print([game.id for game in session.query(Game)])
        return None
    tracks: List[Track] = []
    songs: List[Song] = []
    db_dirs: Dict[int, Directory] = {}
    for track in game.tracks.order_by(Track.number):  # type: ignore
        db_dirs[track.song.directory.pk] = track.song.directory
        song = track.song.to_dict(exclude={'album', 'artist'})
        song['album'] = track.song.album.name if track.song.album is not None else ''
        song['artist'] = track.song.artist.name if track.song.artist is not None else ''
        songs.append(song)
        tracks.append(track.to_dict())
    tickets = [ticket.to_dict(with_collections=True)
               for ticket in game.bingo_tickets]  # type: ignore
    data = {
        "Games": [
            game.to_dict()
        ],
        "Directories": [item.to_dict() for item in db_dirs.values()],
        "Songs": songs,
        "Tracks": tracks,
        "BingoTickets": tickets,
    }
    return data
