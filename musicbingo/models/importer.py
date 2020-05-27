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
from pathlib import Path, PurePath, PosixPath, PurePosixPath, PureWindowsPath
import time
from typing import Any, Dict, List, Optional, cast

from sqlalchemy.orm.session import Session  # type: ignore

from musicbingo.options import Options
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.utils import (
    parse_date, make_naive_utc, flatten, from_isodatetime,
    to_iso_datetime
)

from .bingoticket import BingoTicket, BingoTicketTrack
from .directory import Directory
from .game import Game
from .group import Group
from .modelmixin import ModelMixin, JsonObject, PrimaryKeyMap
from .song import Song
from .track import Track
from .user import User

def max_with_none(a, b):
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

    def __init__(self, options: Options, session: Session):
        self.options = options
        self.session = session
        self.log = logging.getLogger('musicbingo.models')
        self.pk_maps: PrimaryKeyMap = {}
        self.added: Dict[str, int] = {}
        self.check_exists = False
        self.update_models = False
        for model in ["User", "Directory", "Song", "Track", "BingoTicket", "Game"]:
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

    def add(self, model: "ModelMixin") -> None:
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

    def import_database(self, filename: Path) -> None:
        """
        Import JSON file into database
        """
        self.log.info('Importing database from file "%s"', filename)
        with filename.open('r') as input:
            data = json.load(input)

        if 'User' not in data and 'Songs' not in data and 'Games' in data and 'Tracks' in data:
            self.import_game_data(data)
        else:
            self.import_json(data)
        self.session.commit()

    def import_game_data(self, data: JsonObject) -> None:
        """
        Import games into database.
        This is used to import "game-<game-id>.json" files or the output from the
        "export-game" command.
        """
        self.rename_pk_aliases(data)
        if 'Games' not in data:
            self.log.error("A game must be provided to import_game_data")
            return
        self.rename_pk_aliases(data)
        self.log.debug("Processing tracks...")
        lost: Optional[Directory] = cast(
            Optional[Directory],
            Directory.get(self.session, name="lost+found"))
        if lost is None:
            lost = Directory(
                name="lost+found",
                title="lost & found",
                artist="Orphaned songs")
            self.session.add(lost)
        game = data["Games"][0]
        song_dir: Optional[Directory] = cast(
            Optional[Directory],
            Directory.get(self.session, name=game['id'], parent=lost))
        if 'Songs' in data:
            Song.import_json(self, data['Songs'])  # type: ignore
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
                        title=game['title'],
                        artist="Unknown")
                    self.session.add(song_dir)
                    self.session.flush()
                song_fields = Song.from_json(self.session, self.pk_maps, track)
                song_fields['directory'] = song_dir
                song = Song(**song_fields)
                self.session.add(song)
                self.session.flush()
                self.log.info('Adding song "%s" (%d) to lost+found directory', song.title, song.pk)
            self.pk_maps["Song"][track['pk']] = song.pk
            self.pk_maps["Directory"][song.directory.pk] = song.directory.pk
            track["song"] = song.pk
        self.import_games(data['Games'])  # type: ignore
        self.import_tracks(data['Tracks'])  # type: ignore
        if 'BingoTickets' in data:
            self.import_bingo_tickets(data['BingoTickets'])  # type: ignore
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
                            data[field] = data[alias]
                            del data[alias]

    def import_json(self, data: JsonObject) -> None:
        """
        Import the models found in the data.
        It will import users, directories, songs, games, tracks and bingo tickets.
        """
        self.rename_pk_aliases(data)
        if 'Users' in data:
            self.import_users(data["Users"])
        if 'Directories' in data:
            self.import_directories(data["Directories"])
        elif 'Directorys' in data:
            self.import_directories(data["Directorys"])
        if 'Songs' in data:
            self.import_songs(data["Songs"])
        if 'Games' not in data:
            return
        #tracks: Dict[int, JsonObject] = {}
        #if 'Tracks' in data:
        #    max_pk = 0
        #    for item in data['Tracks']:
        #        pk = item.get('pk', None)
        #        if pk is not None:
        #            max_pk = max(max_pk, pk)
        #    for item in data['Tracks']:
        #        track = Track.from_json(item)
        #        pk = track.get('pk', None)
        #        if pk is None:
        #            pk = max_pk
        #            max_pk += 1
        #            track['pk'] = pk
        #        tracks.append(track)
        self.import_games(data["Games"])
        if 'Tracks' in data:
            self.import_tracks(data['Tracks'])
        if 'BingoTickets' in data:
            self.import_bingo_tickets(data['BingoTickets'])

    def import_game_tracks(self, filename: Path, game_id: str) -> None:
        """
        Import an old gameTracks.json file into database.
        This format has a list of songs, in playback order.
        """
        self.log.info('Importing gameTracks.json from file "%s"',
                      filename)
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
            self.log.error('Failed to auto-detect game ID')
            return
        self.log.info('Game ID: %s', game_id)
        if Game.exists(self.session, id=game_id):
            self.log.error("Game has aleady been imported")
            return
        data = self.translate_game_tracks(filename, game_id)
        self.session.commit()
        self.log.info("Import directories")
        self.import_directories(data['Directories'])  # type: ignore
        self.log.info("Import songs")
        self.import_songs(data['Songs'])  # type: ignore
        self.log.info("Import games")
        self.import_games(data['Games'])  # type: ignore
        self.log.info("Import tracks")
        self.import_tracks(data['Tracks'])  # type: ignore
        if 'BingoTickets' in data:
            self.log.info("Import Bingo tickets")
            self.import_bingo_tickets(data['BingoTickets'])  # type: ignore


    def translate_game_tracks(self, filename: Path,
                              game_id: str) -> JsonObject:
        """
        Load a gameTracks.json and create an object that matches the current
        export-game format.
        """
        with filename.open('r') as input:
            tracks = json.load(input)

        if isinstance(tracks, dict) and "Tracks" in tracks and "Games" in tracks:
            return self.translate_v3_game_tracks(filename, tracks, game_id)
        return self.translate_v1_v2_game_tracks(filename, tracks, game_id)

    def translate_v1_v2_game_tracks(self, filename: Path,
                                    tracks: List[JsonObject],
                                    game_id: str) -> JsonObject:
        """
        Load a v1 or v2 gameTracks.json and create an object that matches the
        current export-game format.
        """
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
        clip_dir = self.options.clips()
        position = 0
        lost: Optional[Directory] = cast(
            Optional[Directory],
        Directory.get(self.session, name="lost+found"))
        if lost is None:
            lost = Directory(
                name="lost+found",
                title="lost & found",
                artist="Orphaned songs")
            self.session.add(lost)
            self.session.flush()
        data["Directories"].append(lost.to_dict())  # type: ignore
        lost_song_dir: Optional[Directory] = cast(
            Optional[Directory],
            Directory.get(self.session, name=game_id, parent=lost))
        for idx, track in enumerate(tracks):
            song = {
                'title': '',
                'filename': '',
                'channels': 2,
                'sample_rate': 44100,
                'sample_width': 16,
                'bitrate': self.options.bitrate,
            }
            song.update(track)
            for field in ['prime', 'start_time', 'number']:
                if field in song:
                    del song[field]
            fullpath: Optional[PurePath] = None
            if 'fullpath' in song:
                if '\\' in cast(str, song['fullpath']):
                    fullpath = PureWindowsPath(cast(str, song['fullpath']))
                else:
                    fullpath = Path(cast(str, song['fullpath']))
                del song['fullpath']
            elif 'filepath' in song:
                if '\\' in cast(str, song['filepath']):
                    fullpath = PureWindowsPath(cast(str, song['filepath']))
                else:
                    fullpath = PurePosixPath(cast(str, song['filepath']))
                del song['filepath']
            else:
                fullpath = Path(cast(str, song['filename']))
            song['filename'] = fullpath.name
            song_dir = cast(
                Optional[Directory],
                Directory.get(self.session, name=str(fullpath.parent)))
            if song_dir is None:
                dirname = clip_dir.joinpath(fullpath)
                song_dir = cast(
                    Optional[Directory],
                    Directory.get(self.session, name=str(dirname.parent)))
            if song_dir is None:
                dirname = Path(self.options.clip_directory).joinpath(fullpath)
                song_dir = cast(
                    Optional[Directory],
                    Directory.get(self.session, name=str(dirname.parent)))
            if song_dir is None:
                song_dir = Directory.search_for_directory(self.session, song)
            if song_dir is None:
                if lost_song_dir is None:
                    lost_song_dir = Directory(
                        parent=lost,
                        name=game_id,
                        title=game_id,
                        artist="Unknown")
                    self.session.add(lost_song_dir)
                    self.session.flush()
                    data["Directories"].append(lost_song_dir.to_dict())  # type: ignore
                song_dir = lost_song_dir
            assert song_dir is not None
            song['directory'] = song_dir.pk
            if 'song' in track:
                song["pk"] = track["song"]
            elif 'song_id' in track:
                song["pk"] = track["song_id"]
                del song["song_id"]
                del track["song_id"]
            else:
                song["pk"] = 100 + idx
            title = cast(str, song['title'])
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

    def translate_v3_game_tracks(self, filename: Path,
                                 data: JsonObject,
                                 game_id: str) -> JsonObject:
        """
        Load a v3 gameTracks.json and create an object that matches the current
        export-game format.
        """
        retval = copy.deepcopy(data)
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
            song_mod = Song.search_for_song(self.session, self.pk_maps, song)
            if song_mod is not None:
                song["pk"] = song_mod.pk
                song["directory"] = song_mod.directory.pk
                directories[song_mod.directory.pk] = song_mod.directory
                track["song"] = song_mod.pk
            retval["Songs"].append(song)
            retval["Tracks"].append(track)
        retval["Directories"] = [d.to_dict() for d in directories.values()]
        return retval

    def import_users(self, data: List) -> None:
        pk_map: Dict[int, int] = {}
        self.set_map("User", pk_map)
        for item in data:
            user = cast(
                Optional[User], User.get(
                    self.session, username=item['username']))
            user_pk: Optional[int] = None
            try:
                user_pk = item['pk']
                del item['pk']
            except KeyError:
                pass
            if item['last_login']:
                item['last_login'] = parse_date(item['last_login'])
                assert isinstance(item['last_login'], datetime)
                # Pony doesn't work correctly with timezone aware datetime
                # see: https://github.com/ponyorm/pony/issues/434
                item['last_login'] = make_naive_utc(item['last_login'])
            if 'reset_date' in item:
                # reset_date was renamed reset_expires in user schema v4
                item['reset_expires'] = item['reset_date']
                del item['reset_date']
            remove = ['bingo_tickets', 'groups']
            # if user is None and user_pk and User.does_exist(imp.session, pk=user_pk):
            if user is None and user_pk and User.get(self.session, pk=user_pk) is not None:
                remove.append('pk')
            for field in remove:
                try:
                    del item[field]
                except KeyError:
                    pass
            if not 'groups_mask' in item:
                item['groups_mask'] = Group.users.value
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

    def import_directories(self, items: List[JsonObject]) -> None:
        pk_map: Dict[int, int] = {}
        self.set_map("Directory", pk_map)
        skipped = []
        for item in items:
            fields = self.directory_from_json(item)
            directory = self.lookup_directory(fields)
            try:
                pk = fields['pk']
                del fields['pk']
            except KeyError:
                pk = None
            if directory is None:
                # print(fields)
                directory = Directory(**fields)
                if self.check_exists:
                    if not directory.absolute_path(self.options).exists():
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
            parent_pk = item.get('Parent', None)
            if parent_pk is None:
                parent_pk = item.get('Directory', None)
            if directory.parent is None and parent_pk is not None:
                parent = Directory.get(self.session, pk=parent_pk)
                if parent is None and parent_pk in pk_map:
                    parent = Directory.get(self.session, pk=pk_map[parent_pk])
                if parent is not None:
                    directory.directory = parent
                    self.flush()
        for item in skipped:
            directory = Directory.search_for_directory(self.session, item)
            if directory is not None:
                pk_map[item['pk']] = directory.pk

    def import_songs(self, items: List[JsonObject]) -> None:
        pk_map: Dict[int, int] = {}
        self.set_map("Song", pk_map)
        skipped = []
        empty = self.session.query(Song).first() is None
        for item in items:
            fields = Song.from_json(self.session, self.pk_maps, item)
            #song = cls.lookup(fields, pk_maps)
            song = Song.search_for_song(self.session, self.pk_maps, fields) if not empty else None
            skip = False
            if fields['directory'] is None:
                self.log.warning('Failed to find parent %s for song: "%s"',
                                 item.get('directory', None), fields['filename'])
                self.log.debug('item=%s', item)
                self.log.debug('fields=%s', item)
                skip = True
            elif self.check_exists == True:
                dirname = fields['directory'].absolute_path(self.options)
                filename = dirname.joinpath(fields['filename'])
                if not filename.exists():
                    skip = True
            if skip:
                alternative = Song.search_for_song(self.session, self.pk_maps, item)
                if alternative:
                    pk_map[item['pk']] = alternative.pk
                else:
                    skipped.append(item)
                continue
            pk = None
            if 'pk' in fields:
                pk = fields['pk']
                del fields['pk']
            if song is None:
                song = Song(**fields)
                self.add(song)
            elif self.update_models:
                for key, value in fields.items():
                    if key not in ['filename']:
                        setattr(song, key, value)
            self.flush()
            if pk is not None:
                pk_map[pk] = song.pk
        for item in skipped:
            alternative = Song.search_for_song(self.session, self.pk_maps, item)
            if alternative:
                self.log.debug('Found alternative for %s missing song %s',
                               alternative.pk, item)
                pk_map[item['pk']] = alternative.pk
            else:
                self.log.debug('Adding song as failed to find an alterative: %s', item)
                lost = Directory.get(self.session, name="lost+found")
                if lost is None:
                    lost = Directory(
                        name="lost+found",
                        title="lost & found",
                        artist="Orphaned songs")
                    self.session.add(lost)
                fields = Song.from_json(self.session, self.pk_maps, item)
                if 'directory' not in fields or fields['directory'] is None:
                    fields['directory'] = lost
                if 'pk' in fields:
                    del fields['pk']
                song = Song(**fields)
                self.add(song)
                self.flush()
                if 'pk' in item:
                    pk_map[item['pk']] = song.pk

    def import_games(self, items: List[JsonObject]) -> None:
        pk_map: Dict[int, int] = {}
        self.set_map("Game", pk_map)
        for item in items:
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

    def import_tracks(self, items: List[JsonObject]) -> None:
        for item in items:
            self.import_track(item)

    def import_track(self, item: JsonObject) -> None:
        """
        Try to import  the track described in 'item'.
        """
        if item['game'] not in self.pk_maps["Game"]:
            self.log.info('Skipping track %s as game %d has not been imported',
                          item.get('pk', None), item['game'])
            return
        fields = Track.from_json(self.session, self.pk_maps, item)
        if fields['game'] is None:
            self.log.warning('Failed to find game for track: %s', fields)
            self.log.debug('%s', item)
            return
        if fields['song'] is None and 'filename' in fields:
            self.log.warning('Failed to find song, adding it to lost+found directory: {0}'.format(item))
            lost = Directory.get(self.session, name="lost+found")
            if lost is None:
                lost = Directory(
                    name="lost+found",
                    title="lost & found",
                    artist="Orphaned songs")
                self.session.add(lost)
            song_fields = Song.from_json(self.session, self.pk_maps, item)
            song_fields['directory'] = lost
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

    def import_bingo_tickets(self, items: List[JsonObject]) -> None:
        """
        Import the list of Bingo tickets. If the game has not been imported
        by this Importer, the ticket is skipped.
        """
        pk_map: Dict[int, int] = {}
        self.set_map("BingoTicket", pk_map)
        for item in items:
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
            #    item['order'] = [t.pk for t in item['tracks']]
            try:
                pk = item['pk']
                del item['pk']
            except KeyError:
                self.log.debug('KeyError: %s', item)
                pk = None
            ticket = BingoTicket(**item)
            self.add(ticket)
            self.flush()
            if pk is not None:
                pk_map[pk] = ticket.pk

    def directory_from_json(self, item: JsonObject) -> JsonObject:
        """
        converts any fields in item into a dictionary ready for use Track constructor
        """
        retval = {}
        for field, value in item.items():
            if field not in ['directories', 'songs', 'directory', 'parent']:
                retval[field] = value
        clipdir = str(self.options.clips())
        if retval['name'].startswith(clipdir):
            retval['name'] = retval['name'][len(clipdir):]
        if retval['name'] == "":
            retval['name'] = "."
        parent = item.get('parent', None)
        if parent is None:
            parent = item.get('directory', None)
        if parent is not None:
            retval['parent'] = self.lookup_directory(dict(pk=parent))
        return retval

    def lookup_directory(self, item: JsonObject) -> Optional[Directory]:
        """
        Check if this directory is already in the database
        """
        pk_map = self.pk_maps["Directory"]
        try:
            rv = Directory.get(self.session, pk=item['pk'])
            if rv is None and item['pk'] in pk_map:
                rv = Directory.get(self.session, pk=pk_map[item['pk']])
        except KeyError:
            rv = None
        if rv is None and 'name' in item:
            clipdir = str(self.options.clips())
            name = item['name']
            if name.startswith(clipdir):
                name = name[len(clipdir):]
            if name == "":
                name = "."
            rv = Directory.get(self.session, name=name)
        return cast(Optional[Directory], rv)
