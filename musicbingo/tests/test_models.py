"""
Unit tests for database models using the version 1 Schema.
"""

import copy
import datetime
import io
import json
import logging
import os
from pathlib import Path
import subprocess
import time
import sys
from typing import Dict
import unittest

from sqlalchemy import create_engine, MetaData  # type: ignore

from musicbingo import models, utils
from musicbingo.models.db import DatabaseConnection, db_session
from musicbingo.models.importsession import ImportSession
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
        logging.getLogger().setLevel(logging.ERROR)
        format = r"%(relativeCreated)06d:%(levelname)s:%(filename)s@%(lineno)d:%(funcName)s  %(message)s"
        logging.basicConfig(format=format)

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

    def import_test(self, schema_version):
        DatabaseConnection.bind(self.options.database)
        json_filename = fixture_filename(f"tv-themes-v{schema_version}.json")
        with json_filename.open('r') as src:
            expected = json.load(src)
        with models.db.session_scope() as dbs:
            imp_sess = models.import_database(self.options, json_filename, dbs)
        self.compare_import_results(imp_sess, expected, True)

    def compare_import_results(self, imp_sess : ImportSession, expected: JsonObject, map_pks: bool):
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
                    bingo_tickets = [imp_sess["BingoTicket"][pk] for pk in item['bingo_tickets']]
                    item['bingo_tickets'] = bingo_tickets
                if map_pks and 'tracks' in item:
                    tracks = [imp_sess["Track"][pk] for pk in item['tracks']]
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
                    dir_pk = imp_sess["Directory"][dir_pk]
                direc = models.Directory.get(dbs, pk=dir_pk)
                self.assertIsNotNone(direc)
                song = models.Song.get(dbs, directory=direc, filename=item['filename'])
                self.assertIsNotNone(song)
                # if schema_version == 1:
                #    actual = song.to_dict(with_collections=False, exclude=["tracks"])
                #    del item['classtype']
                #    actual['directory'] = actual['directory_pk']
                #    del actual['directory_pk']
                # else:
                if map_pks:
                    tracks = [imp_sess["Track"][pk] for pk in item['tracks']]
                    item['tracks'] = tracks
                actual = song.to_dict(with_collections=True)  # type: ignore
                msg = f'Song[{idx}]'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["Tracks"]):
                pk = item['pk']
                if map_pks:
                    pk = imp_sess["Track"][pk]
                track = models.Track.get(dbs, pk=pk)
                self.assertIsNotNone(track)
                # if schema_version == 1:
                #    for field in ["filename", "title", "artist", "duration",
                #                  "album"]:
                #        self.assertEqual(getattr(track.song, field), item[field], field)
                self.assertEqual(item['number'], track.number)  # type: ignore
                self.assertEqual(item['start_time'], track.start_time)  # type: ignore
                self.assertEqual(imp_sess["Game"][item["game"]], track.game.pk)  # type: ignore
                if map_pks:
                    item['game'] = imp_sess["Game"][item["game"]]
                    bingo_tickets = [imp_sess["BingoTicket"][pk] for pk in item['bingo_tickets']]
                    item['bingo_tickets'] = bingo_tickets
                    item['pk'] = imp_sess["Track"][item['pk']]
                actual = track.to_dict(with_collections=True)  # type: ignore
                msg = f'Track[{idx}]'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["BingoTickets"]):
                pk = imp_sess["BingoTicket"][item['pk']]
                ticket = models.BingoTicket.get(dbs, pk=pk)
                self.assertIsNotNone(ticket)
                actual = ticket.to_dict(with_collections=True)  # type: ignore
                if map_pks:
                    item['game'] = imp_sess["Game"][item['game']]
                    tracks = [imp_sess["Track"][pk] for pk in item['tracks']]
                    item['tracks'] = tracks
                    item['pk'] = imp_sess["BingoTicket"][item["pk"]]
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
        DatabaseConnection.bind(self.options.database, create_tables=False, engine=engine)
        output = io.StringIO()
        models.export_database_to_file(output)
        output.seek(0)
        actual_json = json.load(output)
        # Song.show(session)
        # Track.show(session)
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
        self.gametracks_import_test(1)

    def test_import_v2_gametracks(self):
        """
        Test import of JSON file containing information about a generated game (v2 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        self.gametracks_import_test(2)

    def test_import_v3_gametracks(self):
        """
        Test import of JSON file containing information about a generated game (v3 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        self.gametracks_import_test(3)

    @db_session
    def gametracks_import_test(self, version: int, session):
        """
        Check that import_game_tracks() imports the gameTracks file into the
        database
        """
        src_filename = fixture_filename(f"gameTracks-v{version}.json")
        helper = models.import_game_tracks(self.options, src_filename, f'01-02-03-{version}', session)
        self.assertEqual(helper.added["User"], 0)
        self.assertEqual(helper.added["Game"], 1)
        if version == 1:
            num_tracks = 43
        elif version == 2:
            num_tracks = 50
        else:
            num_tracks = 40
        self.assertEqual(helper.added["Song"], num_tracks)
        self.assertEqual(helper.added["Track"], num_tracks)
        if version < 3:
            self.assertEqual(helper.added["BingoTicket"], 0)
        else:
            self.assertEqual(helper.added["BingoTicket"], 24)
        exp_filename = fixture_filename(f"imported-game-v{version}.json")
        with exp_filename.open('rt') as inp:
            expected = json.load(inp)
        self.compare_import_results(helper, expected, False)

    def test_translate_v1_gametracks(self):
        """
        Test conversion of JSON file containing information about a generated game (v1 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        self.gametracks_translate_test(1)

    def test_translate_v2_gametracks(self):
        """
        Test conversion of JSON file containing information about a generated game (v2 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        self.gametracks_translate_test(2)

    def test_translate_v3_gametracks(self):
        """
        Test conversion of JSON file containing information about a generated game (v3 format)
        """
        DatabaseConnection.bind(self.options.database, create_tables=True)
        self.gametracks_translate_test(3)

    @db_session
    def gametracks_translate_test(self, version: int, session):
        """
        Check that translate_game_tracks() produces the correct output
        """
        src_filename = fixture_filename(f"gameTracks-v{version}.json")
        helper = ImportSession(self.options, session)
        data = models.translate_game_tracks(helper, src_filename, f'01-02-03-{version}')
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
        self.assertEqual(len(actual), len(expected), msg)
        pk_map = {}
        for item in expected:
            pk_map[item['pk']] = item
        for idx, item in enumerate(actual):
            pk = item['pk']
            expect = pk_map[pk]
            self.assertModelEqual(item, expect, f'{msg}[{idx}] (pk={pk})')

    def assertModelEqual(self, actual, expected, msg) -> None:
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
