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
                         outdir / 'gameTracks.json')
        self.assertEqual(opts.track_listing_output_name(),
                         outdir / '2020-02-14-1 Track Listing.pdf')
        self.assertEqual(opts.ticket_results_output_name(),
                         outdir / '2020-02-14-1 Ticket Results.pdf')
        self.assertEqual(opts.ticket_checker_output_name(),
                         outdir / 'ticketTracks')
