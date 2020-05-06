"""
This file contains all of the database models.

"""
import copy
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import secrets
import threading
import typing

from pony.orm import Database, PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import perm, composite_key, db_session, select  # type: ignore
from pony.orm import user_groups_getter, commit, exists, show # type: ignore
from pony.orm import Json, flush # type: ignore

from musicbingo.utils import flatten, from_isodatetime
from musicbingo.options import Options
from musicbingo.models.db import db, schema_version

if schema_version == 1:
    from musicbingo.models.v1.schema import BingoTicket, Directory, Game, Group, Song, Track, User
else:
    from musicbingo.models.v2.schema import BingoTicket, Directory, Game, Group, Song, Track, User


with db.set_perms_for(User, BingoTicket, Game, Track):
    perm('view', group='anybody').exclude(User.password, User.email)

__setup = False
__bind_lock = threading.Lock()

def bind(**bind_args):
    """
    setup database to be able to use it
    """
    global __setup
    global __bind_lock
    with __bind_lock:
        if __setup == True:
            return
        basedir = Path(__file__).parents[1]
        if 'name' in bind_args:
            bind_args['db'] = bind_args['name']
            del bind_args['name']
        print('bind database', bind_args)
        db.bind(**bind_args)
        db.generate_mapping(create_tables=True)
        with db_session:
            admin = User.get(username="admin")
            if admin is None:
                password = secrets.token_urlsafe(14)
                groups_mask = Group.admin.value + Group.users.value
                admin = User(username="admin", email="admin@music.bingo",
                             groups_mask=groups_mask,
                             password=User.hash_password(password))
                #TODO: investigate why groups_mask not working when
                #creating admin account
                admin.set_groups([Group.admin, Group.users])
                print(f'Created admin account "{admin.username}" ({admin.email}) with password "{password}"')
        __setup = True

@db_session(sql_debug=True, show_values=True)
def show_database():
    """
    Display entire contents of database
    """
    for table in [User, Game, BingoTicket, Track, Directory, Song]:
        table.select().show()


def export_database(filename: Path) -> None:
    """
    Output entire contents of database as JSON
    """
    with filename.open('w') as output:
        export_database_to_file(output)

@db_session
def export_database_to_file(output: typing.TextIO) -> None:
    """
    Output entire contents of database as JSON to specified file
    """
    output.write('{\n')
    for table in [User, Game, BingoTicket, Track, Directory, Song]:
        print(table.__name__)
        contents = []
        for item in table.select(): # type: ignore
            data = item.to_dict(with_collections=True)
            contents.append(flatten(data)) # type: ignore
        output.write(f'"{table.__plural__}":') # type: ignore
        json.dump(contents, output, indent='  ')
        comma = ','
        if table != Song:
            output.write(',')
        output.write('\n')
    output.write('}\n')

@db_session
def import_database(options: Options, filename: Path) -> typing.Dict[str, typing.Dict[int, int]]:
    """
    Import JSON file into database
    """
    if schema_version != 2:
        print("WARNING: Importing is only supported into the latest version of the database")

    with filename.open('r') as input:
        data = json.load(input)

    if 'User' not in data and 'Songs' not in data and 'Games' in data and 'Tracks' in data:
        return import_game_data(data, options)

    pk_maps: typing.Dict[str, typing.Dict[int, int]] = {}
    for table in [User, Directory, Song, Game, Track, BingoTicket]:
        print(table.__name__)
        if table.__name__ in data:
            table.import_json(data[table.__name__], options,  # type: ignore
                              pk_maps)
        elif table.__plural__ in data: # type: ignore
            table.import_json(data[table.__plural__], options,  # type: ignore
                              pk_maps)
        elif table == Directory and 'Directorys' in data:
            table.import_json(data['Directorys'], options, # type: ignore
                              pk_maps)
        commit()
    return pk_maps

@db_session
def import_game_data(data: typing.List, options: Options) -> typing.Dict[str, typing.Dict[int, int]]:
    """
    Import games into database.
    This is used to import "game-<game-id>.json" files or the output from the
    "export-game" command.
    """
    if schema_version != 2:
        print("WARNING: Importing is only supported into the latest version of the database")

    pk_maps: typing.Dict[str, typing.Dict[int, int]] = {}
    pk_maps[Song] = {}
    for track in data['Tracks']:
        song: typing.Optional[Song] = None
        if 'song_pk' in track:
            song = Song.get(pk=track['song_pk'])
        if song is None:
            song = Song.lookup(track, pk_maps)
        if song is None:
            song = Song.search_for_song(track)
        if song is None:
            print('Failed to find song for track:', track)
            continue
        pk_maps[Song][track['pk']] = song.pk
        track["song"] = song.pk
    Game.import_json(data['Games'], options, pk_maps) # type: ignore
    Track.import_json(data['Tracks'], options, pk_maps)
    BingoTicket.import_json(data['BingoTickets'], options, pk_maps) # type: ignore
    commit()
    return pk_maps

def export_game(game_id: str, filename: Path) -> None:
    """
    Output one game as a JSON file
    """
    with filename.open('w') as output:
        export_game_to_file(game_id, output)

@db_session
def export_game_to_file(game_id: str, output: typing.TextIO) -> bool:
    """
    Output one game in JSON format to specified file
    """
    game = Game.get(id=game_id)
    if game is None:
        print(f'Failed to find game "{game_id}". Available games:')
        print([game.id for game in Game.select()])
        return False
    tracks = []
    for track in game.tracks.order_by(Track.number):
        item = track.song.to_dict()
        item.update(track.to_dict())
        tracks.append(item)
    tickets = [ticket.to_dict(with_collections=True) for ticket in game.bingo_tickets]
    data = {
        "Games": [
            game.to_dict(with_collections=True)
        ],
        "Tracks": tracks,
        "BingoTickets": tickets,
    }
    json.dump(data, output, indent=2, default=flatten)
    return True
