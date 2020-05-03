"""
Unit test for the various database models Schemas.
"""

import io
import json
import os
from pathlib import Path
import unittest

from pony.orm import db_session  # type: ignore

from musicbingo import models
from .fixture import fixture_filename

class TestDatabaseSchema(unittest.TestCase):
    def tearDown(self):
        """called after each test"""
        #models.db.drop_all_tables(with_all_data=True)
        models.db.disconnect()

    def test_export(self):
        """
        Test exporting a database to a JSON file
        """
        schema_version = models.db.schema_version
        models.__setup = True
        models.db.bind(provider='sqlite', filename=':memory:')
        sql_filename = fixture_filename(f"tv-themes-v{schema_version}.sql")
        with sql_filename.open('rt') as src:
            sql = src.read()
        with db_session:
            conn = models.db.get_connection()
            for line in sql.split(';'):
                while line and line[0] in [' ', '\r', '\n']:
                    line = line[1:]
                if not line:
                    continue
                #print(f'"{line}"')
                if line in ['BEGIN TRANSACTION', 'COMMIT']:
                    continue
                conn.execute(line)
        models.db.generate_mapping(create_tables=False)
        output = io.StringIO()
        models.export_database_to_file(output)
        json_filename = fixture_filename(f"tv-themes-v{schema_version}.json")
        with json_filename.open('r') as src:
            expected_json = json.load(src)
        output.seek(0)
        actual_json = json.load(output)
        self.assertDictEqual(actual_json, expected_json)
