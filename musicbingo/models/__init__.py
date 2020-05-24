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
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.models import db
from musicbingo.models.bingoticket import BingoTicket
from musicbingo.models.game import Game
from musicbingo.models.group import Group
from musicbingo.models.importer import Importer
from musicbingo.models.modelmixin import JsonObject
from musicbingo.models.user import User
from musicbingo.models.directory import Directory
from musicbingo.models.song import Song
from musicbingo.models.token import Token, TokenType
from musicbingo.models.track import Track
from musicbingo.utils import flatten


@db.db_session
def show_database(session):
    """
    Display entire contents of database
    """
    for table in [User, Game, BingoTicket, Track, Directory, Song]:
        table.show(session)


def export_database(filename: Path) -> None:
    """
    Output entire contents of database as JSON
    """
    with filename.open('w') as output:
        export_database_to_file(output)


@db.db_session
def export_database_to_file(output: typing.TextIO, session) -> None:
    """
    Output entire contents of database as JSON to specified file
    """
    log = logging.getLogger('musicbingo.models')
    output.write('{\n')
    tables = [User, Game, BingoTicket, Track, Directory, Song]
    for table in tables:
        log.info("%s", table.__name__)  # type: ignore
        contents = []
        for item in table.all(session):  # type: ignore
            data = item.to_dict(with_collections=True)
            contents.append(flatten(data))  # type: ignore
        output.write(f'"{table.__plural__}":')  # type: ignore
        json.dump(contents, output, indent='  ')
        comma = ','
        if table != tables[-1]:
            output.write(',')
        output.write('\n')
    output.write('}\n')


def export_game(game_id: str, filename: Path) -> None:
    """
    Output one game as a JSON file
    """
    with filename.open('w') as output:
        export_game_to_file(game_id, output)


@db.db_session
def export_game_to_file(game_id: str, output: typing.TextIO, session) -> bool:
    """
    Output one game in JSON format to specified file
    """
    game = Game.get(session, id=game_id)
    if game is None:
        print(f'Failed to find game "{game_id}". Available games:')
        print([game.id for game in Game.select()])
        return False
    tracks = []
    for track in game.tracks.order_by(Track.number):  # type: ignore
        item = track.song.to_dict()
        item.update(track.to_dict())
        tracks.append(item)
    tickets = [ticket.to_dict(with_collections=True)
               for ticket in game.bingo_tickets]  # type: ignore
    data = {
        "Games": [
            game.to_dict(with_collections=True)
        ],
        "Tracks": tracks,
        "BingoTickets": tickets,
    }
    json.dump(data, output, indent=2, default=flatten)
    return True
