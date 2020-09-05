"""
Tests of the Options() class and command line parsing
"""
from pathlib import Path
import unittest

from musicbingo.options import Options


class MockOptions(Options):
    """
    version of Options class that does not try and
    load an INI file
    """

    def load_ini_file(self) -> bool:
        return False

    def save_ini_file(self) -> None:
        pass


class TestOptions(unittest.TestCase):
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
            '--dbname', 'bingo',
            '--dbhost', 'db.unit.test',
            '--dbuser', 'dbuser',
            '--dbpasswd', 'secret',
            '--dbprovider', 'mysql',
            '--dbssl', '{"ssl_mode":"preferred"}',
            'Clips'])
        conn = opts.database.connection_string()
        self.assertEqual(conn, 'mysql://dbuser:secret@db.unit.test/bingo?ssl=true')

    def test_sqlite_database_connection_strings(self):
        """
        Test generation of sqlite connection string
        """
        opts = MockOptions.parse([
            '--id', '2020-02-14-1',
            '--dbname', 'bingo.db3',
            '--dbprovider', 'sqlite',
            'Clips'])
        conn = opts.database.connection_string()
        self.assertEqual(conn, 'sqlite:///bingo.db3')

    def test_mssql_database_connection_strings(self):
        """
        Test generation of mysql connection string
        """
        opts = MockOptions.parse([
            '--id', '2020-02-14-1',
            '--dbname', 'bingo',
            '--dbhost', 'db.unit.test',
            '--dbuser', 'dbuser',
            '--dbpasswd', 'secret',
            '--dbprovider', 'mssql+pyodbc',
            '--dbdriver', 'ODBC Driver 17 for SQL Server',
            'Clips'])
        conn = opts.database.connection_string()
        self.assertEqual(conn, ('mssql+pyodbc://dbuser:secret@db.unit.test/' +
                                'bingo?driver=ODBC+Driver+17+for+SQL+Server'))

if __name__ == "__main__":
    unittest.main()
