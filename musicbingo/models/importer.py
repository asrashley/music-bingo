"""
Class that allows various JSON files to be imported into the database.
It supports importing:
* a whole database (the output from export)
* one game (the output from export-game)
* gameTracks (the JSON file created when a game is generated)
"""
import copy
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
import time
from typing import Dict, List, Optional, Tuple, cast

from chardet.universaldetector import UniversalDetector
from sqlalchemy import func # type: ignore

from musicbingo.options import Options
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.progress import Progress
from musicbingo.utils import (
    clean_string, parse_date, make_naive_utc, to_iso_datetime,
    pick,
)
from musicbingo.uuidmixin import UuidMixin

from .album import Album
from .artist import Artist
from .bingoticket import BingoTicket, BingoTicketTrack
from .directory import Directory
from .game import Game
from .group import Group
from .modelmixin import ModelMixin, JsonObject, PrimaryKeyMap
from .session import DatabaseSession
from .song import Song
from .track import Track
from .user import User

# pylint: disable=invalid-name
def max_with_none(a, b):
    """
    version of max that works when items might be None
    """
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b)

class Importer:
    """
    Helper class that holds state informtion when importing a JSON
    file into the database.
    """

    BINGO_GAMES_DIRECTORY = "bingo+games"
    LOST_SONGS_DIRECTORY = "lost+found"

    def __init__(self, options: Options, session: DatabaseSession, progress: Progress):
        self.options = options
        self.session = session
        self.progress = progress
        self.log = logging.getLogger('musicbingo.models')
        self.pk_maps: PrimaryKeyMap = {}
        self.added: Dict[str, int] = {}
        # self.filename: Optional[Path] = None
        self.check_exists = False
        self.update_models = False
        self.imported_options: Optional[JsonObject] = None
        for model in ["User", "Album", "Artist", "Directory", "Song",
                      "Game", "Track", "BingoTicket"]:
            self.pk_maps[model] = {}
            self.added[model] = 0

    def __getitem__(self, table: str) -> Dict[int, int]:
        """
        Get the private key map for the given table.
        This map is from the PK defined in the JSON file to the PK of the item
        in the database.
        """
        return self.pk_maps[table]

    def set_map(self, table: str, pk_map: Dict[int, int]) -> None:
        """
        Set the private key map for the given table
        """
        self.pk_maps[table] = pk_map

    def add(self, model: ModelMixin) -> None:
        """
        Add model to the database
        """
        self.session.add(model)
        try:
            self.added[type(model).__name__] += 1
        except KeyError:
            self.added[type(model).__name__] = 1

    def commit(self) -> None:
        """
        Commit pending changes to the database
        """
        self.session.commit()

    def flush(self) -> None:
        """
        Flush pending changes to the database so that automatic fields (like pk)
        are assigned.
        Transaction can still be rolled-back on error.
        """
        self.session.flush()

    def import_database(self, filename: Path, data: Optional[JsonObject] = None) -> None:
        """
        Import JSON file into database
        """
        self.log.info('Importing database from file "%s"', filename)
        if data is None:
            with filename.open('r') as inp:
                data = json.load(inp)

        assert data is not None

        if 'Options' in data:
            self.imported_options = data['Options']
        #if 'User' not in data and 'Songs' not in data and 'Games' in data and 'Tracks' in data:
        #    self.log.info('Importing games')
        #    self.import_game_data(data)
        #else:
        self.import_json(data)
        self.session.commit()

    # pylint: disable=too-many-statements
    def off_import_game_data(self, data: JsonObject) -> None:
        """
        Import games into database.
        This is used to import "game-<game-id>.json" files or the output from the
        "export-game" command.
        """
        self.rename_pk_aliases(data)
        if 'Games' not in data:
            self.log.error("A game object must be provided to import_game_data")
            self.progress.text = "A game object must be provided to import_game_data"
            return
        self.rename_pk_aliases(data)
        self.log.debug("Processing tracks...")
        self.progress.text = "Processing tracks..."
        self.progress.num_phases = 6
        self.progress.current_phase = 0
        game = data["Games"][0]
        _, lost = self.get_bingo_games_directory(game['id'])
        song_dir: Optional[Directory] = cast(
            Optional[Directory],
            Directory.get(self.session, name=game['id'], parent=lost))
        self.progress.current_phase = 1
        if 'Songs' in data:
            self.import_songs(data['Songs'], game['id'])  # type: ignore
        self.progress.current_phase = 2
        for track in data['Tracks']:  # type: ignore
            song: Optional[Song] = None
            song_pk = track.get('song', None)
            if 'Songs' in data:
                song_pk = self["Song"][song_pk]
            if song_pk is not None:
                song = cast(
                    Optional[Song],
                    Song.get(self.session, pk=song_pk))
            if song is None:
                song = Song.search_for_song(self.session, self.pk_maps, track)
            if song is None:
                self.log.info('Failed to find song for track %s in the database', track.get('pk'))
                self.log.debug('%s', track)
                if 'filename' not in track:
                    self.log.warning('Skipping track %s', track)
                    continue
                if song_dir is None:
                    song_dir = Directory(
                        parent=lost,
                        name=game['id'],
                        title=game['title'])
                    self.session.add(song_dir)
                    self.session.flush()
                song_fields = Song.from_json(self.session, self.pk_maps, track)
                song_fields['directory'] = song_dir
                song = Song(**song_fields)
                self.session.add(song)
                self.session.flush()
                self.log.info('Adding song "%s" (%d) to Bingo Games directory',
                              song.title, song.pk)
            self.pk_maps["Song"][track['pk']] = song.pk
            self.pk_maps["Directory"][song.directory.pk] = song.directory.pk
            track["song"] = song.pk
        self.progress.current_phase = 3
        self.import_games(data['Games'])  # type: ignore
        self.progress.current_phase = 4
        self.import_tracks(data['Tracks'], game['id'])  # type: ignore
        self.progress.current_phase = 5
        if 'BingoTickets' in data:
            self.import_bingo_tickets(data['BingoTickets'])  # type: ignore
        self.progress.pct = 100.0
        self.session.commit()

    def rename_pk_aliases(self, data):
        """
        various JSON formats use different names for referencing primary keys
        of other models, such as "foo" , "foo_id" or "foo_pk". Harmonize all
        of these to "foo"
        """
        if isinstance(data, list):
            for item in data:
                self.rename_pk_aliases(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    self.rename_pk_aliases(value)
                elif key in ['song', 'game', 'directory']:
                    for suffix in ['id', 'pk']:
                        alias = f'{key}_{suffix}'
                        if alias in data:
                            data[key] = data[alias]
                            del data[alias]

    def import_json(self, data: JsonObject) -> None:
        """
        Import the models found in the data.
        """
        self.rename_pk_aliases(data)
        self.progress.num_phases = 8
        self.progress.current_phase = 0
        if 'Users' in data:
            self.import_users(data["Users"])
        self.progress.current_phase = 1
        if 'Directories' in data:
            self.import_directories(data["Directories"])
        elif 'Directorys' in data:
            self.import_directories(data["Directorys"])
        self.progress.current_phase = 2
        if 'Artists' in data:
            self.import_artists(data["Artists"])
        self.progress.current_phase = 3
        if 'Albums' in data:
            self.import_albums(data["Albums"])
        self.progress.current_phase = 4
        if 'Songs' in data:
            self.check_albums_and_artists(data["Songs"])
            self.import_songs(data["Songs"], None)
        self.progress.current_phase = 5
        if 'Games' not in data:
            self.progress.current_phase = 7
            self.progress.text = 'Import complete'
            self.progress.pct = 100
            return
        self.import_games(data["Games"])
        self.progress.current_phase = 6
        if 'Tracks' in data:
            self.import_tracks(data['Tracks'], None)
        self.progress.current_phase = 7
        if 'BingoTickets' in data:
            self.import_bingo_tickets(data['BingoTickets'])
        self.progress.pct = 100.0
        self.progress.text = 'Import complete'

    def check_albums_and_artists(self, songs: List[JsonObject]) -> None:
        """
        Look for albums and artists in the list of songs.
        Adds them to the database if not found.
        """
        albums = set()
        artists = set()
        for song in songs:
            if 'album' in song and isinstance(song['album'], str):
                albums.add(song['album'])
            if 'artist' in song and isinstance(song['artist'], str):
                artists.add(song['artist'])
        if albums:
            max_pk = self.session.query(func.max(Album.pk)).scalar()
            if max_pk is None:
                next_pk = 1
            else:
                next_pk = max_pk + 10
            self.import_albums([
                {'name': album, 'pk': next_pk+idx} for idx, album in enumerate(albums)])
        if artists:
            max_pk = self.session.query(func.max(Artist.pk)).scalar()
            if max_pk is None:
                next_pk = 1
            else:
                next_pk = max_pk + 10
            self.import_artists([
                {'name': artist, 'pk': next_pk+idx} for idx, artist in enumerate(artists)])

    def import_game_tracks(self, filename: Path, game_id: str,
                           source: Optional[JsonObject] = None) -> None:
        """
        Import a gameTracks.json file into database.
        """
        self.log.info('Importing gameTracks.json from file "%s"', filename)
        if not game_id:
            game_id = self.detect_game_id_from_filename(filename)
        if not game_id:
            self.log.error('Failed to auto-detect game ID')
            return
        self.log.info('Game ID: %s', game_id)
        if Game.exists(self.session, id=game_id):
            self.log.error("Game has aleady been imported")
            self.progress.text = f'Game "{game_id}" is aleady in the database'
            return
        self.progress.num_phases = 8
        self.progress.current_phase = 0
        data = self.translate_game_tracks(filename, game_id, source=source)
        self.progress.current_phase = 1
        self.log.info("Importing directories")
        self.import_directories(data['Directories'])  # type: ignore
        self.progress.current_phase = 2
        self.log.info("Importing albums")
        self.import_albums(data['Albums'])  # type: ignore
        self.progress.current_phase = 3
        self.log.info("Importing artists")
        self.import_artists(data['Artists'])  # type: ignore
        self.progress.current_phase = 4
        self.log.info("Import songs")
        self.import_songs(data['Songs'], game_id)  # type: ignore
        self.progress.current_phase = 5
        self.log.info("Import games")
        self.import_games(data['Games'])  # type: ignore
        self.progress.current_phase = 6
        self.log.info("Import tracks")
        self.import_tracks(data['Tracks'], game_id)  # type: ignore
        self.progress.current_phase = 7
        if 'BingoTickets' in data:
            self.log.info("Import Bingo tickets")
            self.import_bingo_tickets(data['BingoTickets'])  # type: ignore
        self.progress.pct = 100
        self.progress.text = 'Import complete'

    @staticmethod
    def detect_game_id_from_filename(filename: Path) -> str:
        """
        Extract the game ID from a filename
        """
        game_id = ''
        if filename.name.lower().startswith('game-'):
            game_id = filename.stem[5:]
        elif filename.parent.name.startswith('Game-'):
            game_id = filename.parent.name[5:]
        elif filename.name == 'gameTracks.json':
            game_id = filename.parent.name
            if game_id.lower().startswith('game-'):
                game_id = game_id[5:]
        return game_id

    def translate_game_tracks(self, filename: Path, game_id: str, *,
                              source: Optional[JsonObject] = None,
                              encoding: Optional[str] = None) -> JsonObject:
        """
        Load a gameTracks.json and create an object that matches the current
        export-game format.
        """
        if source is None:
            if encoding is None:
                detector = UniversalDetector()
                with filename.open('rb') as probe:
                    for line in probe:
                        detector.feed(line)
                        if detector.done:
                            break
                detector.close()
                if detector.result['confidence'] > 0.1:
                    encoding = detector.result['encoding']
            with filename.open('rt', encoding=encoding) as inp:
                tracks = json.load(inp)
        else:
            tracks = source

        if (isinstance(tracks, dict) and "Songs" in tracks and "Tracks" in tracks
                and "Games" in tracks):
            return self.translate_v4_game_tracks(tracks)
        if isinstance(tracks, dict) and "Tracks" in tracks and "Games" in tracks:
            return self.translate_v3_game_tracks(tracks, game_id)
        return self.translate_v1_v2_game_tracks(filename, tracks, game_id)

    def translate_v1_v2_game_tracks(self, filename: Optional[Path],
                                    tracks: List[JsonObject],
                                    game_id: str) -> JsonObject:
        """
        Load a v1 or v2 gameTracks.json and create an object that matches the
        current export-game format.
        """
        if filename and filename.exists():
            stats = filename.stat()
            start = datetime(*(time.gmtime(stats.st_mtime)[0:6]))
        else:
            start = datetime.now()
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
            "Albums": [],
            "Artists": [],
            "Directories": [],
            "Songs": [],
            "Tracks": []
        }
        position = 0
        artists = {}
        albums = {}
        dir_map: Dict[int, JsonObject] = {}
        for idx, trk in enumerate(tracks):
            song, track = self.translate_one_v1_v2_track(
                game_id, idx, position, dir_map, trk)
            track["game"] = game_pk
            album = song['album']
            if isinstance(album, list):
                album = album[0]
            if album not in albums:
                albums[album] = 1 + len(cast(list, data['Albums']))
                cast(list, data['Albums']).append({
                    'name': album,
                    'pk': 1 + len(cast(list, data['Albums']))
                })
            song['album'] = albums[album]
            artist = song['artist']
            if artist not in artists:
                artists[artist] = 1 + len(cast(list, data['Artists']))
                cast(list, data['Artists']).append({
                    'name': artist,
                    'pk': 1 + len(cast(list, data['Artists']))
                })
            song['artist'] = artists[artist]
            data["Songs"].append(song)  # type: ignore
            data["Tracks"].append(track)  # type: ignore
            position += trk['duration']
        data['Directories'] = list(dir_map.values())
        return data

    # pylint: disable=too-many-branches,too-many-statements
    def translate_one_v1_v2_track(self, game_id: str, idx: int,
                                  position: int, dir_map: Dict[int, JsonObject],
                                  data: JsonObject) -> Tuple[JsonObject, JsonObject]:
        """
        Create one Song object and one Track object from the given data
        """
        directory: Optional[Directory] = None
        song = {
            'title': '',
            'filename': '',
            'channels': 2,
            'sample_rate': 44100,
            'sample_width': 16,
            'bitrate': self.options.bitrate,
        }
        song.update(data)
        for field in ['prime', 'start_time', 'number']:
            if field in song:
                del song[field]
        games_dir_parent, games_dir = self.get_bingo_games_directory(game_id)
        fullpath: Optional[PurePath] = None
        if 'fullpath' in song:
            if '\\' in cast(str, song['fullpath']):
                fullpath = PureWindowsPath(cast(str, song['fullpath']))
            else:
                fullpath = PurePosixPath(cast(str, song['fullpath']))
            del song['fullpath']
            fullpath = self.options.clips().joinpath(fullpath)
        elif 'filepath' in song:
            if '\\' in cast(str, song['filepath']):
                fullpath = PureWindowsPath(cast(str, song['filepath']))
            else:
                fullpath = PurePosixPath(cast(str, song['filepath']))
            del song['filepath']
            fullpath = self.options.clips().joinpath(fullpath)
        else:
            fullpath = PurePosixPath(games_dir['name']) / cast(str, song['filename'])
        song['filename'] = fullpath.name
        for field in ['album', 'artist', 'title']:
            # work-around bug in v1 gameTracks
            if isinstance(song[field], list):
                song[field] = ' '.join(cast(List[str], song[field]))
            song[field] = clean_string(cast(str, song[field]))
        uuid = UuidMixin.create_uuid(**song) # type: ignore
        song_models = Song.search(self.session, uuid=uuid)
        if song_models.count() == 1:
            directory = song_models[0].directory
            song['uuid'] = uuid
            song['artist'] = song_models[0].artist.name
            song['album'] = song_models[0].album.name
        else:
            song_model = Song.search_for_song(self.session, self.pk_maps, song)
            if song_model is not None:
                directory = song_model.directory
                song['uuid'] = song_model.uuid
        if directory is None:
            directory = cast(
                Optional[Directory],
                Directory.get(self.session, name=str(fullpath.parent)))
        if directory is None:
            song['directory'] = games_dir['pk']
            if games_dir_parent['pk'] not in dir_map:
                dir_map[games_dir_parent['pk']] = games_dir_parent
            if games_dir['pk'] not in dir_map:
                dir_map[games_dir['pk']] = games_dir
        else:
            song['directory'] = directory.pk
            if directory.pk not in dir_map:
                dir_map[directory.pk] = directory.to_dict()
                parent = directory.parent
                while parent is not None:
                    if parent.pk not in dir_map:
                        dir_map[parent.pk] = parent.to_dict()
                    parent = parent.parent
        if 'song' in data:
            song["pk"] = data["song"]
        elif 'song_id' in data:
            song["pk"] = data["song_id"]
            del song["song_id"]
            del data["song_id"]
        else:
            song["pk"] = 100 + idx
        try:
            prime = data["prime"]
            number = PRIME_NUMBERS.index(prime)
        except KeyError:
            number = data.get("number", idx)
        try:
            start_time = data["start_time"]
        except KeyError:
            start_time = position
        if isinstance(start_time, str):
            mins, secs = start_time.split(':')
            start_time = (int(secs) + 60 * int(mins)) * 1000
        track = {
            "pk": 200 + idx,
            "number": number,
            "start_time": start_time,
            "song": song['pk'],
        }
        return (song, track,)

    def translate_v3_game_tracks(self, data: JsonObject, game_id: str) -> JsonObject:
        """
        Load a v3 gameTracks.json and create an object that matches the current
        export-game format.
        """
        retval = {
            "Albums": [],
            "Artists": [],
            "Directories": [],
            "Songs": [],
            "Games": data['Games'],
            "Tracks": [],
            "BingoTickets": data["BingoTickets"],
        }
        dir_map: Dict[str, JsonObject] = {}
        album_map: Dict[str, int] = {}
        artist_map: Dict[str, int] = {}
        for item in data["Tracks"]:
            song, track = self.translate_one_v3_track(
                item, game_id, album_map, artist_map, dir_map)
            retval["Songs"].append(song) # type: ignore
            retval["Tracks"].append(track) # type: ignore
        retval["Directories"] = list(dir_map.values())
        for name, pk in album_map.items():
            retval['Albums'].append({
                'name': name,
                'pk': pk
            })
        for name, pk in artist_map.items():
            retval['Artists'].append({
                'name': name,
                'pk': pk
            })
        return retval

    def translate_one_v3_track(self, item: JsonObject,
                               game_id: str,
                               album_map: Dict[str, int],
                               artist_map: Dict[str, int],
                               dir_map: Dict[str, JsonObject]) -> Tuple[JsonObject, JsonObject]:
        """
        Convert one v3 track into a directory, song and track
        """
        for name in ['album', 'artist', 'title']:
            if name in item and item[name]:
                item[name] = clean_string(item[name])
        song = copy.copy(item)
        track = pick(item, {"pk", "number", "start_time", "game", "song", "title"})
        song['pk'] = item['song']
        uuid = UuidMixin.create_uuid(**song)
        album = song["album"]
        if album not in album_map:
            album_map[album] = 1 + len(album_map)
        song["album"] = album_map[album]
        artist = song["artist"]
        if artist not in artist_map:
            artist_map[artist] = 1 + len(artist_map)
        song["artist"] = artist_map[artist]
        song_mod: Optional[Song] = None
        query = Song.search(self.session, uuid=uuid)
        if query.count() == 1:
            song_mod = query.first()
        if song_mod is None:
            song_mod = Song.search_for_song(self.session, self.pk_maps, song)
        if song_mod is None:
            games_dir_parent, games_dir = self.get_bingo_games_directory(game_id)
            if games_dir_parent['name'] not in dir_map:
                dir_map[games_dir_parent['name']] = games_dir_parent
            if games_dir['name'] not in dir_map:
                dir_map[games_dir['name']] = games_dir
            song["directory"] = games_dir['pk']
        else:
            song["pk"] = song_mod.pk
            song["directory"] = song_mod.directory.pk
            song["uuid"] = song_mod.uuid
            track["song"] = song_mod.pk
            if song_mod.directory.name not in dir_map:
                dir_map[song_mod.directory.name] = song_mod.directory.to_dict()
        return (song, track,)

    def translate_v4_game_tracks(self, data: JsonObject) -> JsonObject:
        """
        Load a v4 gameTracks.json and create an object that matches the current
        export-game format.
        """
        max_dir_pk = self.session.query(func.max(Directory.pk)).scalar()
        if max_dir_pk is None:
            max_dir_pk = 1
        game_id = data['Games'][0]['id']
        result = copy.deepcopy(data)
        album_map: Dict[str, int] = {}
        artist_map: Dict[str, int] = {}
        input_dir_map: Dict[int, JsonObject] = {}
        for directory in data["Directories"]:
            directory['pk'] += max_dir_pk
            input_dir_map[directory['pk']] = directory
        dir_map: Dict[int, JsonObject] = {}
        games_dir_parent, games_dir = self.get_bingo_games_directory(game_id)
        for song in result["Songs"]:
            if song['album'] not in album_map:
                album_map[song['album']] = 1 + len (album_map)
            if song['artist'] not in artist_map:
                artist_map[song['artist']] = 1 + len (artist_map)
            song['album'] = album_map[song['album']]
            song['artist'] = artist_map[song['artist']]
            direc = input_dir_map[song['directory'] + max_dir_pk]
            uuid = UuidMixin.str_from_uuid(UuidMixin.str_to_uuid(song['uuid']))
            query = self.session.query(Song).filter(Song.uuid == uuid)
            count = query.count()
            if count > 1:
                query = self.session.query(Song).join(Directory).filter(
                    (Directory.title == direc['title']) & (Song.uuid == uuid))
                count = query.count()
            if count == 1:
                song_model = query.first()
                song['directory'] = song_model.directory.pk
                if song_model.directory.pk not in dir_map:
                    dir_map[song_model.directory.pk] = song_model.directory.to_dict()
                    parent = song_model.directory.parent
                    while parent is not None:
                        if parent.pk not in dir_map:
                            dir_map[parent.pk] = parent.to_dict()
                        parent = parent.parent
            else:
                song['directory'] = games_dir['pk']
                if games_dir_parent['pk'] not in dir_map:
                    dir_map[games_dir_parent['pk']] = games_dir_parent
                if games_dir['pk'] not in dir_map:
                    dir_map[games_dir['pk']] = games_dir
        result['Directories'] = list(dir_map.values())
        result['Albums'] = []
        for name, pk in album_map.items():
            result['Albums'].append(dict(pk=pk, name=name))
        result['Artists'] = []
        for name, pk in artist_map.items():
            result['Artists'].append(dict(pk=pk, name=name))
        return result

    def get_bingo_games_directory(self, game_id: Optional[str],
                                  next_pk: Optional[int] = None) -> Tuple[JsonObject,
                                                                          JsonObject]:
        """
        Get directory to store songs from bingo games
        """
        toplevel_json: JsonObject = {}
        gamedir_json: JsonObject = {}
        if next_pk is None:
            max_dir_pk = self.session.query(func.max(Directory.pk)).scalar()
            if max_dir_pk is None:
                max_dir_pk = 1
            next_pk = 1 + max_dir_pk
        toplevel_dir: Optional[Directory] = cast(
            Optional[Directory],
            Directory.get(self.session, name=self.BINGO_GAMES_DIRECTORY))
        if toplevel_dir is not None:
            toplevel_json = toplevel_dir.to_dict()
        else:
            toplevel_json = {
                'pk': next_pk,
                'name': self.BINGO_GAMES_DIRECTORY,
                'title': 'Bingo Games',
                'parent': None
            }
            next_pk += 1
        if game_id is None:
            return (toplevel_json, {},)
        dirname = f'{self.BINGO_GAMES_DIRECTORY}/{game_id}'
        game_dir: Optional[Directory] = cast(
            Optional[Directory],
            Directory.get(self.session, name=dirname))
        if game_dir is not None:
            gamedir_json = game_dir.to_dict()
        else:
            gamedir_json = {
                'pk': next_pk,
                'parent': toplevel_json['pk'],
                'name': dirname,
                'title': f'Game {game_id}'
            }
        return (toplevel_json, gamedir_json,)

    def get_bingo_games_directory_models(self, game_id: Optional[str],
                                  next_pk: Optional[int] = None) -> Tuple[Directory, Directory]:
        """
        Get Directory models for a directory to store bingo games plus its parent directory
        """
        games_dir_parent_json, games_dir_json = self.get_bingo_games_directory(game_id, next_pk)
        games_dir_parent = self.lookup_directory(games_dir_parent_json)
        if games_dir_parent is None:
            games_dir_parent = Directory(**games_dir_parent_json)
            self.add(games_dir_parent)
            self.flush()
        games_dir = self.lookup_directory(games_dir_json)
        if games_dir is None:
            games_dir_json['parent'] = games_dir_parent
            games_dir = Directory(**games_dir_json)
            self.add(games_dir)
            self.flush()
        return (games_dir_parent, games_dir,)

    def get_lost_songs_directory(self, song: JsonObject,
                                 next_pk: Optional[int] = None) -> Tuple[JsonObject, JsonObject]:
        """
        Get Directory json for a directory to store songs plus its parent directory
        """
        if next_pk is None:
            max_dir_pk = self.session.query(func.max(Directory.pk)).scalar()
            if max_dir_pk is None:
                max_dir_pk = 1
            next_pk = 1 + max_dir_pk
        songs_dir_parent_json: JsonObject = {
            'name': self.LOST_SONGS_DIRECTORY,
            'title': self.LOST_SONGS_DIRECTORY,
            'parent': None
        }
        songs_dir_parent = self.lookup_directory(songs_dir_parent_json)
        if songs_dir_parent is None:
            songs_dir_parent_json['pk'] = next_pk # type: ignore
            next_pk += 1
        else:
            songs_dir_parent_json = songs_dir_parent.to_dict()
        album = song['album']
        if isinstance(album, int):
            album_mod = cast(Optional[Album],
                             Album.get(self.session, pk=self.pk_maps["Album"][album]))
            album = album_mod.name if album_mod is not None else 'Unknown'
        songs_dir_json: JsonObject = {
            'name': f'{songs_dir_parent_json["name"]}/{album}',
            'parent': songs_dir_parent_json['pk'],
            'title': album
        }
        songs_dir = self.lookup_directory(songs_dir_json)
        if songs_dir is None:
            songs_dir_json['pk'] = next_pk
        else:
            songs_dir_json = songs_dir.to_dict()
        return (songs_dir_parent_json, songs_dir_json,)

    def get_lost_songs_directory_models(self, song: JsonObject,
                                        next_pk: Optional[int] = None) -> Tuple[Directory,
                                                                                Directory]:
        """
        Get Directory models for a directory to store songs plus its parent directory
        """
        songs_dir_parent_json, songs_dir_json = self.get_lost_songs_directory(song, next_pk)
        songs_dir_parent = self.lookup_directory(songs_dir_parent_json)
        if songs_dir_parent is None:
            songs_dir_parent = Directory(**songs_dir_parent_json)
            self.add(songs_dir_parent)
            self.flush()
        songs_dir = self.lookup_directory(songs_dir_json)
        if songs_dir is None:
            songs_dir_json['parent'] = songs_dir_parent
            songs_dir = Directory(**songs_dir_json)
            self.add(songs_dir)
            self.flush()
        return (songs_dir_parent, songs_dir,)

    def get_clips_directory(self) -> Directory:
        """
        Get top level song clips directory
        """
        clipdir = str(self.options.clips())
        retval: Optional[Directory] = cast(
            Optional[Directory],
            Directory.get(self.session, name=clipdir))
        if retval is None:
            retval = Directory(
                name=clipdir,
                title="Clips")
            self.session.add(retval)
            self.session.flush()
        return retval

    def import_users(self, data: List) -> None:
        """
        Try to import the specified list of users
        """
        pk_map: Dict[int, int] = {}
        self.set_map("User", pk_map)
        self.log.info('Importing users...')
        self.progress.text = 'Importing users...'
        if not data:
            return
        pct = 100.0 / float(len(data))
        for index, item in enumerate(data):
            self.progress.pct = index * pct
            user = cast(
                Optional[User], User.get(
                    self.session, username=item['username']))
            user_pk: Optional[int] = None
            try:
                user_pk = item['pk']
                del item['pk']
            except KeyError:
                pass
            if 'reset_date' in item:
                # reset_date was renamed reset_expires in user schema v4
                item['reset_expires'] = item['reset_date']
                del item['reset_date']
            for field in ['last_login', 'reset_expires']:
                if field in item and item[field]:
                    item[field] = parse_date(item[field])
                    assert isinstance(item[field], datetime)
                    # Pony doesn't work correctly with timezone aware datetime
                    # see: https://github.com/ponyorm/pony/issues/434
                    item[field] = make_naive_utc(item[field])
            remove = ['bingo_tickets', 'groups']
            if user is None and user_pk and User.get(self.session, pk=user_pk) is not None:
                remove.append('pk')
            for field in remove:
                try:
                    del item[field]
                except KeyError:
                    pass
            if not 'groups_mask' in item:
                item['groups_mask'] = Group.USERS.value
            if user is None:
                user = User(**item)
                self.add(user)
            elif self.update_models:
                user.password = item['password']
                user.email = item['email']
                user.groups_mask = item['groups_mask']
                if isinstance(user.last_login, str):
                    user.last_login = parse_date(user.last_login)
                user.last_login = max_with_none(user.last_login, item['last_login'])
            self.flush()
            if user_pk:
                pk_map[user_pk] = user.pk

    # pylint: disable=too-many-branches
    def import_directories(self, items: List[JsonObject]) -> None:
        """
        Try to import the specified list of directories
        """
        self.log.info('Importing directories...')
        self.progress.text = 'Importing directories...'
        pk_map: Dict[int, int] = {}
        self.set_map("Directory", pk_map)
        if not items:
            return
        skipped = []
        pct = 100.0 / float(len(items))
        self.progress.pct = 0
        for index, item in enumerate(items):
            self.progress.pct = index * pct
            fields = self.directory_from_json(item)
            directory = self.lookup_directory(fields)
            pk = fields['pk']
            del fields['pk']
            if directory is None:
                self.log.debug('Add directory %s', fields)
                directory = Directory(**fields)
                if self.check_exists and not Path(directory.name).exists():
                    self.log.info('Skipping missing directory: "%s"',
                                  directory.name)
                    skipped.append(item)
                    continue
                self.add(directory)
            elif self.update_models:
                for key, value in fields.items():
                    if key not in ['pk', 'name']:
                        setattr(directory, key, value)
            self.flush()
            if pk is not None:
                pk_map[pk] = directory.pk
        for item in items:
            directory = self.lookup_directory(item)
            if directory is None:
                continue
            parent_pk = item.get('parent', None)
            if parent_pk is None:
                parent_pk = item.get('directory', None)
            if directory.parent is None and parent_pk is not None:
                parent = Directory.get(self.session, pk=parent_pk)
                if parent is None and parent_pk in pk_map:
                    parent = Directory.get(self.session, pk=pk_map[parent_pk])
                if parent is not None:
                    directory.parent = parent
                    self.flush()
        for item in skipped:
            directory = Directory.search_for_directory(self.session, item)
            if directory is not None:
                pk_map[item['pk']] = directory.pk

    def import_artists(self, items: List[JsonObject]) -> None:
        """
        Try to import the specified list of artists
        """
        self.log.info('Importing artists...')
        self.progress.text = 'Importing artists...'
        pk_map: Dict[int, int] = {}
        self.set_map("Artist", pk_map)
        if not items:
            return
        pct = 100.0 / float(len(items))
        for index, item in enumerate(items):
            self.progress.pct = index * pct
            fields = Artist.from_json(self.session, self.pk_maps, item)
            artist = Artist.lookup(self.session, self.pk_maps, fields)
            pk: Optional[int] = None
            if 'pk' in fields:
                pk = fields['pk']
                del fields['pk']
            if artist is None:
                artist = Artist(**fields)
                self.add(artist)
                self.flush()
            if pk is not None:
                pk_map[pk] = artist.pk

    def import_albums(self, items: List[JsonObject]) -> None:
        """
        Try to import the specified list of albums
        """
        self.log.info('Importing albums...')
        self.progress.text = 'Importing albums...'
        pk_map: Dict[int, int] = {}
        self.set_map("Album", pk_map)
        if not items:
            return
        pct = 100.0 / float(len(items))
        for index, item in enumerate(items):
            self.progress.pct = index * pct
            fields = Album.from_json(self.session, self.pk_maps, item)
            album = Album.lookup(self.session, self.pk_maps, fields)
            pk = None
            if 'pk' in fields:
                pk = fields['pk']
                del fields['pk']
            if album is None:
                album = Album(**fields)
                self.add(album)
                self.flush()
                self.log.debug('Added album: %s %d %s', pk, album.pk, fields)
            if pk is not None:
                pk_map[pk] = album.pk

    def import_songs(self, items: List[JsonObject], game_id: Optional[str]) -> None:
        """
        Try to import the specified list of songs
        """
        self.log.info('Importing songs...')
        self.progress.text = 'Importing songs...'
        pk_map: Dict[int, int] = {}
        self.set_map("Song", pk_map)
        if not items:
            return
        skipped: List[JsonObject] = []
        pct = 100.0 / float(len(items))
        for index, item in enumerate(items):
            self.progress.pct = index * pct
            self.import_one_song(item, pk_map, skipped)
        for item in skipped:
            alternative = Song.search_for_song(self.session, self.pk_maps, item)
            if alternative:
                self.log.debug('Found alternative for %s missing song %s',
                               alternative.pk, item)
                pk_map[item['pk']] = alternative.pk
            else:
                self.log.debug('Adding song as failed to find an alterative: %s', item)
                fields = Song.from_json(self.session, self.pk_maps, item)
                if game_id is None:
                    _, games_dir = self.get_lost_songs_directory_models(fields)
                else:
                    _, games_dir = self.get_bingo_games_directory_models(game_id)
                if 'directory' not in fields or fields['directory'] is None:
                    fields['directory'] = games_dir
                if 'pk' in fields:
                    del fields['pk']
                song = Song(**fields)
                self.add(song)
                self.flush()
                if 'pk' in item:
                    pk_map[item['pk']] = song.pk

    def import_one_song(self, item: JsonObject, pk_map: Dict[int, int],
                        skipped: List[JsonObject]) -> Optional[Song]:
        """
        Import a song into the database
        """
        fields = Song.from_json(self.session, self.pk_maps, item)
        song: Optional[Song] = None
        if fields['directory'] is not None:
            song = cast(Optional[Song], Song.get(
                self.session, directory=fields['directory'],
                filename=fields['filename']))
        if song is None:
            song = Song.search_for_song(self.session, self.pk_maps, fields)
        skip = False
        if fields['directory'] is None:
            self.log.warning('Failed to find parent %s for song: "%s"',
                             item.get('directory', None), fields['filename'])
            self.log.debug('item=%s', item)
            self.log.debug('fields=%s', item)
            skip = True
        elif self.check_exists:
            dirname = fields['directory'].absolute_path(self.options)
            filename = dirname.joinpath(fields['filename'])
            if not filename.exists():
                self.log.debug('Skipping song as MP3 file not found: %s',
                               fields)
                skip = True
        if skip:
            alternative = Song.search_for_song(self.session, self.pk_maps, item)
            if alternative:
                pk_map[item['pk']] = alternative.pk
            else:
                skipped.append(item)
            return None
        pk = None
        if 'pk' in fields:
            pk = fields['pk']
            del fields['pk']
        if song is None:
            self.log.debug("Add song %s", fields)
            song = Song(**fields)
            self.add(song)
            self.flush()
        elif self.update_models:
            for key, value in fields.items():
                if key not in ['filename']:
                    setattr(song, key, value)
        if pk is not None:
            pk_map[pk] = song.pk
        return song

    def import_games(self, items: List[JsonObject]) -> None:
        """
        Try to import the list of games
        """
        self.log.info('Importing games...')
        pk_map: Dict[int, int] = {}
        self.set_map("Game", pk_map)
        if not items:
            return
        pct = 100.0 / float(len(items))
        for index, item in enumerate(items):
            self.progress.pct = index * pct
            game = Game.lookup(self.session, item)
            if game:
                self.log.info('Skipping game "%s" as it already exists', item["id"])
                continue
            for field in ['start', 'end']:
                item[field] = parse_date(item[field])
                # Pony doesn't work correctly with timezone aware datetime
                # see: https://github.com/ponyorm/pony/issues/434
                item[field] = make_naive_utc(item[field])
            for field in ['bingo_tickets', 'tracks']:
                try:
                    del item[field]
                except KeyError:
                    pass
            try:
                pk = item['pk']
                del item['pk']
            except KeyError:
                pk = None
            game = Game(**item)
            self.add(game)
            self.flush()
            if pk is not None:
                pk_map[pk] = game.pk

    def import_tracks(self, items: List[JsonObject], game_id: Optional[str]) -> None:
        """
        Try to import all of the tracks in the provided list
        """
        self.log.info('Importing tracks...')
        self.progress.text = 'Importing tracks...'
        if not items:
            return
        pct = 100.0 / len(items)
        for index, item in enumerate(items):
            self.progress.pct = index * pct
            self.import_track(item, game_id)

    def import_track(self, item: JsonObject, game_id: Optional[str]) -> None:
        """
        Try to import  the track described in 'item'.
        """
        if item['game'] not in self.pk_maps["Game"]:
            self.log.info('Skipping track %s as game %d has not been imported',
                          item.get('pk', None), item['game'])
            return
        if 'song' not in item:
            # v1 database format does not have a reference to the song PK
            item['song'] = Song.search_for_song(self.session, self.pk_maps, item)
            assert item['song'] is not None
        fields = Track.from_json(self.session, self.pk_maps, item)
        if fields['game'] is None:
            self.log.warning('Failed to find game for track: %s', fields)
            self.log.debug('%s', item)
            return
        if fields['song'] is None and 'filename' in fields:
            self.log.warning(
                'Failed to find song, adding it to Bingo Games directory: %s',
                item)
            song_fields = Song.from_json(self.session, self.pk_maps, item)
            if game_id is None:
                _, games_dir = self.get_lost_songs_directory_models(song_fields)
            else:
                _, games_dir = self.get_bingo_games_directory_models(game_id)
            song_fields['directory'] = games_dir
            for field in list(fields.keys()) + ["bingo_tickets", "prime"]:
                if field in song_fields:
                    del song_fields[field]
            fields['song'] = Song(**song_fields)
            self.session.add(fields['song'])
        if 'pk' in fields:
            del fields['pk']
        if fields['song'] is None:
            self.log.error(item)
            self.log.error(fields)
        assert fields['song'] is not None
        track = Track(**fields)
        self.add(track)
        self.flush()
        if 'pk' in item:
            self.pk_maps["Track"][item['pk']] = track.pk

    # pylint: disable=too-many-statements
    def import_bingo_tickets(self, items: List[JsonObject]) -> None:
        """
        Import the list of Bingo tickets. If the game has not been imported
        by this Importer, the ticket is skipped.
        """
        self.log.info('Importing bingo tickets...')
        self.progress.text = 'Importing bingo tickets...'
        pk_map: Dict[int, int] = {}
        self.set_map("BingoTicket", pk_map)
        if not items:
            return
        pct = 100.0 / float(len(items))
        new_tickets: Dict[int, BingoTicket] = {}
        for index, item in enumerate(items):
            self.progress.pct = index * pct
            self.log.debug("Importing BingoTicket %d", index)
            try:
                game_pk = item['game']
                if game_pk not in self.pk_maps["Game"]:
                    self.log.info("Skipping Bingo Ticket as game %d has not been imported",
                                  game_pk)
                    self.log.debug("Games: %s", self.pk_maps["Game"])
                    continue
                game_pk = self["Game"][game_pk]
            except KeyError as err:
                self.log.warning(
                    'Failed to find primary key for game %s for ticket %s: %s',
                    item.get('game', None), item.get('pk', None), err)
                self.log.debug('%s', item)
                continue
            game = cast(Optional[Game], Game.get(self.session, pk=game_pk))
            if not game:
                self.log.error('Failed to find game %d for ticket %s',
                               game_pk, item.get('pk', None))
                continue
            user = None
            if item.get('user', None):
                try:
                    user_pk = self['User'][item['user']]
                except KeyError:
                    user_pk = item['user']
                user = User.get(self.session, pk=user_pk)
                if not user:
                    self.log.warning(
                        'failed to find user %s for ticket %s in game %s',
                        item.get('user', None), item.get('pk', None),
                        item.get('game', None))
            # The database field "order" has the list of Track primary keys.
            # The JSON representation of BingoTicket should have a property called
            # "tracks" which is an ordered list of Track.pk. If the JSON
            # file has an "order" property, it can be used as a fallback.
            if 'order' in item and 'tracks' not in item:
                item['tracks'] = item['order']
            tracks: List[BingoTicketTrack] = []
            for idx, trk_pk in enumerate(item['tracks']):
                if trk_pk not in self["Track"]:
                    self.log.warning(
                        "Skipping BingoTicket %s, as ticket %d has not been imported",
                        item.get('pk', None), trk_pk)
                    continue
                trk_pk = self["Track"][trk_pk]
                if not Track.exists(self.session, pk=trk_pk):
                    self.log.warning(
                        'failed to find track %d for ticket %s in game %s',
                        trk_pk, item.get('pk', None), game.id)
                    continue
                btt = BingoTicketTrack(order=idx, track_pk=trk_pk)
                tracks.append(btt)
            item['game'] = game
            item['user'] = user
            item['tracks'] = tracks
            if 'order' in item:
                del item['order']
            try:
                pk = item['pk']
                del item['pk']
            except KeyError:
                self.log.debug('KeyError: %s', item)
                pk = None
            ticket = BingoTicket(**item)
            self.add(ticket)
            if pk is not None:
                new_tickets[pk] = ticket
            self.log.debug("BingoTicket %d done", index)
        self.flush()
        for pk, ticket in new_tickets.items():
            pk_map[pk] = ticket.pk

    def directory_from_json(self, item: JsonObject) -> JsonObject:
        """
        converts any fields in item into a dictionary ready for use with Directory constructor
        """
        retval: JsonObject = {
            'name': clean_string(item['name']),
            'title': clean_string(item['title']),
            'parent': None
        }
        if 'pk' in item:
            retval['pk'] = item['pk']
        parent = item.get('parent', None)
        if parent is None:
            parent = item.get('directory', None)
        if parent is not None:
            retval['parent'] = self.lookup_directory(dict(pk=parent)) # type: ignore
        model = cast(Optional[Directory],
                     Directory.get(self.session, name=retval['name']))
        if model is not None:
            if 'pk' in retval:
                self.pk_maps["Directory"][retval['pk']] = model.pk # type: ignore
            retval['parent'] = model.parent
            if parent is not None and model.parent is not None:
                self.pk_maps["Directory"][parent] = model.parent.pk
            return retval
        if '\\' in retval['name']: # type: ignore
            retval['name'] = PureWindowsPath(retval['name']).as_posix() # type: ignore
        clipdir = self.options.clips().as_posix()
        if clipdir[-1] == '/':
            clipdir = clipdir[:-1]
        name = cast(str, retval['name'])
        if name.startswith("Clips/"):
            name = name[len("Clips/"):]
        if name.startswith(clipdir):
            name = name[len(clipdir):]
        if (self.imported_options is not None and
            name.startswith(self.imported_options['clip_directory'])):
            name = name[len(self.imported_options['clip_directory']):]
        if name and name[0] == "/":
            name = name[1:]
        if name == "":
            name = "."
        if not name.startswith(self.BINGO_GAMES_DIRECTORY):
            name = f'{clipdir}/{name}'
        retval['name'] = name
        return retval

    def lookup_directory(self, item: JsonObject) -> Optional[Directory]:
        """
        Check if this directory is already in the database
        """
        self.log.debug('lookup_directory %s', item)
        pk_map = self.pk_maps["Directory"]
        retval: Optional[Directory] = None
        try:
            retval = cast(Optional[Directory],
                          Directory.get(self.session, pk=pk_map[item['pk']]))
        except KeyError as err:
            self.log.debug("KeyError %s", err)
        if retval is None and 'name' in item:
            retval = cast(Optional[Directory],
                          Directory.get(self.session, name=clean_string(item['name'])))
        return cast(Optional[Directory], retval)
