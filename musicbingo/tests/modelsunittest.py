"""
Extended TestCase class with functions for comparing database models
"""
from pathlib import Path
from typing import List
import unittest

class ModelsUnitTest(unittest.TestCase):
    """
    Extended TestCase class with functions for comparing database models
    """
    @staticmethod
    def fixture_filename(name: str) -> Path:
        """returns absolute file path of the given fixture"""
        return Path(__file__).parent / "fixtures" / name

    @classmethod
    def load_fixture(cls, engine, filename: str) -> None:
        """
        Load the specified SQL file into the database
        """
        sql_filename = cls.fixture_filename(filename)
        # print(sql_filename)
        with sql_filename.open('rt', encoding="utf-8") as src:
            sql = src.read()
        with engine.connect() as conn:
            for line in sql.split(';\n'):
                while line and line[0] in [' ', '\r', '\n']:
                    line = line[1:]
                if not line:
                    continue
                # print(f'"{line}"')
                if line in ['BEGIN TRANSACTION', 'COMMIT']:
                    continue
                conn.execute(line)

    def assertModelListEqual(self, actual: List, expected: List, msg: str) -> None:
        """
        assert that two lists of database models are identical
        """
        self.assertEqual(len(actual), len(expected), msg)
        pk_map = {}
        for item in expected:
            if 'pk' in item:
                pk_map[item['pk']] = item
        for idx, item in enumerate(actual):
            if 'pk' in item:
                pk = item['pk']
                self.assertIn(pk, pk_map, f'{msg}[{idx}] (pk={pk})')
                expect = pk_map[pk]
                self.assertModelEqual(item, expect, f'{msg}[{idx}] (pk={pk})')
            else:
                self.assertIn(idx, expected, f'{msg}[{idx}]')
                expect = expected[idx]
                self.assertModelEqual(item, expect, f'{msg}[{idx}]')

    def assertModelEqual(self, actual, expected, msg) -> None:
        """
        assert that two database models are identical
        """
        for key in actual.keys():
            if isinstance(actual[key], list):
                actual[key].sort()
                self.assertIn(key, expected, f'{msg}: Expected data missing field {key}')
                expected[key].sort()
            kmsg = f'{msg}: {key}'
            self.assertIn(key, expected, f'{kmsg}: not found in expected data')
            if isinstance(actual[key], dict):
                self.assertDictEqual(actual[key], expected[key], kmsg)
            elif isinstance(actual[key], list):
                self.assertListEqual(actual[key], expected[key], kmsg)
            else:
                self.assertEqual(actual[key], expected[key], kmsg)
