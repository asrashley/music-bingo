"""
This file contains all of the database models.

"""
import copy
import io
import json
import logging
from pathlib import Path
import typing

from sqlalchemy import create_engine, inspect, MetaData  # type: ignore

from musicbingo.options import DatabaseOptions, Options
from musicbingo.utils import flatten
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.progress import Progress

from musicbingo.models import db
from .bingoticket import BingoTicket, BingoTicketTrack
from .directory import Directory
from .game import Game
from .group import Group
from .importer import Importer
from .modelmixin import JsonObject
from .session import DatabaseSession
from .song import Song
from .token import Token, TokenType
from .track import Track
from .user import User


@db.db_session
def show_database(session: DatabaseSession):
    """
    Display entire contents of database
    """
    for table in [User, Game, BingoTicket, Track, Directory, Song]:
        table.show(session)


def export_database(filename: Path, progress: Progress) -> None:
    """
    Output entire contents of database as JSON
    """
    with filename.open('w') as output:
        # pylint: disable=no-value-for-parameter
        export_database_to_file(output, progress)


@db.db_session
def export_database_to_file(output: typing.TextIO, progress: Progress,
                            session: DatabaseSession) -> None:
    """
    Output entire contents of database as JSON to specified file
    """
    log = logging.getLogger('musicbingo.models')
    output.write('{\n')
    tables = [User, Game, BingoTicket, Track, Directory, Song]
    progress.num_phases = len(tables)
    for phase, table in enumerate(tables):
        progress.current_phase = phase
        log.info("%s", table.__name__)  # type: ignore
        progress.text = f'Exporting {table.__plural__}'  # type: ignore
        contents = []
        num_items = float(table.total_items(session))
        index = 0
        for item in table.all(session):  # type: ignore
            progress.pct = 100.0 * index / num_items
            data = item.to_dict(with_collections=True)
            contents.append(flatten(data))  # type: ignore
            index += 1
        progress.pct = 100.0
        output.write(f'"{table.__plural__}":')  # type: ignore
        json.dump(contents, output, indent='  ')
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
                          session: DatabaseSession) -> typing.Optional[JsonObject]:
    """
    Output one game in JSON format to specified file
    """
    game = Game.get(session, id=game_id)
    if game is None:
        print(f'Failed to find game "{game_id}". Available games:')
        print([game.id for game in session.query(Game)])
        return None
    tracks: typing.List[Track] = []
    songs: typing.List[Song] = []
    db_dirs: typing.Dict[int, Directory] = {}
    for track in game.tracks.order_by(Track.number):  # type: ignore
        db_dirs[track.song.directory.pk] = track.song.directory
        songs.append(track.song.to_dict())
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
