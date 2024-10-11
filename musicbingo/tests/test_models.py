"""
Unit tests for database models
"""

import datetime
import io
import json
import logging
from os import stat_result
from pathlib import Path, PurePosixPath
import time
from typing import cast, Dict, Iterable, List, NamedTuple, Optional, Type, Union
import unittest

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from musicbingo import models, utils
from musicbingo.models.db import (
    DatabaseConnection, DatabaseSession, session_scope
)
from musicbingo.models.importer import Importer
from musicbingo.models.modelmixin import JsonObject, ModelMixin
from musicbingo.uuidmixin import UuidMixin
from musicbingo.options import DatabaseOptions, Options
from musicbingo.progress import Progress
from musicbingo.schemas import JsonSchema, validate_json

from .fixture import fixture_filename
from .modelsunittest import ModelsUnitTest

DatabaseOptions.DEFAULT_FILENAME = None
Options.INI_FILENAME = None

class ClipOptions(Options):
    """
    Wrapper around Options that modifies clip location
    """
    def clips(self) -> Path:
        """Return directory containing song clips"""
        return cast(Path, PurePosixPath(self.clip_directory))

class ExpectedImportResult(NamedTuple):
    """
    Tuple used to contain the expected number of objects imported during a test
    """
    bingo_tickets: int = 0
    albums: int = 0
    artists: int = 0
    directories: int = 0
    games: int = 0
    songs: int = 0
    tracks: int = 0
    users: int = 0

class TestDatabaseModels(ModelsUnitTest):
    """
    Unit tests for database models
    """

    EXPECTED_OUTPUT: Optional[Path] = None # Path(__file__).parent / "expected"

    def setUp(self) -> None:
        """called before each test"""
        db_opts = DatabaseOptions(database_provider='sqlite', database_name=':memory:')
        self.options = ClipOptions(clip_directory="/home/bingo/Clips", database=db_opts)

        # self.options.exists = False
        logging.getLogger().setLevel(logging.ERROR)
        log_format = (r"%(relativeCreated)06d:%(levelname)s:" +
                      r"%(filename)s@%(lineno)d:%(funcName)s  %(message)s")
        logging.basicConfig(format=log_format)

    def tearDown(self) -> None:
        """called after each test"""
        DatabaseConnection.close()

    def load_clips_fixture(self) -> Engine:
        """
        Load the fixture containing the song clips used by the tests
        """
        connect_str = "sqlite:///:memory:"
        engine = create_engine(connect_str, echo=False)
        self.load_fixture(engine, 'clips-db.sql')
        return engine

    def test_v1_export(self) -> None:
        """
        Test exporting a database to a JSON file from the version 1 Schema
        """
        self.export_test(1)

    def test_v2_export(self) -> None:
        """
        Test exporting a database to a JSON file from the version 2 Schema
        """
        self.export_test(2)

    def test_v3_export(self) -> None:
        """
        Test exporting a database to a JSON file from the version 3 Schema
        """
        self.export_test(3)

    def test_v4_export(self) -> None:
        """
        Test exporting a database to a JSON file from the version 4 Schema
        """
        self.export_test(4)

    def test_v5_export(self) -> None:
        """
        Test exporting a database to a JSON file from the version 5 Schema
        """
        self.export_test(5)

    def test_v6_export(self) -> None:
        """
        Test exporting a database to a JSON file from the version 6 Schema
        """
        self.export_test(6)

    def test_v1_import(self) -> None:
        """
        Test importing a v1 file into the current database Schema
        """
        self.import_test(1)

    def test_v2_import(self) -> None:
        """
        Test importing a v2 file into the current database Schema
        """
        self.import_test(2)

    def test_v3_import(self) -> None:
        """
        Test importing a v3 file into the current database Schema
        """
        self.import_test(3)

    def test_v4_import(self) -> None:
        """
        Test importing a v4 file into the current database Schema
        """
        self.import_test(4)

    def test_v5_import(self) -> None:
        """
        Test importing a v5 file into the current database Schema
        """
        self.import_test(5)

    def test_v6_import(self) -> None:
        """
        Test importing a v6 file into the current database Schema
        """
        self.import_test(6)

    def test_fixture_loading(self) -> None:
        """
        tests that the load fixture function correctly handles an input SQL file
        """
        insert_tests: list[str] = [
            #pylint: disable-next=line-too-long
            r"""14,1,'10 The Six Million Dollar Man.mp3','The Six Million Dollar Man',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','.opQ.nJbc"K!"RUCq6p,',2""",
            #pylint: disable-next=line-too-long
            r"""15,1,'11 M-A-S-H.mp3','M*A*S*H',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]',':?''.NjdT22YM:S:j<0i-',4""",
            #pylint: disable-next=line-too-long
            r"""16,1,'12 The Waltons.mp3','The Waltons',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','TW28C>mjfVPj4%P]S]L''',8""",
        ]
        exp_cols1: list[str | int | None] = [
            14,
            1,
            '10 The Six Million Dollar Man.mp3',
            'The Six Million Dollar Man',
            30016,
            2,
            44100,
            16,
            256,
            'All-Time Top 100 TV Themes [Disc 2]',
            '.opQ.nJbc"K!"RUCq6p,',
            2
        ]
        exp_cols2: list[str | int | None] = [
            15,
            1,
            '11 M-A-S-H.mp3',
            'M*A*S*H',
            30016,
            2,
            44100,
            16,
            256,
            'All-Time Top 100 TV Themes [Disc 2]',
            ":?'.NjdT22YM:S:j<0i-",
            4
        ]
        exp_cols3: list[str | int | None] = [
            16,
            1,
            '12 The Waltons.mp3',
            'The Waltons',
            30016,
            2,
            44100,
            16,
            256,
            'All-Time Top 100 TV Themes [Disc 2]',
            "TW28C>mjfVPj4%P]S]L'",
            8
        ]
        expected_data: List[List[str | int | None]] = [exp_cols1, exp_cols2, exp_cols3]
        self.maxDiff = None
        for text, expected in zip(insert_tests, expected_data):
            names, params = ModelsUnitTest.split_columns(text)
            expected_params: dict[str, Union[str, int, None]] = {}
            expected_names: list[str] = []
            for idx, value in enumerate(expected, start=1):
                expected_params[f'col_{idx:02d}'] = value
                expected_names.append(f':col_{idx:02d}')
            self.assertDictEqual(expected_params, params)
            self.assertEqual(','.join(expected_names), names)

        connect_str = "sqlite:///:memory:"
        engine: Engine = create_engine(connect_str, echo=False)
        self.load_fixture(engine, 'tv-themes-v5.sql')
        DatabaseConnection.bind(self.options.database, engine=engine, debug=False)
        with models.db.session_scope() as dbs:
            for cols in expected_data:
                song: models.Song | None = cast(
                    models.Song | None, models.Song.get(dbs, pk=cols[0]))
                assert song is not None
                self.assertEqual(song.filename, cols[2])
                self.assertEqual(song.title, cols[3])
                self.assertEqual(song.duration, cols[4])
                self.assertEqual(song.channels, cols[5])
                self.assertEqual(song.sample_rate, cols[6])
                self.assertEqual(song.sample_width, cols[7])
                self.assertEqual(song.bitrate, cols[8])
                self.assertEqual(song.album.name, cols[9])
                self.assertEqual(song.uuid, cols[10])
                # check that UUID can be parsed
                uuid = UuidMixin.str_to_uuid(song.uuid)
                self.assertEqual(models.Song.str_from_uuid(uuid), cols[10])

    def import_test(self, schema_version) -> None:
        """
        Run import test
        """
        DatabaseConnection.bind(self.options.database, debug=False)
        json_filename: Path = fixture_filename(f"tv-themes-v{schema_version}.json")
        with models.db.session_scope() as dbs:
            imp = Importer(self.options, dbs, Progress())
            imp.import_database(json_filename)
        self.create_expected_json(f"expected-tv-themes-v{schema_version}.json", imp)
        json_filename = fixture_filename(f"expected-tv-themes-v{schema_version}.json")
        with json_filename.open('rt', encoding='utf-8') as src:
            expected = json.load(src)
        self.compare_import_results(schema_version, imp, expected, True)

    def create_expected_json(self, filename: str, imp: Importer) -> None:
        """
        Create a JSON file of the expected results of an import
        """
        if self.EXPECTED_OUTPUT is None:
            return
        tables: list[type[ModelMixin]] = [
            models.User, models.Album, models.Artist, models.Directory,
            models.Song, models.Game, models.Track, models.BingoTicket
        ]
        pk_maps: Dict[str, Dict[int, int]] = {}
        for table in tables:
            pk_maps[table.__tablename__] = {}  # type: ignore
            for key, value in imp[table.__tablename__].items():  # type: ignore
                pk_maps[table.__tablename__][value] = key  # type: ignore
        destination = self.EXPECTED_OUTPUT / filename
        with models.db.session_scope() as dbs:
            with destination.open("wt", encoding='utf-8') as dst:
                dst.write('{\n')
                for table in tables:
                    contents: List[JsonObject] = []
                    for item in table.all(dbs):  # type: ignore
                        data = item.to_dict()
                        try:
                            data['pk'] = pk_maps[table.__tablename__][item.pk]   # type: ignore
                        except KeyError:
                            # item was already in database and was not imported
                            continue
                        self.map_primary_keys(pk_maps, tables, item, data)
                        contents.append(data)  # type: ignore
                    dst.write(f'"{table.__plural__}":')  # type: ignore
                    json.dump(contents, dst, indent=2,
                              sort_keys=True, default=utils.flatten)
                    if table != tables[-1]:
                        dst.write(',')
                    dst.write('\n')
                dst.write('}\n')

    @staticmethod
    def map_primary_keys(pk_maps: Dict[str, Dict[int, int]],
                         tables: List[Type[ModelMixin]], item: ModelMixin,
                         data: JsonObject) -> None:
        """
        map primary keys back to the PKs used in the source file
        """
        # special case, where Directory.parent is not automatically mapped
        if isinstance(item, models.Directory) and item.parent is not None:
            data['parent'] = pk_maps['Directory'][item.parent.pk]
        for tab in tables:
            js_name: str = tab.__tablename__.lower()  # type: ignore
            if isinstance(getattr(item, js_name, None), ModelMixin):
                pk = data[js_name]
                # print(f'{js_name} = "{pk}"')
                if pk is not None:
                    try:
                        data[js_name] = pk_maps[tab.__tablename__][pk]  # type: ignore
                    except KeyError:
                        #print((err, js_name, pk_maps[tab.__tablename__]))
                        continue

    def compare_import_results(self, version: int, imp: Importer,
                               expected: JsonObject,
                               map_pks: bool, empty: bool = True) -> None:
        """
        Check the results of an import
        """
        # self.maxDiff = None
        with models.db.session_scope() as dbs:
            if 'Users' in expected:
                self.compare_imported_users(dbs, expected)
            self.compare_imported_directories(dbs, imp, expected, map_pks)
            album_pks = self.compare_imported_albums(dbs, version, imp, expected, map_pks)
            artist_pks = self.compare_imported_artists(dbs, version, imp, expected, map_pks)
            self.compare_imported_songs(dbs, version, imp, expected, map_pks,
                                        album_pks, artist_pks)
            self.compare_imported_games(dbs, expected)
            self.compare_imported_tracks(dbs, imp, expected, map_pks, empty)
            self.compare_imported_tickets(dbs, imp, expected, map_pks, empty)

    def compare_imported_users(self, dbs: DatabaseSession, expected: JsonObject) -> None:
        """
        Check the results of importing users
        """
        for item in expected["Users"]:
            for field in ['last_login', 'reset_expires']:
                if item[field]:
                    item[field] = utils.make_naive_utc(
                        cast(datetime.datetime, utils.parse_date(item[field])))
            user = models.User.get(dbs, username=item["username"])
            self.assertIsNotNone(user)
            item['pk'] = user.pk  # type: ignore
            self.assertModelEqual(
                user.to_dict(),  # type: ignore
                item, user.username)  # type: ignore

    def compare_imported_games(self, dbs: DatabaseSession, expected: JsonObject) -> None:
        """
        Check the results of importing
        """
        for idx, item in enumerate(expected["Games"]):
            game = models.Game.get(dbs, id=item["id"])
            self.assertIsNotNone(game)
            actual = utils.flatten(game.to_dict())  # type: ignore
            item['pk'] = game.pk  # type: ignore
            gid = item["id"]
            msg = f'Game[{idx}] (id={gid})'
            self.assertModelEqual(actual, item, msg)

    def compare_imported_directories(self, dbs: DatabaseSession, imp: Importer,
                                     expected: JsonObject, map_pks: bool) -> None:
        """
        Check the results of importing directories
        """
        # with models.db.session_scope() as dbs:
        #     models.Directory.show(dbs)
        for idx, item in enumerate(expected["Directories"]):
            direc = models.Directory.get(dbs, name=item['name'])
            if direc is None:
                models.Directory.show(dbs)
            self.assertIsNotNone(direc, f'Failed to find directory {item["name"]}')
            actual = direc.to_dict()  # type: ignore
            if map_pks:
                self.assertEqual(imp["Directory"][item['pk']], direc.pk)  # type: ignore
            item['pk'] = direc.pk  # type: ignore
            if map_pks and 'directory' in item:
                # the parent directory property was renamed from "directory" to "parent"
                item['parent'] = item['directory']
                del item['directory']
            if item['parent'] is not None:
                item['parent'] = imp["Directory"][item['parent']]
            msg = f'Directory[{idx}]'
            self.assertModelEqual(actual, item, msg)

    def compare_imported_albums(self, dbs: DatabaseSession, version: int, imp: Importer,
                                expected: JsonObject, map_pks: bool) -> Dict[int, int]:
        """
        Check the results of importing albums
        """
        album_pks: Dict[int, int] = {}
        for idx, item in enumerate(expected["Albums"]):
            album = models.Album.get(dbs, name=item['name'])
            self.assertIsNotNone(album, f'Failed to find album {item["name"]}')
            actual = album.to_dict()  # type: ignore
            album_pks[item['pk']] = album.pk  # type: ignore
            if version < 6:
                item['pk'] = album.pk  # type: ignore
            elif map_pks:
                item['pk'] = imp["Album"][item['pk']]
            msg = f'Album[{idx}]'
            self.assertModelEqual(actual, item, msg)
        return album_pks

    def compare_imported_artists(self, dbs: DatabaseSession, version: int, imp: Importer,
                                 expected: JsonObject, map_pks: bool) -> Dict[int, int]:
        """
        Check the results of importing artists
        """
        artist_pks: Dict[int, int] = {}
        for idx, item in enumerate(expected["Artists"]):
            art = models.Artist.get(dbs, name=item['name'])
            self.assertIsNotNone(art, f'Failed to find artist {item["name"]}')
            actual = art.to_dict()  # type: ignore
            artist_pks[item['pk']] = art.pk  # type: ignore
            if version < 6:
                item['pk'] = art.pk  # type: ignore
            elif map_pks:
                item['pk'] = imp["Artist"][item['pk']]
            msg = f'Artist[{idx}]'
            self.assertModelEqual(actual, item, msg)
        return artist_pks

    def compare_imported_songs(self, dbs: DatabaseSession, version: int, imp: Importer,
                               expected: JsonObject, map_pks: bool,
                               album_pks: Dict[int, int], artist_pks: Dict[int, int]) -> None:
        """
        Check the results of importing songs
        """
        for idx, item in enumerate(expected["Songs"]):
            msg = f'Song[{idx}]'
            dir_pk = item['directory']
            if map_pks and dir_pk in imp["Directory"]:
                dir_pk = imp["Directory"][dir_pk]
            direc = models.Directory.get(dbs, pk=dir_pk)
            self.assertIsNotNone(direc, msg)
            item['directory'] = direc.pk  # type: ignore
            song = models.Song.get(dbs, directory=direc, filename=item['filename'])
            self.assertIsNotNone(song, f'song[{idx}]')
            if map_pks:
                try:
                    self.assertEqual(song.pk, imp["Song"][item['pk']])  # type: ignore
                except KeyError:
                    pass
                item['pk'] = song.pk  # type: ignore
                if version < 6:
                    item['album'] = album_pks[item['album']]
                    try:
                        item['artist'] = artist_pks[item['artist']]
                    except KeyError:
                        # gameTracks-v2 has a track from Blue Oyster Cult that causes
                        # the test to fail because the group exists in both its
                        # unicode and ascii version in clips-db.sql
                        self.assertEqual(version, 2)
                        self.assertIn(item['artist'], [190, 207])
                        continue
            actual = song.to_dict()  # type: ignore
            self.assertModelEqual(actual, item, msg)

    def compare_imported_tracks(self, dbs: DatabaseSession, imp: Importer,
                                expected: JsonObject, map_pks: bool, empty: bool) -> None:
        """
        Check the results of importing tracks
        """
        for idx, item in enumerate(expected["Tracks"]):
            pk = item['pk']
            if map_pks:
                pk = imp["Track"][pk]
            track = models.Track.get(dbs, pk=pk)
            self.assertIsNotNone(track)
            self.assertEqual(item['number'], track.number)  # type: ignore
            self.assertEqual(item['start_time'], track.start_time)  # type: ignore
            if empty:
                self.assertEqual(imp["Game"][item["game"]], track.game.pk)  # type: ignore
            elif track.game.pk not in imp["Game"].values():  # type: ignore
                continue
            if map_pks:
                item['game'] = imp["Game"][item["game"]]
                item['pk'] = imp["Track"][item['pk']]
                item['song'] = imp["Song"][item['song']]
            actual = track.to_dict()  # type: ignore
            msg: str = f'Track[{idx}]'
            self.assertModelEqual(actual, item, msg)

    def compare_imported_tickets(self, dbs: DatabaseSession, imp: Importer,
                                 expected: JsonObject, map_pks: bool, empty: bool) -> None:
        """
        Check the results of importing Bingo tickets
        """
        for idx, item in enumerate(expected["BingoTickets"]):
            if not empty and item['pk'] not in imp["BingoTicket"]:
                continue
            pk = imp["BingoTicket"][item['pk']]
            ticket = models.BingoTicket.get(dbs, pk=pk)
            self.assertIsNotNone(ticket)
            actual = ticket.to_dict()  # type: ignore
            if map_pks:
                item['game'] = imp["Game"][item['game']]
                #tracks = [imp["Track"][pk] for pk in item['tracks']]
                #item['tracks'] = tracks
                item['pk'] = imp["BingoTicket"][item["pk"]]
            msg: str = f'BingoTicket[{idx}]'
            self.assertModelEqual(actual, item, msg)

    def export_test(self, schema_version: int) -> None:
        """
        Test exporting a database to a JSON file
        """
        connect_str = "sqlite:///:memory:"
        engine: Engine = create_engine(connect_str)  # , echo=True)
        self.load_fixture(engine, f"tv-themes-v{schema_version}.sql")

        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        output = io.StringIO()
        # pylint: disable=no-value-for-parameter
        with models.db.session_scope() as dbs:
            models.export_database_to_file(output, self.options, Progress(), dbs, None)
        output.seek(0)
        actual_json = json.load(output)
        if self.EXPECTED_OUTPUT is not None:
            destination: Path = self.EXPECTED_OUTPUT / f"exported-tv-themes-v{schema_version}.json"
            with open(destination, 'wt', encoding='utf-8') as dbg:
                dbg.write(output.getvalue())
        validate_json(JsonSchema.DATABASE, actual_json)
        json_filename: Path = fixture_filename(f"exported-tv-themes-v{schema_version}.json")
        with json_filename.open('rt', encoding='utf-8') as src:
            expected_json = json.load(src)
        self.assertEqual(expected_json['Users'][0]['username'], 'admin')
        expected_json['Users'][0]['last_login'] = None
        # self.maxDiff = None
        for table in expected_json.keys():
            # print(f'Check {table}')
            if isinstance(actual_json[table], dict):
                self.assertDictEqual(actual_json[table], expected_json[table], table)
            else:
                self.assertModelListEqual(actual_json[table], expected_json[table], table)

    def test_import_v1_gametracks_empty_db(self) -> None:
        """
        Test import of JSON file containing information about a generated game (v1 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        # pylint: disable=no-value-for-parameter
        results = ExpectedImportResult(games=1, songs=43, tracks=43)
        self.gametracks_import_test(1, results)

    def test_import_v1_gametracks_with_clips(self) -> None:
        """
        Test import of JSON file containing information about a generated game (v1 format)
        """
        engine: Engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, songs=0, tracks=43)
        # pylint: disable=no-value-for-parameter
        self.gametracks_import_test(1, results)

    def test_import_v1_bug_gametracks_empty_db(self) -> None:
        """
        Test import a v1 gameTracks that has a bug that puts an array
        in the album field (empty databse)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=12, artists=29,
                                       songs=30, tracks=30)
        self.gametracks_import_test(1, results, 'gameTracks-v1-bug')

    def test_import_v1_bug_gametracks_with_clips(self) -> None:
        """
        Test import a v1 gameTracks that has a bug that puts an array
        in the album field (non-empty database)
        """
        engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=2, albums=12, artists=29,
                                       songs=4, tracks=30)
        self.gametracks_import_test(1, results, 'gameTracks-v1-bug')

    def test_import_v1_gametracks_no_album_with_clips(self) -> None:
        """
        Test import a v1 gameTracks that has a bug that doesn't have an album field
        """
        engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=2, albums=12, artists=29,
                                       songs=30, tracks=30)
        self.gametracks_import_test(1, results, 'gameTracks-v1-no-album')

    def test_import_v2_gametracks_empty_db(self) -> None:
        """
        Test import of JSON file containing information about a generated game (v2 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, songs=50, tracks=50)
        # pylint: disable=no-value-for-parameter
        results = ExpectedImportResult(games=1, directories=2, albums=8, artists=44,
                                       songs=50, tracks=50)
        self.gametracks_import_test(2, results)

    def test_import_v2_gametracks_with_clips(self) -> None:
        """
        Test import of JSON file containing information about a generated game (v2 format)
        """
        engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=1, albums=8, artists=44,
                                       songs=0, tracks=50)
        self.gametracks_import_test(2, results)

    def test_import_v3_gametracks_empty_db(self) -> None:
        """
        Importing v3 gameTracks JSON (empty database)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=1, artists=34,
                                       songs=40, tracks=40, bingo_tickets=24)
        self.gametracks_import_test(3, results)

    def test_import_v3_gametracks_with_clips(self) -> None:
        """
        Importing v3 gameTracks JSON (songs already in database)
        """
        engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=1, albums=1, artists=34,
                                       songs=0, tracks=40, bingo_tickets=24)
        self.gametracks_import_test(3, results)

    def test_import_v3_gametracks_with_missing_song_clips(self) -> None:
        """
        Importing v3 gameTracks JSON that had a bug with missing song ID (songs already in database)
        """
        engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=1, albums=1, artists=34,
                                       songs=45, tracks=45, bingo_tickets=24)
        self.gametracks_import_test(3, results, 'gameTracks-v3-no-song')

    def test_import_v3_gametracks_with_no_song_metadata(self) -> None:
        """
        Importing v3 gameTracks JSON that had a bug with missing all song metadata
        """
        engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=0, albums=0, artists=0,
                                       songs=0, tracks=0, bingo_tickets=0)
        self.gametracks_import_test(3, results, 'gameTracks-v3-no-song-data')

    def test_import_v4_gametracks_empty_db(self) -> None:
        """
        Importing v4 gameTracks JSON (empty database)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=1, artists=34,
                                       songs=40, tracks=40, bingo_tickets=24)
        self.gametracks_import_test(4, results)

    def test_import_v4_gametracks_with_clips(self) -> None:
        """
        Importing v4 gameTracks JSON (songs already in database)
        """
        engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=1, albums=1, artists=34,
                                       songs=0, tracks=40, bingo_tickets=24)
        self.gametracks_import_test(4, results)

    def test_import_v4_exported_gametracks_empty_db(self) -> None:
        """
        Importing v4 gameTracks JSON created by export-game (empty database)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=16,
                                       artists=29, songs=30, tracks=30)
        self.gametracks_import_test(4, results, "game-18-04-25-1")

    def test_import_v4_exported_gametracks_with_clips(self) -> None:
        """
        Importing v4 gameTracks JSON created by export-game (songs in database)
        """
        engine: Engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=2, albums=16,
                                       artists=29, songs=23, tracks=30)
        self.gametracks_import_test(4, results, "game-18-04-25-1")

    def gametracks_import_test(self, version: int, results: ExpectedImportResult,
                               src_filename: Optional[str] = None) -> None:
        """
        Check that import_game_tracks() imports the gameTracks file into the
        database
        """
        with models.db.session_scope() as session:
            has_clips: bool = models.Song.total_items(session) > 0
            empty: str = '' if has_clips else '-empty'
            if src_filename is None:
                src_filename = f"gameTracks-v{version}"
            fix_filename = fixture_filename(f"{src_filename}.json")
            imp = Importer(self.options, session, Progress())
            imp.import_game_tracks(fix_filename, f'01-02-03-{version}')
            if self.EXPECTED_OUTPUT is not None:
                filename: Path = self.EXPECTED_OUTPUT / f"db-imported-{src_filename}{empty}.json"
                # logging.getLogger('musicbingo.models').setLevel(logging.DEBUG)
                models.export_database(filename, self.options, Progress(), session)
                self.create_expected_json(f"imported-{src_filename}{empty}.json", imp)
            self.assertEqual(imp.added["User"], results.users)
            self.assertEqual(imp.added["Game"], results.games)
            self.assertEqual(imp.added["Song"], results.songs)
            self.assertEqual(imp.added["Track"], results.tracks)
            self.assertEqual(imp.added["BingoTicket"], results.bingo_tickets)
            exp_filename = fixture_filename(f"imported-{src_filename}{empty}.json")
        # print(exp_filename)
        with exp_filename.open('rt', encoding='utf-8') as inp:
            expected = json.load(inp)
        if version < 3:
            stats: stat_result = fix_filename.stat()
            start = datetime.datetime(*(time.gmtime(stats.st_mtime)[0:6]))
            end: datetime.datetime = start + datetime.timedelta(days=1)
            expected["Games"][0]["start"] = utils.to_iso_datetime(start)
            expected["Games"][0]["end"] = utils.to_iso_datetime(end)
        self.compare_import_results(version, imp, expected, True)

    def test_translate_v1_gametracks_empty_db(self) -> None:
        """
        Converting gameTracks v1 JSON file, no clips in database
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=5,
                                       artists=42, songs=43, tracks=43)
        with session_scope() as session:
            self.gametracks_translate_test(1, False, results, session)

    def test_translate_v1_gametracks_with_clips(self) -> None:
        """
        Converting gameTracks v1 JSON file, with clips already in database
        """
        engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        # pylint: disable=no-value-for-parameter
        results = ExpectedImportResult(games=1, directories=3, albums=5,
                                       artists=42, songs=43, tracks=43)
        with session_scope() as session:
            self.gametracks_translate_test(1, False, results, session)

    def test_translate_v1_bug_gametracks_empty_db(self) -> None:
        """
        Test convert a v1 gameTracks that has a bug that puts an array
        in the album field (empty databse)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=12,
                                       artists=29, songs=30, tracks=30)
        with session_scope() as session:
            self.gametracks_translate_test(1, True, results, session)

    def test_translate_v1_bug_gametracks_with_clips(self) -> None:
        """
        Test convert a v1 gameTracks that has a bug that puts an array
        in the album field (non-empty database)
        """
        engine: Engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=11, albums=12,
                                       artists=29, songs=30, tracks=30)
        with session_scope() as session:
            self.gametracks_translate_test(1, True, results, session)

    def test_translate_v2_gametracks_empty_db(self) -> None:
        """
        Test conversion of JSON file containing information about a generated game (v2 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=8,
                                       artists=44, songs=50, tracks=50)
        with session_scope() as session:
            self.gametracks_translate_test(2, False, results, session)

    def test_translate_v2_gametracks_with_clips(self) -> None:
        """
        Converting gameTracks v2 JSON file, with clips already in database
        """
        engine: Engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=2, albums=8,
                                       artists=44, songs=50, tracks=50)
        with session_scope() as session:
            self.gametracks_translate_test(2, False, results, session)

    def test_translate_v3_gametracks_empty_db(self) -> None:
        """
        Test conversion of JSON file containing information about a generated game (v3 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=1,
                                       artists=34, songs=40, tracks=40,
                                       bingo_tickets=24)
        with session_scope() as session:
            self.gametracks_translate_test(3, False, results, session)

    def test_translate_v3_gametracks_with_clips(self) -> None:
        """
        Converting gameTracks v3 JSON file, with clips already in database
        """
        engine: Engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        results = ExpectedImportResult(games=1, directories=1, albums=1,
                                       artists=34, songs=40, tracks=40,
                                       bingo_tickets=24)
        with session_scope() as session:
            self.gametracks_translate_test(3, False, results, session)

    def test_translate_v4_gametracks_empty_db(self) -> None:
        """
        Converting gameTracks v4 JSON file, from empty database
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=1,
                                       artists=34, songs=40, tracks=40,
                                       bingo_tickets=24)
        with session_scope() as session:
            self.gametracks_translate_test(4, False, results, session)

    def test_translate_v4_gametracks_with_clips(self) -> None:
        """
        Converting gameTracks v4 JSON file, with clips already in database
        """
        engine: Engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine)
        results = ExpectedImportResult(games=1, directories=2, albums=1,
                                       artists=34, songs=40, tracks=40,
                                       bingo_tickets=24)
        with session_scope() as session:
            self.gametracks_translate_test(4, False, results, session)

    def test_translate_v4_exported_gametracks_empty_db(self) -> None:
        """
        Converting exported gameTracks v4 JSON file, clips not in database
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        results = ExpectedImportResult(games=1, directories=2, albums=16,
                                       artists=29, songs=30, tracks=30)
        with session_scope() as session:
            self.gametracks_translate_test(
                4, False, results, session, "game-18-04-25-1")

    def test_translate_v4_exported_gametracks_with_clips(self) -> None:
        """
        Converting exported gameTracks v4 JSON file, clips in database
        """
        engine: Engine = self.load_clips_fixture()
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine)
        results = ExpectedImportResult(games=1, directories=7, albums=16,
                                       artists=29, songs=30, tracks=30)
        with session_scope() as session:
            self.gametracks_translate_test(4, False, results, session,
                                           "game-18-04-25-1")

    def test_create_superuser_blank_database(self) -> None:
        """
        Check that an admin account is created if the database is empty
        """
        DatabaseConnection.bind(self.options.database, create_tables=True, create_superuser=True)
        with models.db.session_scope() as dbs:
            self.assertEqual(models.User.total_items(dbs), 1)
            admin: models.User | None = cast(
                models.User | None, models.User.get(
                    dbs, username=models.User.__DEFAULT_ADMIN_USERNAME__))
            assert admin is not None
            self.assertTrue(admin.check_password(models.User.__DEFAULT_ADMIN_PASSWORD__))
            self.assertTrue(admin.is_admin)

    def test_create_superuser_non_empty_database(self) -> None:
        """
        Check that an admin account is not created if the database not empty
        """
        connect_str = "sqlite:///:memory:"
        engine: Engine = create_engine(connect_str)
        self.load_fixture(engine, "tv-themes-v4.sql")
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        with models.db.session_scope() as dbs:
            self.assertEqual(models.User.total_items(dbs), 2)
            admin: models.User | None = cast(
                models.User | None, models.User.get(
                    dbs, username=models.User.__DEFAULT_ADMIN_USERNAME__))
            assert admin is not None
            self.assertTrue(admin.is_admin)
            self.assertFalse(admin.check_password(models.User.__DEFAULT_ADMIN_PASSWORD__))
            self.assertTrue(admin.check_password('adm!n'))

    def test_export_game(self) -> None:
        """
        Test exporting a game to a gameTracks JSON file
        """
        connect_str = "sqlite:///:memory:"
        engine: Engine = create_engine(connect_str)
        self.load_fixture(engine, "tv-themes-v4.sql")
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=False)
        with models.db.session_scope() as dbs:
            for song in cast(Iterable[models.Song], models.Song.all(dbs)):
                song.check_for_uuid()
            result: JsonObject | None = models.export_game_to_object("20-04-24-2", dbs)
            assert result is not None
        result = utils.flatten(result)
        assert result is not None
        validate_json(JsonSchema.GAME_TRACKS_V4, result)
        if self.EXPECTED_OUTPUT is not None:
            destination = self.EXPECTED_OUTPUT / 'exported-game-v4.json'
            with open(destination, 'wt', encoding='utf-8') as dst:
                json.dump(result, dst, indent=2, sort_keys=True)
        json_filename: Path = fixture_filename("exported-game-v4.json")
        with json_filename.open('rt', encoding='utf-8') as src:
            expected = json.load(src)
        for table in expected.keys():
            # print(f'Check {table}')
            self.assertModelListEqual(result[table], expected[table], table)

    def gametracks_translate_test(self,
                                  version: int,
                                  has_bug: bool,
                                  results: ExpectedImportResult,
                                  session: models.DatabaseSession,
                                  src_filename: Optional[str] = None) -> None:
        """
        Check that translate_game_tracks() produces the correct output
        """
        is_empty: bool = models.Song.total_items(session) == 0
        bug: str = '-bug' if has_bug else ''
        empty = '-empty' if is_empty else ''
        if src_filename is None:
            src_filename = f"gameTracks-v{version}{bug}"
        fix_filename = fixture_filename(f"{src_filename}.json")
        imp = Importer(self.options, session, Progress())
        data = imp.translate_game_tracks(fix_filename, f'01-02-03-{version}{bug}')
        if self.EXPECTED_OUTPUT is not None:
            destination = self.EXPECTED_OUTPUT / f'translated-{src_filename}{empty}.json'
            with open(destination, 'wt', encoding='utf-8') as dst:
                json.dump(data, dst, indent=2)
        self.assertEqual(len(data.get("Users",[])), results.users)
        self.assertEqual(len(data["Directories"]), results.directories)
        self.assertEqual(len(data["Albums"]), results.albums)
        self.assertEqual(len(data["Artists"]), results.artists)
        self.assertEqual(len(data["Songs"]), results.songs)
        self.assertEqual(len(data["Games"]), results.games)
        self.assertEqual(len(data["Tracks"]), results.tracks)
        self.assertEqual(len(data.get("BingoTickets",[])), results.bingo_tickets)
        stats = fix_filename.stat()
        if version < 3:
            start = datetime.datetime(*(time.gmtime(stats.st_mtime)[0:6]))
            self.assertEqual(data['Games'][0]['start'], utils.to_iso_datetime(start))
        exp_filename = fixture_filename(f"translated-{src_filename}{empty}.json")
        # print(exp_filename)
        with exp_filename.open('rt', encoding='utf-8') as inp:
            expected = json.load(inp)
        expected['Games'][0]['start'] = data['Games'][0]['start']
        expected['Games'][0]['end'] = data['Games'][0]['end']
        # self.maxDiff = None
        for name in ['Directories', 'Albums', 'Artists', 'Songs', 'Games',
                     'Tracks', 'BingoTickets']:
            if name == 'BingoTickets' and version < 3:
                continue
            self.assertModelListEqual(data[name], expected[name], name)


if __name__ == "__main__":
    unittest.main()
