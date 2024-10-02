"""
Extended TestCase class with functions for comparing database models
"""
from pathlib import Path
import re
from typing import List, Pattern, Union
import unittest

from sqlalchemy import Engine, text

from .mixin import TestCaseMixin

class ModelsUnitTest(TestCaseMixin, unittest.TestCase):
    """
    Extended TestCase class with functions for comparing database models
    """
    @staticmethod
    def fixture_filename(name: Union[str, Path]) -> Path:
        """returns absolute file path of the given fixture"""
        return Path(__file__).parent / "fixtures" / name

    @classmethod
    def load_fixture(cls, engine: Engine, filename: str) -> None:
        """
        Load the specified SQL file into the database
        """
        sql_filename: Path = cls.fixture_filename(filename)
        with sql_filename.open('rt', encoding="utf-8") as src:
            sql: str = src.read()
        insert_cmd: Pattern[str] = re.compile(
            r'^INSERT INTO (?P<table>\w+) VALUES\((?P<data>.+)\)$')
        with engine.connect() as conn:
            line: str
            for line in sql.split(';\n'):
                line = line.lstrip()
                if not line:
                    continue
                match: re.Match[str] | None = insert_cmd.match(line)
                if match:
                    names, params = ModelsUnitTest.split_columns(match['data'])
                    statement: str = f'INSERT INTO {match["table"]} VALUES({names})'
                    conn.execute(text(statement).bindparams(**params))
                else:
                    conn.execute(text(line))
            conn.commit()

    @staticmethod
    def split_columns(data: str) -> tuple[str, dict[str, Union[str, int, None]]]:
        """
        split a comma separated string into columns
        """
        result: dict[str, Union[str, int, None]] = {}
        col_names: list[str] = []

        def append_column(val: str, idx: int) -> None:
            name: str = f'col_{idx:02d}'
            if val.isdecimal():
                result[name] = int(val, 10)
            elif val == 'NULL':
                result[name] = None
            else:
                result[name] = val[1:-1]
            col_names.append(f':{name}')

        value: str = ''
        index: int = 1
        quoted: bool = False
        previous: str = ''
        for char in data:
            if char == ',' and not quoted:
                append_column(value, index)
                index += 1
                value = ''
            else:
                if char == "'":
                    quoted = not quoted
                if not (char == "'" and quoted and previous == "'"):
                    value += char
            previous = char
        if value != '':
            append_column(value, index)
        return (','.join(col_names), result,)

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
            kmsg = f'{msg}.{key}: '
            self.assertIn(key, expected, f'{kmsg}: not found in expected data')
            if isinstance(actual[key], dict):
                self.assertDictEqual(actual[key], expected[key], kmsg)
            elif isinstance(actual[key], list):
                self.assertListEqual(actual[key], expected[key], kmsg)
            else:
                kmsg = (
                    f'{kmsg} expected `{ expected[key] }` ({ type(expected[key]) }) ' +
                    f'got `{ actual[key] }` ({ type(actual[key]) })')
                self.assertEqual(actual[key], expected[key], kmsg)
