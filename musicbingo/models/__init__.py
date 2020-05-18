"""
This file contains all of the database models.

"""
import copy
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import time
import typing

from sqlalchemy import create_engine, inspect, MetaData  # type: ignore

from musicbingo.utils import flatten, from_isodatetime, to_iso_datetime
from musicbingo.options import DatabaseOptions, Options
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.models import db
from musicbingo.models.bingoticket import BingoTicket
from musicbingo.models.game import Game
from musicbingo.models.group import Group
from musicbingo.models.importsession import ImportSession
from musicbingo.models.modelmixin import JsonObject
from musicbingo.models.user import User
from musicbingo.models.directory import Directory
from musicbingo.models.song import Song
from musicbingo.models.token import Token, TokenType
from musicbingo.models.track import Track


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
    output.write('{\n')
    tables = [User, Game, BingoTicket, Track, Directory, Song]
    for table in tables:
        print(table.__name__)  # type: ignore
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


@db.db_session
def import_database(options: Options, filename: Path, session) -> ImportSession:
    """
    Import JSON file into database
    """
    with filename.open('r') as input:
        data = json.load(input)

    if 'User' not in data and 'Songs' not in data and 'Games' in data and 'Tracks' in data:
        return import_game_data(data, options)

    helper = ImportSession(options, session)

    for table in [User, Directory, Song, Game, Track, BingoTicket]:
        print(table.__name__)  # type: ignore
        helper.pk_maps[table.__name__] = {}
        if table.__name__ in data:  # type: ignore
            table.import_json(helper, data[table.__name__])  # type: ignore
        elif table.__plural__ in data:  # type: ignore
            table.import_json(helper, data[table.__plural__])  # type: ignore
        elif table == Directory and 'Directorys' in data:
            table.import_json(helper, data['Directorys'])  # type: ignore
    session.commit()
    return helper


@db.db_session
def import_game_data(data: typing.List, options: Options, session) -> ImportSession:
    """
    Import games into database.
    This is used to import "game-<game-id>.json" files or the output from the
    "export-game" command.
    """
    helper = ImportSession(options, session)
    helper.pk_maps = {
        "Directory": {},
        "Song": {},
    }
    print("Processing tracks...")
    for track in data['Tracks']:  # type: ignore
        song: typing.Optional[Song] = None
        song_pk = track.get('song', None)
        if song_pk is None:
            song_pk = track.get('song_pk', None)
        if song_pk is not None:
            song = typing.cast(
                typing.Optional[Song],
                Song.get(session, pk=song_pk))
        # if song is None:
        #    song = Song.lookup(track, pk_maps)
        if song is None:
            song = Song.search_for_song(helper, track)
        if song is None:
            print('Failed to find song for track:', track)
            continue
        helper.pk_maps["Song"][track['pk']] = song.pk
        helper.pk_maps["Directory"][song.directory.pk] = song.directory.pk
        track["song"] = song.pk
    Game.import_json(helper, data['Games'])  # type: ignore
    Track.import_json(helper, data['Tracks'])  # type: ignore
    BingoTicket.import_json(helper, data['BingoTickets'])  # type: ignore
    session.commit()
    return helper


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


@db.db_session
def import_game_tracks(options: Options, filename: Path,
                       game_id: str, session) -> ImportSession:
    """
    Import an old gameTracks.json file into database.
    This format has a list of songs, in playback order.
    """
    helper = ImportSession(options, session)
    data = translate_game_tracks(helper, filename, game_id)
    Song.import_json(helper, data['Songs'])  # type: ignore
    Game.import_json(helper, data['Games'])  # type: ignore
    Track.import_json(helper, data['Tracks'])  # type: ignore
    session.commit()
    return helper


def translate_game_tracks(helper: ImportSession, filename: Path,
                          game_id: str) -> JsonObject:
    """
    Load a gameTracks.json and create an object that matches the current
    export-game format.
    """
    with filename.open('r') as input:
        tracks = json.load(input)

    stats = filename.stat()
    start = datetime(*(time.gmtime(stats.st_mtime)[0:6]))
    end = start + timedelta(days=1)
    game_pk = 1
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
    clip_dir = helper.options.clips()
    position = 0
    for idx, track in enumerate(tracks):
        song = {
            'title': '',
            'filename': '',
            'channels': 2,
            'sample_rate': 44100,
            'sample_width': 16,
            'bitrate': helper.options.bitrate,
        }
        song.update(track)
        for field in ['prime', 'start_time', 'number']:
            if field in song:
                del song[field]
        if 'fullpath' in song:
            fullpath = Path(typing.cast(str, song['fullpath']))
            del song['fullpath']
        elif 'filepath' in song:
            fullpath = Path(typing.cast(str, song['filepath']))
            del song['filepath']
        else:
            fullpath = Path(typing.cast(str, song['filename']))
        song['filename'] = fullpath.name
        song_dir = typing.cast(
            typing.Optional[Directory],
            Directory.get(helper.session, name=str(fullpath.parent)))
        if song_dir is None:
            dirname = clip_dir.joinpath(fullpath)
            song_dir = typing.cast(
                typing.Optional[Directory],
                Directory.get(helper.session, name=str(dirname.parent)))
        if song_dir is None:
            dirname = Path(helper.options.clip_directory).joinpath(fullpath)
            song_dir = typing.cast(
                typing.Optional[Directory],
                Directory.get(helper.session, name=str(dirname.parent)))
        if song_dir is not None:
            song['directory'] = song_dir.pk
            helper.pk_maps["Directory"][song_dir.pk] = song_dir.pk
        try:
            song["pk"] = track["song_id"]
            del song["song_id"]
            del track["song_id"]
        except KeyError:
            song["pk"] = 100 + idx
        title = typing.cast(str, song['title'])
        if title[:2] == 'u"' and title[-1] == '"':
            title = title[2:-1]
        elif title[0] == '"' and title[-1] == '"':
            title = title[1:-1]
        if title[0] == '[' and title[-1] == ']':
            title = title[1:-1]
        song["title"] = title
        data["Songs"].append(song)  # type: ignore
        try:
            prime = track["prime"]
            number = PRIME_NUMBERS.index(prime)
        except KeyError:
            number = track.get("number", idx)
        try:
            start_time = track["start_time"]
        except KeyError:
            start_time = position
        if isinstance(start_time, str):
            mins, secs = start_time.split(':')
            start_time = (int(secs) + 60 * int(mins)) * 1000
        data["Tracks"].append({  # type: ignore
            "pk": 200 + idx,
            "game": game_pk,
            "number": number,
            "start_time": start_time,
            "song": song['pk'],
        })
        position += track['duration']
    #print(json.dumps(data, indent=2))
    return data
