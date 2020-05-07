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
import time
import typing

from pony.orm import Database, PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import perm, composite_key, db_session, select  # type: ignore
from pony.orm import user_groups_getter, commit, exists, show # type: ignore
from pony.orm import Json, flush # type: ignore

from musicbingo.utils import flatten, from_isodatetime, to_iso_datetime
from musicbingo.options import Options
from musicbingo.models.db import db, schema_version
from musicbingo.primes import PRIME_NUMBERS

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
        pk_maps[table.__name__] = {}
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

    pk_maps: typing.Dict[str, typing.Dict[int, int]] = {
        "Directory": {},
        "Song": {},
    }
    print("Processing tracks...")
    for track in data['Tracks']:
        song: typing.Optional[Song] = None
        song_pk = track.get('song', None)
        if song_pk is None:
            song_pk = track.get('song_pk', None)
        if 'song_pk' is not None:
            song = Song.get(pk=song_pk)
        #if song is None:
        #    song = Song.lookup(track, pk_maps)
        if song is None:
            song = Song.search_for_song(track, pk_maps)
        if song is None:
            print('Failed to find song for track:', track)
            continue
        pk_maps["Song"][track['pk']] = song.pk
        pk_maps["Directory"][song.directory.pk] = song.directory.pk
        track["song"] = song.pk
    print("Importing games")
    Game.import_json(data['Games'], options, pk_maps) # type: ignore
    print("Importing tracks")
    Track.import_json(data['Tracks'], options, pk_maps)
    print("Importing tickets")
    BingoTicket.import_json(data['BingoTickets'], options, pk_maps) # type: ignore
    print("commit")
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

@db_session
def import_game_tracks(options: Options, filename: Path, game_id: str) -> typing.Dict[str, typing.Dict[int, int]]:
    """
    Import an old gameTracks.json file into database
    """
    if schema_version != 2:
        print("WARNING: Importing is only supported into the latest version of the database")

    with filename.open('r') as input:
        tracks = json.load(input)

    stats = filename.stat()
    start = datetime(*(time.gmtime(stats.st_mtime)[0:6]))
    end = start + timedelta(days=1)
    game_pk = int(stats.st_ctime)
    data = {
        "Games": [{
            "pk": game_pk,
            "id": game_id,
            "title": game_id,
            "start": to_iso_datetime(start),
            "end": to_iso_datetime(end),
        }],
        "Songs": [],
        "Tracks": []
    }
    clip_dir = options.clips()
    pk_maps: typing.Dict[str, typing.Dict[int, int]] = {
        "Directory": {},
    }
    for idx, track in enumerate(tracks):
        song = {
            'channels': 2,
            'sample_rate': 44100,
            'sample_width': 16,
            'bitrate': options.bitrate,
        }
        song.update(track)
        for field in ['prime', 'start_time', 'number']:
            if field in song:
                del song[field]
        try:
            fullpath = Path(song['fullpath'])
            del song['fullpath']
        except KeyError:
            fullpath = Path(song['filepath'])
            del song['filepath']
        song['filename'] = fullpath.name
        song_dir = Directory.get(name=str(fullpath.parent))
        if song_dir is None:
            dirname = clip_dir.joinpath(fullpath)
            song_dir = Directory.get(name=str(dirname.parent))
        if song_dir is None:
            dirname = Path(options.clip_directory).joinpath(fullpath)
            song_dir = Directory.get(name=str(dirname.parent))
        if song_dir is not None:
            song['directory'] = song_dir.pk
            pk_maps["Directory"][song_dir.pk] = song_dir.pk
        try:
            song["pk"] = track["song_id"]
            del song["song_id"]
            del track["song_id"]
        except KeyError:
            song["pk"] = 100 + idx
        if song["title"][:2] == 'u"' and song["title"][-1] == '"':
            song["title"] = song["title"][2:-1]
        elif song["title"][0] == '"' and song["title"][-1] == '"':
            song["title"] = song["title"][1:-1]
        if song["title"][0] == '[' and song["title"][-1] == ']':
            song["title"] = song["title"][1:-1]
        data["Songs"].append(song)
        try:
            prime = track["prime"]
            number = PRIME_NUMBERS.index(prime)
        except KeyError:
            number = track.get("number", idx)
        start_time =  track["start_time"]
        if isinstance(start_time, str):
            mins, secs = start_time.split(':')
            start_time = int(secs) + 60 * int(mins)
        data["Tracks"].append({
            "pk": 200 + idx,
            "game": game_pk,
            "number": number,
            "start_time": start_time,
            "song": song['pk'],
        })
    #print(json.dumps(data, indent=2))
    Song.import_json(data['Songs'], options, pk_maps) # type: ignore
    Game.import_json(data['Games'], options, pk_maps) # type: ignore
    Track.import_json(data['Tracks'], options, pk_maps) # type: ignore
    commit()
    return pk_maps
