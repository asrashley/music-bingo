"""
Unit tests for GameGenerator
"""
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from typing import Dict, List, Optional
import unittest
from unittest import mock

from freezegun import freeze_time  # type: ignore

from musicbingo.assets import Assets
from musicbingo.bingoticket import BingoTicket
from musicbingo.directory import Directory
from musicbingo.generator import GameGenerator
from musicbingo.options import DatabaseOptions, Options, PageSortOrder
from musicbingo.palette import Palette
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.progress import Progress
from musicbingo.docgen.sizes.pagesize import PageSizes
from musicbingo.song import Song
from musicbingo.track import Track
from musicbingo import models

from .mock_editor import MockMP3Editor
from .mock_docgen import MockDocumentGenerator
from .mock_random import MockRandom
from .modelsunittest import ModelsUnitTest

class MockPosixPath(PurePosixPath):
    """
    Version of PosixPath that can be used in unit tests
    """

    def resolve(self) -> "MockPosixPath":
        """
        convert Path to an absolute path
        """
        return self

class TestGameGenerator(ModelsUnitTest):
    """tests of the GameGenerator class"""

    EXPECTED_OUTPUT: Optional[Path] = None  # Path(__file__).parent / "expected"

    def setUp(self):
        """called before each test"""
        options = Options(database=DatabaseOptions(
            database_provider='sqlite', database_name=':memory:'))
        models.db.DatabaseConnection.bind(options.database, create_tables=True)
        self.tmpdir = Path(tempfile.mkdtemp())
        #self.songs = []
        filename = self.fixture_filename("songs.json")
        clips = Directory(None, MockPosixPath("/home/bingo/Clips"))
        self.directory = Directory(clips, clips._fullpath / 'Fifties')
        self.directory.title = 'The 50s 60 Classic Fifties Hits'
        self.directory.artist = 'Various Artists'
        with filename.open('r', encoding='utf-8') as src:
            for index, item in enumerate(json.load(src)):
                #item['filepath'] = filename.parent / item['filename']
                filename = item.pop('filename')
                item['bitrate'] = 256
                item['sample_rate'] = 44100
                item['sample_width'] = 16
                item['channels'] = 2
                self.directory.songs.append(
                    Song(filename, parent=self.directory, ref_id=index + 1, **item))
        with models.db.session_scope() as session:
            clips.save(session, options)
            db_dir = self.directory.save(session, options)
            for song in self.directory.songs:
                song.save(session, db_dir)

    def tearDown(self):
        """called after each test"""
        # pylint: disable=broad-except
        try:
            shutil.rmtree(str(self.tmpdir))
        except (Exception) as ex:
            print(ex)
        models.db.DatabaseConnection.close()

    def test_generate_bingo_game_letter_page_size(self):
        """
        Test of Bingo game generation (letter page size)
        """
        for cards_per_page in [1, 2, 3, 4, 6]:
            # pylint: disable=no-value-for-parameter
            self.check_bingo_game_pipeline(PageSizes.LETTER, cards_per_page, 'blue')

    def test_generate_bingo_game_a3_page_size(self):
        """
        Test of Bingo game generation (A3 page, 2 cards per page)
        """
        for cards_per_page in [1, 2, 3, 4, 6]:
            # pylint: disable=no-value-for-parameter
            self.check_bingo_game_pipeline(PageSizes.A3, cards_per_page, 'blue')

    def test_generate_bingo_game_a4_with_2_cards_per_page(self):
        """
        Test of Bingo game generation (A4 page, 2 cards per page)
        """
        # pylint: disable=no-value-for-parameter
        self.check_bingo_game_pipeline(PageSizes.A4, 2, 'blue')

    def test_generate_bingo_game_a4_with_3_cards_per_page(self):
        """
        Test of Bingo game generation (A4 page, 3 cards per page)
        """
        for colour in Palette.names():
            # pylint: disable=no-value-for-parameter
            self.check_bingo_game_pipeline(PageSizes.A4, 3, colour.lower())

    def test_generate_bingo_game_a4_with_4_cards_per_page(self):
        """
        Test of Bingo game generation (A4 page, 4 cards per page)
        """
        # pylint: disable=no-value-for-parameter
        self.check_bingo_game_pipeline(PageSizes.A4, 4, 'blue')

    def test_generate_bingo_game_a4_with_6_cards_per_page(self):
        """
        Test of Bingo game generation (A4 page, 6 cards per page)
        """
        # pylint: disable=no-value-for-parameter
        self.check_bingo_game_pipeline(PageSizes.A4, 6, 'blue')

    def test_generate_bingo_game_a5_with_2_cards_per_page(self):
        """
        Test of Bingo game generation (A5 page, 2 cards per page)
        """
        # pylint: disable=no-value-for-parameter
        self.check_bingo_game_pipeline(PageSizes.A5, 2, 'blue')

    def test_generate_bingo_game_a5_with_3_cards_per_page(self):
        """
        Test of Bingo game generation (A5 page, 3 cards per page)
        """
        # pylint: disable=no-value-for-parameter
        self.check_bingo_game_pipeline(PageSizes.A5, 3, 'blue')

    def test_generate_bingo_game_a5_with_4_cards_per_page(self):
        """
        Test of Bingo game generation (A5 page, 4 cards per page)
        """
        # pylint: disable=no-value-for-parameter
        self.check_bingo_game_pipeline(PageSizes.A5, 4, 'blue')

    def test_generate_bingo_game_a5_with_6_cards_per_page(self):
        """
        Test of Bingo game generation (A5 page, 6 cards per page)
        """
        # pylint: disable=no-value-for-parameter
        self.check_bingo_game_pipeline(PageSizes.A5, 6, 'blue')

    def test_card_sorting(self) -> None:
        """
        Check each of the card sorting methods
        """
        cards: List[BingoTicket] = []
        tracks: List[Track] = []
        start_time = 0
        for index, song in enumerate(self.directory.songs):
            trk = Track(song, PRIME_NUMBERS[index], start_time)
            start_time += song.duration
            tracks.append(trk)
        for index in range(len(tracks) - 15):
            tkt = BingoTicket(
                palette=Palette.BLUE, columns=5, number=(index + 1),
                tracks=(tracks[index: index+15]))
            tkt.wins_on_track = len(tracks)
            cards.append(tkt)
        for index, card in enumerate(cards[-8:]):
            card.wins_on_track -= index + 1
        opts = Options(
            game_id='test-sort',
            games_dest=str(self.tmpdir),
            number_of_cards=len(cards),
            title='Game title',
            cards_per_page=4,
            colour_scheme=Palette.BLUE,
            crossfade=0,
            page_size=PageSizes.A4,
            sort_order=PageSortOrder.INTERLEAVE
        )
        editor = MockMP3Editor()
        docgen = MockDocumentGenerator()
        progress = Progress()
        gen = GameGenerator(opts, editor, docgen, progress)
        result = gen.sort_cards_by_page(cards)
        # print([t.number for t in result])
        expected: List[int] = []
        buckets: Dict[int, List[int]] = {}
        for index in range(len(cards)):
            if (index % 16) == 0:
                for val in buckets.values():
                    expected += val
                buckets = {}
            bkt = index % 4
            try:
                buckets[bkt].append(index + 1)
            except KeyError:
                buckets[bkt] = [index + 1]
        for val in buckets.values():
            expected += val
        # print(expected)
        self.assertEqual(expected, [ticket.number for ticket in result])
        gen.options.sort_order = PageSortOrder.NUMBER
        result = gen.sort_cards_by_page(cards)
        # print('by number:')
        # print([t.number for t in result])
        expected = [(i+1) for i in range(len(cards))]
        self.assertEqual(expected, [ticket.number for ticket in result])
        gen.options.sort_order = PageSortOrder.WINNER
        result = gen.sort_cards_by_page(cards)
        # print('by winner:')
        # print([(t.number, t.wins_on_track) for t in result])
        # print([t.number for t in result])
        first_win = min(t.wins_on_track for t in cards)
        for card in result:
            self.assertGreaterThanOrEqual(card.wins_on_track, first_win)
            first_win = card.wins_on_track

    # pylint: disable=too-many-locals,too-many-statements
    @mock.patch('musicbingo.generator.random.shuffle')
    @mock.patch('musicbingo.generator.secrets.randbelow')
    def check_bingo_game_pipeline(self, page_size: PageSizes, cards_per_page: int,
                                  colour_scheme: str, mock_randbelow, mock_shuffle):
        """
        Test of complete Bingo game generation
        """
        self.maxDiff = 500
        mrand = MockRandom()
        mock_randbelow.side_effect = mrand.randbelow
        mock_shuffle.side_effect = mrand.shuffle
        self.assertIsInstance(page_size, PageSizes)
        opts = Options(
            game_id='test-pipeline',
            games_dest=str(self.tmpdir),
            number_of_cards=24,
            title='Game title',
            cards_per_page=cards_per_page,
            colour_scheme=colour_scheme,
            crossfade=0,
            page_size=page_size,
            sort_order=PageSortOrder.NUMBER,
        )
        editor = MockMP3Editor()
        docgen = MockDocumentGenerator()
        progress = Progress()
        time_str = "2020-01-02T03:04:05Z"
        # pylint: disable=unused-variable
        with freeze_time(time_str) as frozen_time:
            gen = GameGenerator(opts, editor, docgen, progress)
            # pylint: disable=no-value-for-parameter
            gen.generate(self.directory.songs[:40])
        # pylint: disable=consider-using-dict-items,consider-iterating-dictionary
        for pdf in docgen.output.keys():
            self.update_extra_files(docgen.output[pdf])
        fixture_filename = f'complete_bingo_game_{cards_per_page}_cards_{page_size}'
        if colour_scheme != 'blue':
            fixture_filename += f'_{colour_scheme}'
        fixture_filename += '.json'
        if self.EXPECTED_OUTPUT is not None:
            destination = self.EXPECTED_OUTPUT / fixture_filename
            with destination.open('w') as rjs:
                json.dump({"docgen": docgen.output, "editor": editor.output},
                          rjs, indent=2, sort_keys=True)
        filename = self.fixture_filename(fixture_filename)
        with filename.open('r', encoding='utf-8') as jsrc:
            expected = json.load(jsrc)
        self.assertEqual(len(docgen.output), 3)
        ticket_file = "test-pipeline Bingo Tickets - (24 Tickets).pdf"
        self.assert_dictionary_equal(expected['docgen'][ticket_file],
                                     docgen.output[ticket_file])

        results_file = "test-pipeline Ticket Results.pdf"
        self.assert_dictionary_equal(expected['docgen'][results_file],
                                     docgen.output[results_file])

        listings_file = "test-pipeline Track Listing.pdf"
        self.assert_dictionary_equal(expected['docgen'][listings_file],
                                     docgen.output[listings_file])

        self.assertEqual(len(editor.output), 1)
        mp3_file = "test-pipeline Game Audio.mp3"
        self.assert_dictionary_equal(expected['editor'][mp3_file],
                                     editor.output[mp3_file])

        json_file = opts.game_info_output_name()
        self.assertTrue(json_file.exists())
        with json_file.open('r') as src:
            result_game_tracks = json.load(src)
        # print(result_game_tracks['Directories'])
        fixture_filename = f'generator-gameTracks_{cards_per_page}_cards_{page_size}'
        if colour_scheme != 'blue':
            fixture_filename += f'_{colour_scheme}'
        fixture_filename += '.json'
        if self.EXPECTED_OUTPUT is not None:
            destination = self.EXPECTED_OUTPUT / fixture_filename
            with destination.open('wt') as rjs:
                json.dump(result_game_tracks, rjs, indent=2, sort_keys=True)
        filename = self.fixture_filename(fixture_filename)
        with filename.open('rt', encoding='utf-8') as src:
            expected_game_tracks = json.load(src)
        for field in ['BingoTickets', 'Directories', 'Games', 'Songs', 'Tracks']:
            self.assertModelListEqual(expected_game_tracks[field],
                                      result_game_tracks[field], field)

    def update_extra_files(self, expected: Dict) -> None:
        """
        Update the any references to "Extra-Files" from an absolute path to relative
        """
        prefix = Assets.get_data_filename(
            'placeholder.txt').as_posix().replace('/placeholder.txt', '')
        for element in expected['elements']:
            if (isinstance(element, dict) and 'elements' in element):
                self.update_extra_files(element)
            elif (isinstance(element, dict) and 'filename' in element and
                    element['filename'].startswith(prefix)):
                if isinstance(element['filename'], Path):
                    filename = element['filename']
                else:
                    filename = Path(element['filename'])
                element['filename'] = f'Extra-Files/{filename.name}'

    def assert_dictionary_equal(self, expected: Dict, actual: Dict,
                                path: str = '') -> None:
        """
        Assert that both dictionaries are the same
        """
        self.assertListEqual(sorted(expected.keys()), sorted(actual.keys()))
        for key, value in expected.items():
            if isinstance(value, dict):
                self.assert_dictionary_equal(value, actual[key], f'{path}{key}.')
                continue
            if isinstance(value, (list, tuple)):
                self.assert_lists_equal(list(value), list(actual[key]),
                                        f'{path}{key}.')
                continue
            self.assertEqual(
                value, actual[key],
                f'{path}{key}: Expected {actual[key]} to equal "{value}"')

    def assert_lists_equal(self, expected: List, actual: List,
                           path: str = '') -> None:
        """
        Assert that both lists are the same
        """
        self.assertEqual(len(expected), len(actual), path)
        index: int = -1
        for exp, act in zip(expected, actual):
            index += 1
            if isinstance(exp, dict):
                self.assert_dictionary_equal(exp, act, f'{path}[{index}]')
            elif isinstance(exp, (list, tuple)):
                self.assert_lists_equal(list(exp), list(act), f'{path}[{index}]')
            else:
                self.assertEqual(
                    exp, act,
                    f'{path}[{index}]: Expected "{act}" to equal "{exp}"')


if __name__ == "__main__":
    unittest.main()
