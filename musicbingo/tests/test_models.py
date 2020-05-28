"""
Unit tests for database models using the version 1 Schema.
"""

import datetime
import io
import json
import logging
import time
import unittest

from sqlalchemy import create_engine  # type: ignore

from musicbingo import models, utils
from musicbingo.models.db import (
    DatabaseConnection, db_session, session_scope
)
from musicbingo.models.importer import Importer
from musicbingo.models.modelmixin import JsonObject
from musicbingo.options import DatabaseOptions, Options
from .fixture import fixture_filename

DatabaseOptions.DEFAULT_FILENAME = None
Options.INI_FILENAME = None

class TestDatabaseModels(unittest.TestCase):
    def setUp(self):
        """called before each test"""
        db_opts = DatabaseOptions(database_provider='sqlite', database_name=':memory:')
        self.options = Options(database=db_opts)
        self.options.exists = False
        logging.getLogger().setLevel(logging.INFO)
        log_format = (r"%(relativeCreated)06d:%(levelname)s:" +
                      r"%(filename)s@%(lineno)d:%(funcName)s  %(message)s")
        logging.basicConfig(format=log_format)

    def tearDown(self):
        """called after each test"""
        DatabaseConnection.close()

    def test_v1_export(self):
        """
        Test exporting a database to a JSON file from the version 1 Schema
        """
        self.export_test(1)

    def test_v2_export(self):
        """
        Test exporting a database to a JSON file from the version 2 Schema
        """
        self.export_test(2)

    def test_v1_import(self):
        """
        Test importing a v1 file into the current database Schema
        """
        self.import_test(1)

    def test_v2_import(self):
        """
        Test importing a v2 file into the current database Schema
        """
        self.import_test(2)

    def test_v3_import(self):
        """
        Test importing a v3 file into the current database Schema
        """
        self.import_test(3)

    def test_v4_import(self):
        """
        Test importing a v4 file into the current database Schema
        """
        self.import_test(4)

    def import_test(self, schema_version):
        DatabaseConnection.bind(self.options.database)
        json_filename = fixture_filename(f"tv-themes-v{schema_version}.json")
        with json_filename.open('r') as src:
            expected = json.load(src)
        with models.db.session_scope() as dbs:
            imp = Importer(self.options, dbs)
            imp.import_database(json_filename)
        self.compare_import_results(imp, expected, True)

    def compare_import_results(self, imp : Importer, expected: JsonObject,
                               map_pks: bool, empty: bool = True):
        # self.maxDiff = None
        if 'Users' in expected:
            for item in expected["Users"]:
                with models.db.session_scope() as dbs:
                    user = models.User.get(dbs, username=item["username"])
                    self.assertIsNotNone(user)
                    item['pk'] = user.pk  # type: ignore
                    # if 'bingo_tickets' in item:
                    #    del item['bingo_tickets']
                    self.assertModelEqual(item, user.to_dict(with_collections=True),  # type: ignore
                                          user.username)  # type: ignore
        with models.db.session_scope() as dbs:
            for idx, item in enumerate(expected["Games"]):
                game = models.Game.get(dbs, id=item["id"])
                self.assertIsNotNone(game)
                actual = utils.flatten(game.to_dict(with_collections=True))  # type: ignore
                item['pk'] = game.pk  # type: ignore
                if map_pks and 'bingo_tickets' in item:
                    bingo_tickets = [imp["BingoTicket"][pk] for pk in item['bingo_tickets']]
                    item['bingo_tickets'] = bingo_tickets
                if map_pks and 'tracks' in item:
                    tracks = [imp["Track"][pk] for pk in item['tracks']]
                    item['tracks'] = tracks
                gid = item["id"]
                msg = f'Game[{idx}] (id={gid})'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["Directories"]):
                direc = models.Directory.get(dbs, name=item['name'])
                self.assertIsNotNone(direc)
                actual = direc.to_dict(with_collections=True)  # type: ignore
                if map_pks and 'directory' in item:
                    # the parent directory property was renamed from "directory" to "parent"
                    item['parent'] = item['directory']
                    del item['directory']
                msg = f'Directory[{idx}]'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["Songs"]):
                dir_pk = item['directory']
                if map_pks:
                    dir_pk = imp["Directory"][dir_pk]
                direc = models.Directory.get(dbs, pk=dir_pk)
                self.assertIsNotNone(direc)
                song = models.Song.get(dbs, directory=direc, filename=item['filename'])
                self.assertIsNotNone(song)
                if map_pks:
                    tracks = [imp["Track"][pk] for pk in item['tracks']]
                    item['tracks'] = tracks
                actual = song.to_dict(with_collections=True)  # type: ignore
                msg = f'Song[{idx}]'
                self.assertModelEqual(actual, item, msg)
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
                    bingo_tickets = [imp["BingoTicket"][pk] for pk in item['bingo_tickets']]
                    item['bingo_tickets'] = bingo_tickets
                    item['pk'] = imp["Track"][item['pk']]
                actual = track.to_dict(with_collections=True)  # type: ignore
                msg = f'Track[{idx}]'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["BingoTickets"]):
                if not empty and item['pk'] not in imp["BingoTicket"]:
                    continue
                pk = imp["BingoTicket"][item['pk']]
                ticket = models.BingoTicket.get(dbs, pk=pk)
                self.assertIsNotNone(ticket)
                actual = ticket.to_dict(with_collections=True)  # type: ignore
                if map_pks:
                    item['game'] = imp["Game"][item['game']]
                    tracks = [imp["Track"][pk] for pk in item['tracks']]
                    item['tracks'] = tracks
                    item['pk'] = imp["BingoTicket"][item["pk"]]
                msg = f'BingoTicket[{idx}]'
                self.assertModelEqual(actual, item, msg)

    def export_test(self, schema_version):
        """
        Test exporting a database to a JSON file
        """
        # print(f"test_export {schema_version}")
        json_filename = fixture_filename(f"tv-themes-v{schema_version}.json")
        # print(json_filename)
        with json_filename.open('r') as src:
            expected_json = json.load(src)
        #models.__setup = True
        #models.bind(provider='sqlite', filename=':memory:')
        connect_str = "sqlite:///:memory:"
        engine = create_engine(connect_str)  # , echo=True)

        sql_filename = fixture_filename(f"tv-themes-v{schema_version}.sql")
        # print(sql_filename)
        with sql_filename.open('rt') as src:
            sql = src.read()
        with engine.connect() as conn:
            for line in sql.split(';'):
                while line and line[0] in [' ', '\r', '\n']:
                    line = line[1:]
                if not line:
                    continue
                # print(f'"{line}"')
                if line in ['BEGIN TRANSACTION', 'COMMIT']:
                    continue
                conn.execute(line)
        DatabaseConnection.bind(self.options.database, create_tables=False,
                                engine=engine, debug=True)
        output = io.StringIO()
        models.export_database_to_file(output)
        output.seek(0)
        actual_json = json.load(output)
        # with session_scope() as session:
        #     models.Game.show(session)
        #     models.Track.show(session)
        # with open(f'tmp-{schema_version}.json', 'wt') as dbg:
        #    dbg.write(output.getvalue())
        # self.maxDiff = None
        for table in expected_json.keys():
            # print(f'Check {table}')
            self.assertModelListEqual(actual_json[table], expected_json[table], table)

    def test_import_v1_gametracks(self):
        """
        Test import of JSON file containing information about a generated game (v1 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        # pylint: disable=no-value-for-parameter
        self.gametracks_import_test(1)

    def test_import_v2_gametracks(self):
        """
        Test import of JSON file containing information about a generated game (v2 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        # pylint: disable=no-value-for-parameter
        self.gametracks_import_test(2)

    def test_import_v3_gametracks(self):
        """
        Test import of JSON file containing information about a generated game (v3 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        # pylint: disable=no-value-for-parameter
        self.gametracks_import_test(3)

    def test_import_v1_bug_gametracks_empty_database(self):
        """
        Test import a v1 gameTracks that has a bug that puts an array
        in the album field (empty databse)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        with session_scope() as session:
            self.check__import_v1_bug_gametracks(session, True)

    def test_import_v1_bug_gametracks(self):
        """
        Test import a v1 gameTracks that has a bug that puts an array
        in the album field (non-empty database)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        with session_scope() as session:
            json_filename = fixture_filename("tv-themes-v4.json")
            imp = Importer(self.options, session)
            imp.import_database(json_filename)
        with session_scope() as session:
            self.check__import_v1_bug_gametracks(session, False)

    def check__import_v1_bug_gametracks(self, session: models.DatabaseSession,
                                        empty: bool):
        """
        Test import a v1 gameTracks that has a bug that puts an array
        in the album field
        """
        src_filename = fixture_filename("gameTracks-v1-bug.json")
        imp = Importer(self.options, session)
        imp.import_game_tracks(src_filename, '01-02-03-bug')
        self.assertEqual(imp.added["User"], 0)
        self.assertEqual(imp.added["Game"], 1)
        self.assertEqual(imp.added["Song"], 30)
        self.assertEqual(imp.added["Track"], 30)
        self.assertEqual(imp.added["BingoTicket"], 0)
        # models.export_database(Path('imported-game-v1-bad.json'))
        if empty:
            exp_filename = fixture_filename("imported-game-v1-bad-empty.json")
        else:
            exp_filename = fixture_filename("imported-game-v1-bad.json")
        with exp_filename.open('rt') as inp:
            expected = json.load(inp)
        game = models.Game.get(session, id='01-02-03-bug')
        self.assertIsNotNone(game)
        if empty:
            expected["Games"][0]["start"] = utils.to_iso_datetime(game.start)  # type: ignore
            expected["Games"][0]["end"] = utils.to_iso_datetime(game.end)  # type: ignore
        else:
            expected["Games"][1]["start"] = utils.to_iso_datetime(game.start)  # type: ignore
            expected["Games"][1]["end"] = utils.to_iso_datetime(game.end)  # type: ignore
        if not empty and False:
            for track in expected["Tracks"]:
                track['pk'] += 50
            expected["Games"][0]["tracks"] = [
                pk+50 for pk in expected["Games"][0]["tracks"]]
            expected["Directories"][0]["pk"] += 1
        self.compare_import_results(imp, expected, False, empty=False)

    @db_session
    def gametracks_import_test(self, version: int, session):
        """
        Check that import_game_tracks() imports the gameTracks file into the
        database
        """
        src_filename = fixture_filename(f"gameTracks-v{version}.json")
        imp = Importer(self.options, session)
        imp.import_game_tracks(src_filename, f'01-02-03-{version}')
        self.assertEqual(imp.added["User"], 0)
        self.assertEqual(imp.added["Game"], 1)
        if version == 1:
            num_tracks = 43
        elif version == 2:
            num_tracks = 50
        else:
            num_tracks = 40
        self.assertEqual(imp.added["Song"], num_tracks)
        self.assertEqual(imp.added["Track"], num_tracks)
        if version < 3:
            self.assertEqual(imp.added["BingoTicket"], 0)
        else:
            self.assertEqual(imp.added["BingoTicket"], 24)
        exp_filename = fixture_filename(f"imported-game-v{version}.json")
        with exp_filename.open('rt') as inp:
            expected = json.load(inp)
        if version < 3:
            stats = src_filename.stat()
            start = datetime.datetime(*(time.gmtime(stats.st_mtime)[0:6]))
            end = start + datetime.timedelta(days=1)
            expected["Games"][0]["start"] = utils.to_iso_datetime(start)
            expected["Games"][0]["end"] = utils.to_iso_datetime(end)
        self.compare_import_results(imp, expected, False)

    def test_translate_v1_gametracks(self):
        """
        Test conversion of JSON file containing information about a generated game (v1 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        # pylint: disable=no-value-for-parameter
        self.gametracks_translate_test(1)

    def test_translate_v2_gametracks(self):
        """
        Test conversion of JSON file containing information about a generated game (v2 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        # pylint: disable=no-value-for-parameter
        self.gametracks_translate_test(2)

    def test_translate_v3_gametracks(self):
        """
        Test conversion of JSON file containing information about a generated game (v3 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        # pylint: disable=no-value-for-parameter
        self.gametracks_translate_test(3)

    @db_session
    def gametracks_translate_test(self, version: int, session):
        """
        Check that translate_game_tracks() produces the correct output
        """
        src_filename = fixture_filename(f"gameTracks-v{version}.json")
        imp = Importer(self.options, session)
        data = imp.translate_game_tracks(src_filename, f'01-02-03-{version}')
        # with open(f'translated-game-v{version}.json', 'wt') as dst:
        #           json.dump(data, dst, indent=2, sort_keys=True)
        self.assertTrue('Games' in data)
        self.assertEqual(len(data['Games']), 1)
        stats = src_filename.stat()
        if version < 3:
            start = datetime.datetime(*(time.gmtime(stats.st_mtime)[0:6]))
            self.assertEqual(data['Games'][0]['start'], utils.to_iso_datetime(start))
        exp_filename = fixture_filename(f"translated-game-v{version}.json")
        with exp_filename.open('rt') as inp:
            expected = json.load(inp)
        expected['Games'][0]['start'] = data['Games'][0]['start']
        expected['Games'][0]['end'] = data['Games'][0]['end']
        # self.maxDiff = None
        self.assertDictEqual(data, expected)

    def assertModelListEqual(self, actual, expected, msg) -> None:
        """
        assert that two lists of database models are identical
        """
        self.assertEqual(len(actual), len(expected), msg)
        pk_map = {}
        for item in expected:
            pk_map[item['pk']] = item
        for idx, item in enumerate(actual):
            pk = item['pk']
            expect = pk_map[pk]
            self.assertModelEqual(item, expect, f'{msg}[{idx}] (pk={pk})')

    def assertModelEqual(self, actual, expected, msg) -> None:
        """
        assert that two database models are identical
        """
        for key in actual.keys():
            if isinstance(actual[key], list):
                actual[key].sort()
                self.assertIn(key, expected, f'{msg} Expected data missing field {key}')
                expected[key].sort()
            kmsg = f'{msg}: {key}'
            self.assertIn(key, expected)
            if isinstance(actual[key], dict):
                self.assertDictEqual(actual[key], expected[key], kmsg)
            elif isinstance(actual[key], list):
                self.assertListEqual(actual[key], expected[key], kmsg)
            else:
                self.assertEqual(actual[key], expected[key], kmsg)


if __name__ == "__main__":
    unittest.main()
