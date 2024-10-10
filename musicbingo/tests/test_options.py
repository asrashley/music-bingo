"""
Tests of the Options() class and command line parsing
"""
from pathlib import Path
import unittest

from musicbingo.docgen.sizes.pagesize import PageSizes
from musicbingo.options import GameMode, Options
from musicbingo.options.page_sort_order import PageSortOrder
from musicbingo.palette import Palette
from musicbingo.tests.mixin import TestCaseMixin

class MockOptions(Options):
    """
    version of Options class that does not try and
    load an INI file
    """

    def load_ini_file(self) -> bool:
        return False

    def save_ini_file(self) -> None:
        pass


class TestOptions(TestCaseMixin, unittest.TestCase):
    """tests of the Options class"""

    def test_filename_generation(self):
        """
        Check filename generation
        """
        opts = MockOptions.parse(['--id', '2020-02-14-1', 'Clips'])
        cwd = Path.cwd()
        self.assertEqual(opts.clips(), cwd / "Clips")
        games_dest = cwd / Path(opts.games_dest)
        self.assertEqual(opts.game_destination_dir(),
                         games_dest / 'Game-2020-02-14-1')
        outdir = opts.game_destination_dir()
        self.assertEqual(opts.mp3_output_name(),
                         outdir / '2020-02-14-1 Game Audio.mp3')
        self.assertEqual(opts.bingo_tickets_output_name(),
                         outdir / '2020-02-14-1 Bingo Tickets - (24 Tickets).pdf')
        self.assertEqual(opts.game_info_output_name(),
                         outdir / 'game-2020-02-14-1.json')
        self.assertEqual(opts.track_listing_output_name(),
                         outdir / '2020-02-14-1 Track Listing.pdf')
        self.assertEqual(opts.ticket_results_output_name(),
                         outdir / '2020-02-14-1 Ticket Results.pdf')
        self.assertEqual(opts.ticket_checker_output_name(),
                         outdir / 'ticketTracks')

    def test_mysql_database_connection_strings(self):
        """
        Test generation of mysql connection string
        """
        opts = MockOptions.parse([
            '--id', '2020-02-14-1',
            '--db-name', 'bingo',
            '--db-host', 'db.unit.test',
            '--db-user', 'dbuser',
            '--db-passwd', 'secret',
            '--db-provider', 'mysql',
            '--db-ssl', '{"ssl_mode":"preferred"}',
            'Clips'])
        conn = opts.database.connection_string()
        self.assertEqual(conn, 'mysql://dbuser:secret@db.unit.test/bingo?ssl=true')

    def test_sqlite_database_connection_strings(self):
        """
        Test generation of sqlite connection string
        """
        opts = MockOptions.parse([
            '--id', '2020-02-14-1',
            '--db-name', 'bingo.db3',
            '--db-provider', 'sqlite',
            'Clips'])
        conn = opts.database.connection_string()
        self.assertEqual(conn, r'sqlite:///bingo.db3')

    def test_mssql_database_connection_strings(self):
        """
        Test generation of mysql connection string
        """
        opts = MockOptions.parse([
            '--id', '2020-02-14-1',
            '--db-name', 'bingo',
            '--db-host', 'db.unit.test',
            '--db-user', 'dbuser',
            '--db-passwd', 'secret',
            '--db-provider', 'mssql+pyodbc',
            '--db-driver', 'ODBC Driver 17 for SQL Server',
            'Clips'])
        conn = opts.database.connection_string()
        self.assertEqual(conn, ('mssql+pyodbc://dbuser:secret@db.unit.test/' +
                                'bingo?driver=ODBC+Driver+17+for+SQL+Server'))

    def test_app_options(self):
        """
        Test all app settings
        """
        name_map = {
            'games_dest': 'games',
            'game_id': 'id',
            'new_clips_dest': 'new-clips',
            'number_of_cards': 'cards',
            'include_artist': 'no-artist',
            'create_superuser': 'no-create-superuser',
        }
        expected = {
            'games_dest':  "Games Dest",
            'game_name_template': r'template-{game_id}',
            'game_info_filename': "info-{game_id}.json",
            'game_id': "2022-12-09",
            'title': "title",
            'clip_directory': 'ClipDir',
            'new_clips_dest': 'NewClipDir',
            'clip_start': "01:23",
            'clip_duration': 45,
            'colour_scheme': Palette.PRIDE,
            'number_of_cards': 45,
            'include_artist': False,
            'sort_order': PageSortOrder.NUMBER,
            'columns': 4,
            'rows': 2,
            'bitrate': 192,
            'crossfade': 250,
            'mp3_editor': 'mock',
            'mp3_player': 'mock',
            'checkbox': True,
            'cards_per_page': 4,
            'doc_per_page': True,
            'page_size': PageSizes.A5,
            'max_tickets_per_user': 1,
            'debug': True,
            'create_superuser': False,
            'secret_key': None,
            'mode': GameMode.BINGO,
        }
        args = ['--bingo']
        for key, value in expected.items():
            if key in {'clip_directory', 'mode', 'secret_key'}:
                continue
            try:
                param = name_map[key]
            except KeyError:
                param = key.replace('_', '-')
            args.append(f'--{param}')
            try:
                value = value.to_json()
            except AttributeError:
                pass
            if not isinstance(value, bool):
                args.append(str(value))
        args.append('ClipDir')
        opts = MockOptions.parse(args)
        actual = opts.to_dict()
        del actual['database']
        del actual['privacy']
        del actual['smtp']
        self.maxDiff = None
        self.assertDictEqual(expected, actual)

    def test_database_options(self):
        """
        Test all database settings
        """
        expected = {
            'provider': 'postgres',
            'connect_timeout': 30,
            'create_db': True,
            'driver': 'driver',
            'host': 'host',
            'name': 'dbname',
            'passwd': 'passwd',
            'port': 123,
            'ssl': r'{"ssl_mode": "preferred"}',
            'user': 'user',
        }
        args = []
        for key, value in expected.items():
            args.append(f'--db-{key}')
            if not isinstance(value, str):
                value = str(value)
            args.append(value)
        args.append('Clips')
        opts = MockOptions.parse(args)
        actual = opts.database.to_dict()
        self.assertDictEqual(expected, actual)

    def test_smtp_options(self):
        """
        Test all SMTP settings
        """
        expected = {
            'port': 234,
            'server': 'a.server',
            'sender': 'noreply@a.domain.name',
            'reply_to': 'reply@a.domain.name',
            'username': 'username',
            'password': 'password',
            'starttls': True
        }
        args = []
        for key, value in expected.items():
            args.append(f'--smtp-{key}')
            if key != 'starttls':
                args.append(str(value))
        args.append('Clips')
        opts = MockOptions.parse(args)
        actual = opts.smtp.to_dict()
        self.assertDictEqual(expected, actual)

    def test_privacy_options(self):
        """
        Test all privacy settings
        """
        expected = {
            "name": "Company",
            "email": "test@an.email.address",
            "address": "A road to nowhere",
            "data_center": "Europe",
            "ico": "https://ico.link/blah",
        }
        args = []
        for key, value in expected.items():
            args.append(f'--privacy-{key}')
            args.append(value)
        args.append('Clips')
        opts = MockOptions.parse(args)
        actual = opts.privacy.to_dict()
        self.assertDictEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()
