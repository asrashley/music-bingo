"""
This file contains all of the database models.

"""
import copy
from datetime import datetime, timedelta
import io
import json
import logging
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
        helper.log.info('Import %s', table.__name__)  # type: ignore
        helper.pk_maps[table.__name__] = {}
        if table.__name__ in data:  # type: ignore
            table.import_json(helper, data[table.__name__])  # type: ignore
        elif table.__plural__ in data:  # type: ignore
            table.import_json(helper, data[table.__plural__])  # type: ignore
        elif table == Directory and 'Directorys' in data:
            table.import_json(helper, data['Directorys'])  # type: ignore
    session.commit()
    return helper


def rename_pk_aliases(data):
    """
    various JSON formats use different names for referencing primary keys
    of other models, such as "foo" , "foo_id" or "foo_pk". Harmonize all
    of these to "foo"
    """
    if isinstance(data, list):
        for item in data:
            rename_pk_aliases(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                rename_pk_aliases(value)
            elif key in ['song', 'game', 'directory']:
                for suffix in ['id', 'pk']:
                    alias = f'{key}_{suffix}'
                    if alias in data:
                        data[field] = data[alias]
                        del data[alias]

@db.db_session
def import_game_data(data: JsonObject, options: Options, session) -> ImportSession:
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
    if 'Games' not in data:
        helper.log.error("A game must be provided to import_game_data")
        return helper

    rename_pk_aliases(data)
    helper.log.debug("Processing tracks...")
    lost: typing.Optional[Directory] = typing.cast(
        typing.Optional[Directory],
        Directory.get(session, name="lost+found"))
    if lost is None:
        lost = Directory(
            name="lost+found",
            title="lost & found",
            artist="Orphaned songs")
        session.add(lost)
    game = data["Games"][0]
    song_dir: typing.Optional[Directory] = typing.cast(
        typing.Optional[Directory],
        Directory.get(session, name=game['id'], parent=lost))
    if 'Songs' in data:
        Song.import_json(helper, data['Songs'])  # type: ignore
    for track in data['Tracks']:  # type: ignore
        song: typing.Optional[Song] = None
        song_pk = track.get('song', None)
        if 'Songs' in data:
            song_pk = helper["Song"][song_pk]
        if song_pk is not None:
            song = typing.cast(
                typing.Optional[Song],
                Song.get(session, pk=song_pk))
        if song is None:
            song = Song.search_for_song(helper, track)
        if song is None:
            helper.log.info('Failed to find song for track %s in the database', track.get('pk'))
            helper.log.debug('%s', track)
            if 'filename' not in track:
                helper.log.warning('Skipping track %s', track)
                continue
            if song_dir is None:
                song_dir = Directory(
                    parent=lost,
                    name=game['id'],
                    title=game['title'],
                    artist="Unknown")
                session.add(song_dir)
                session.flush()
            song_fields = Song.from_json(helper, track)
            song_fields['directory'] = song_dir
            song = Song(**song_fields)
            helper.log.info('Adding song "%s" (%d) to lost+found directory', song.title, song.pk)
            session.flush()
        helper.pk_maps["Song"][track['pk']] = song.pk
        helper.pk_maps["Directory"][song.directory.pk] = song.directory.pk
        track["song"] = song.pk
    Game.import_json(helper, data['Games'])  # type: ignore
    Track.import_json(helper, data['Tracks'])  # type: ignore
    if 'BingoTickets' in data:
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
    if not game_id:
        if filename.name.lower().startswith('game-'):
            game_id = filename.stem[5:]
        elif filename.parent.name.startswith('Game-'):
            game_id = filename.parent.name[5:]
        elif filename.name == 'gameTracks.json':
            game_id = filename.parent.name
            if game_id.lower().startswith('game-'):
                game_id = game_id[5:]
    if not game_id:
        print('Failed to auto-detect game ID')
        return helper
    data = translate_game_tracks(helper, filename, game_id)
    session.commit()
    helper.log.info("Import directories")
    Directory.import_json(helper, data['Directories'])  # type: ignore
    helper.log.info("Import songs")
    Song.import_json(helper, data['Songs'])  # type: ignore
    helper.log.info("Import games")
    Game.import_json(helper, data['Games'])  # type: ignore
    helper.log.info("Import tracks")
    Track.import_json(helper, data['Tracks'])  # type: ignore
    if 'BingoTickets' in data:
        helper.log.info("Import Bingo tickets")
        BingoTicket.import_json(helper, data['BingoTickets'])  # type: ignore
    # helper = import_game_data(data, options)
    return helper


def translate_game_tracks(helper: ImportSession, filename: Path,
                          game_id: str) -> JsonObject:
    """
    Load a gameTracks.json and create an object that matches the current
    export-game format.
    """
    with filename.open('r') as input:
        tracks = json.load(input)

    if isinstance(tracks, dict) and "Tracks" in tracks and "Games" in tracks:
        return translate_v3_game_tracks(helper, filename, tracks, game_id)
    return translate_v1_v2_game_tracks(helper, filename, tracks, game_id)

def translate_v1_v2_game_tracks(helper: ImportSession, filename: Path,
                                tracks: typing.List[JsonObject],
                                game_id: str) -> JsonObject:
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
        "Directories": [],
        "Songs": [],
        "Tracks": []
    }
    clip_dir = helper.options.clips()
    position = 0
    lost: typing.Optional[Directory] = typing.cast(
        typing.Optional[Directory],
        Directory.get(helper.session, name="lost+found"))
    if lost is None:
        lost = Directory(
            name="lost+found",
            title="lost & found",
            artist="Orphaned songs")
        helper.session.add(lost)
        helper.session.flush()
    data["Directories"].append(lost.to_dict())  # type: ignore
    lost_song_dir: typing.Optional[Directory] = typing.cast(
        typing.Optional[Directory],
        Directory.get(helper.session, name=game_id, parent=lost))
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
        if song_dir is None:
            song_dir = Directory.search_for_directory(helper.session, song)
        if song_dir is None:
            if lost_song_dir is None:
                lost_song_dir = Directory(
                    parent=lost,
                    name=game_id,
                    title=game_id,
                    artist="Unknown")
                helper.session.add(lost_song_dir)
                helper.session.flush()
                data["Directories"].append(lost_song_dir.to_dict())  # type: ignore
            song_dir = lost_song_dir
        assert song_dir is not None
        song['directory'] = song_dir.pk
        # helper.pk_maps["Directory"][song_dir.pk] = song_dir.pk
        if 'song' in track:
            song["pk"] = track["song"]
        elif 'song_id' in track:
            song["pk"] = track["song_id"]
            del song["song_id"]
            del track["song_id"]
        else:
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

def translate_v3_game_tracks(helper: ImportSession, filename: Path,
                             data: JsonObject,
                             game_id: str) -> JsonObject:
    retval = copy.deepcopy(data);
    directories = {}
    items = data["Tracks"]
    retval["Songs"] = []
    retval["Tracks"] = []
    for track in items:
        if "directory" in track:
            del track["directory"]
        song = copy.copy(track)
        del song["start_time"]
        del song["number"]
        del song["game"]
        del song["pk"]
        song_mod = Song.search_for_song(helper, song)
        if song_mod is not None:
            song["pk"] = song_mod.pk
            song["directory"] = song_mod.directory.pk
            directories[song_mod.directory.pk] = song_mod.directory
            track["song"] = song_mod.pk
        retval["Songs"].append(song)
        retval["Tracks"].append(track)
    print(directories)
    retval["Directories"] = [d.to_dict() for d in directories.values()]
    return retval
