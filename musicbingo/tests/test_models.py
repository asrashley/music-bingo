"""
Unit tests for database models using the version 1 Schema.
"""

import copy
import datetime
import io
import json
import os
from pathlib import Path
import subprocess
from typing import Dict
import unittest

from pony.orm import db_session  # type: ignore

from musicbingo import models, utils
from musicbingo.options import DatabaseOptions, Options
from .fixture import fixture_filename

class TestDatabaseModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_opts = DatabaseOptions(database_provider='sqlite', database_filename=':memory:')
        cls.options = Options(database=db_opts)
        cls.options.exists = False
        models.bind(**cls.options.database_settings())

    def setUp(self):
        """called before each test"""
        self.options = TestDatabaseModels.options
        models.db.create_tables()

    def tearDown(self):
        """called after each test"""
        try:
            models.db.drop_all_tables(with_all_data=True)
        except Exception:
            pass

    @classmethod
    def tearDownClass(cls):
        models.db.disconnect()

    def test_v1_export(self):
        """
        Test exporting a database to a JSON file from the version 1 Schema
        """
        env = copy.copy(os.environ)
        env["DBVER"] = "1"
        args = [
            "python",
            "-m",
            "musicbingo.tests.schema_version_unit"
            ]
        result = subprocess.run(args, env=env, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout)


    def test_v2_export(self):
        """
        Test exporting a database to a JSON file from the version 1 Schema
        """
        env = copy.copy(os.environ)
        env["DBVER"] = "2"
        args = [
            "python",
            "-m",
            "musicbingo.tests.schema_version_unit"
            ]
        result = subprocess.run(args, env=env, stderr=subprocess.STDOUT)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_v1_import(self):
        """
        Test importing a v1 file into the current database Schema
        """
        json_filename = fixture_filename(f"tv-themes-v1.json")
        with json_filename.open('r') as src:
            expected = json.load(src)
        pk_maps = models.import_database(self.options, json_filename)
        for item in expected["Users"]:
            with db_session:
                user = models.User.get(username=item["username"])
                self.assertIsNotNone(user)
                if 'bingo_tickets' in item:
                    del item['bingo_tickets']
                self.assertDictEqual(item, user.to_dict(exclude=['bingo_tickets']))
        for item in expected["Games"]:
            with db_session:
                game = models.Game.get(id=item["id"])
                self.assertIsNotNone(game)
                actual = game.to_dict(with_collections=True)
                for key, value in item.items():
                    if isinstance(actual[key], datetime.datetime):
                        value = utils.from_isodatetime(value)
                        value = utils.make_naive_utc(value)
                    self.assertEqual(value, actual[key], key)
        for item in expected["Directories"]:
            with db_session:
                direc = models.Directory.get(name=item['name'])
                self.assertIsNotNone(direc)
                actual = direc.to_dict(with_collections=True)
                self.assertDictEqual(actual, item)
        for item in expected["Songs"]:
            with db_session:
                dir_pk = pk_maps["Directory"][item['directory']]
                direc = models.Directory.get(pk=dir_pk)
                self.assertIsNotNone(direc)
                song = models.Song.get(directory=direc, filename=item['filename'])
                self.assertIsNotNone(song)
                actual = song.to_dict(with_collections=False, exclude=["tracks"])
                del item['classtype']
                self.assertDictEqual(actual, item)
        for item in expected["Tracks"]:
            with db_session:
                pk = pk_maps["Track"][item['pk']]
                track = models.Track.get(pk=pk)
                self.assertIsNotNone(track)
                for field in ["filename", "title", "artist", "duration",
                              "album"]:
                    self.assertEqual(getattr(track.song, field), item[field], field)
                self.assertEqual(item['number'], track.number)
                self.assertEqual(item['start_time'], track.start_time)
                self.assertEqual(pk_maps["Game"][item["game"]], track.game.pk)
        for item in expected["BingoTickets"]:
            with db_session:
                pk = pk_maps["BingoTicket"][item['pk']]
                ticket = models.BingoTicket.get(pk=pk)
                self.assertIsNotNone(ticket)
                actual = ticket.to_dict(with_collections=True)
                self.assertDictEqual(actual, item)

    def test_v2_import(self):
        """
        Test importing a v2 file into the current database Schema
        """
        json_filename = fixture_filename(f"tv-themes-v2.json")
        with json_filename.open('r') as src:
            expected = json.load(src)
        pk_maps = models.import_database(self.options, json_filename)
        for item in expected["Users"]:
            with db_session:
                user = models.User.get(username=item["username"])
                self.assertIsNotNone(user)
                if 'bingo_tickets' in item:
                    del item['bingo_tickets']
                self.assertDictEqual(item, user.to_dict(exclude=['bingo_tickets']))
        for item in expected["Games"]:
            with db_session:
                game = models.Game.get(id=item["id"])
                self.assertIsNotNone(game)
                actual = game.to_dict(with_collections=True)
                for key, value in item.items():
                    if isinstance(actual[key], datetime.datetime):
                        value = utils.from_isodatetime(value)
                        value = utils.make_naive_utc(value)
                    self.assertEqual(value, actual[key], key)
        for item in expected["Directories"]:
            with db_session:
                direc = models.Directory.get(name=item['name'])
                self.assertIsNotNone(direc)
                actual = direc.to_dict(with_collections=True)
                self.assertDictEqual(actual, item)
        for item in expected["Songs"]:
            with db_session:
                dir_pk = pk_maps["Directory"][item['directory']]
                direc = models.Directory.get(pk=dir_pk)
                self.assertIsNotNone(direc)
                song = models.Song.get(directory=direc, filename=item['filename'])
                self.assertIsNotNone(song)
                actual = song.to_dict(with_collections=True)
                self.assertDictEqual(actual, item)
        for item in expected["Tracks"]:
            with db_session:
                pk = pk_maps["Track"][item['pk']]
                track = models.Track.get(pk=pk)
                self.assertIsNotNone(track)
                actual = track.to_dict(with_collections=True)
                self.assertDictEqual(actual, item)
        for item in expected["BingoTickets"]:
            with db_session:
                pk = pk_maps["BingoTicket"][item['pk']]
                ticket = models.BingoTicket.get(pk=pk)
                self.assertIsNotNone(ticket)
                actual = ticket.to_dict(with_collections=True)
                self.assertDictEqual(actual, item)
