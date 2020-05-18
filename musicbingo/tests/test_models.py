"""
Unit tests for database models using the version 1 Schema.
"""

import copy
import datetime
import io
import json
import os
import subprocess
import time
import sys
from typing import Dict
import unittest

from sqlalchemy import create_engine, MetaData  # type: ignore

from musicbingo import models, utils
from musicbingo.models.db import DatabaseConnection, db_session
from musicbingo.models.importsession import ImportSession
from musicbingo.options import DatabaseOptions, Options
from .fixture import fixture_filename


class TestDatabaseModels(unittest.TestCase):
    def setUp(self):
        """called before each test"""
        db_opts = DatabaseOptions(database_provider='sqlite', database_name=':memory:')
        self.options = Options(database=db_opts)
        self.options.exists = False

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
        imp_sess = models.import_database(self.options, json_filename)
        self.maxDiff = None
        for item in expected["Users"]:
            with models.db.session_scope() as dbs:
                user = models.User.get(dbs, username=item["username"])
                self.assertIsNotNone(user)
                item['pk'] = user.pk
                # if 'bingo_tickets' in item:
                #    del item['bingo_tickets']
                self.assertModelEqual(item, user.to_dict(with_collections=True),
                                      user.username)
        with models.db.session_scope() as dbs:
            for idx, item in enumerate(expected["Games"]):
                game = models.Game.get(dbs, id=item["id"])
                self.assertIsNotNone(game)
                actual = utils.flatten(game.to_dict(with_collections=True))
                item['pk'] = game.pk
                bingo_tickets = [imp_sess["BingoTicket"][pk] for pk in item['bingo_tickets']]
                item['bingo_tickets'] = bingo_tickets
                tracks = [imp_sess["Track"][pk] for pk in item['tracks']]
                item['tracks'] = tracks
                gid = item["id"]
                msg = f'Game[{idx}] (id={gid})'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["Directories"]):
                direc = models.Directory.get(dbs, name=item['name'])
                self.assertIsNotNone(direc)
                actual = direc.to_dict(with_collections=True)
                if 'directory' in item:
                    # the parent directory property was renamed from "directory" to "parent"
                    item['parent'] = item['directory']
                    del item['directory']
                msg = f'Directory[{idx}]'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["Songs"]):
                dir_pk = imp_sess["Directory"][item['directory']]
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
                tracks = [imp_sess["Track"][pk] for pk in item['tracks']]
                item['tracks'] = tracks
                actual = song.to_dict(with_collections=True)
                msg = f'Song[{idx}]'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["Tracks"]):
                pk = imp_sess["Track"][item['pk']]
                track = models.Track.get(dbs, pk=pk)
                self.assertIsNotNone(track)
                # if schema_version == 1:
                #    for field in ["filename", "title", "artist", "duration",
                #                  "album"]:
                #        self.assertEqual(getattr(track.song, field), item[field], field)
                self.assertEqual(item['number'], track.number)
                self.assertEqual(item['start_time'], track.start_time)
                self.assertEqual(imp_sess["Game"][item["game"]], track.game.pk)
                item['game'] = imp_sess["Game"][item["game"]]
                # if schema_version > 1:
                bingo_tickets = [imp_sess["BingoTicket"][pk] for pk in item['bingo_tickets']]
                item['bingo_tickets'] = bingo_tickets
                item['pk'] = imp_sess["Track"][item['pk']]
                actual = track.to_dict(with_collections=True)
                msg = f'Track[{idx}]'
                self.assertModelEqual(actual, item, msg)
            for idx, item in enumerate(expected["BingoTickets"]):
                pk = imp_sess["BingoTicket"][item['pk']]
                ticket = models.BingoTicket.get(dbs, pk=pk)
                self.assertIsNotNone(ticket)
                actual = ticket.to_dict(with_collections=True)
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
        self.maxDiff = None
        for table in expected_json.keys():
            # print(f'Check {table}')
            self.assertModelListEqual(actual_json[table], expected_json[table], table)

    def test_import_v1_gametracks(self):
        DatabaseConnection.bind(self.options.database, create_tables=True)
        self.gametracks_import_test(1)

    def test_import_v2_gametracks(self):
        DatabaseConnection.bind(self.options.database, create_tables=True)
        self.gametracks_import_test(2)

    @db_session
    def gametracks_import_test(self, version: int, session):
        src_filename = fixture_filename(f"gameTracks-v{version}.json")
        helper = ImportSession(self.options, session)
        data = models.translate_game_tracks(helper, src_filename, '01-02-03')
        self.assertTrue('Games' in data)
        self.assertEqual(len(data['Games']), 1)
        stats = src_filename.stat()
        start = datetime.datetime(*(time.gmtime(stats.st_mtime)[0:6]))
        self.assertEqual(data['Games'][0]['start'], utils.to_iso_datetime(start))
        exp_filename = fixture_filename(f"translated-game-v{version}.json")
        with exp_filename.open('rt') as inp:
            expected = json.load(inp)
        expected['Games'][0]['start'] = data['Games'][0]['start']
        expected['Games'][0]['end'] = data['Games'][0]['end']
        self.assertEqual(data, expected)

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
