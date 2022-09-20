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
from musicbingo.directory import Directory
from musicbingo.generator import GameGenerator
from musicbingo.options import DatabaseOptions, Options
from musicbingo.progress import Progress
from musicbingo.song import Song
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

    @mock.patch('musicbingo.generator.random.shuffle')
    @mock.patch('musicbingo.generator.secrets.randbelow')
    def test_complete_bingo_game_pipeline(self, mock_randbelow, mock_shuffle):
        """
        Test of complete Bingo game generation
        """
        self.maxDiff = 500
        mrand = MockRandom()
        mock_randbelow.side_effect = mrand.randbelow
        mock_shuffle.side_effect = mrand.shuffle
        opts = Options(
            game_id='test-pipeline',
            games_dest=str(self.tmpdir),
            number_of_cards=24,
            title='Game title',
            crossfade=0,
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
        if self.EXPECTED_OUTPUT is not None:
            destination = self.EXPECTED_OUTPUT / "test_complete_bingo_game_pipeline.json"
            with destination.open('w') as rjs:
                json.dump({"docgen": docgen.output, "editor": editor.output},
                          rjs, indent=2, sort_keys=True)
        filename = self.fixture_filename("test_complete_bingo_game_pipeline.json")
        with filename.open('r', encoding='utf-8') as jsrc:
            expected = json.load(jsrc)
        self.assertEqual(len(docgen.output), 3)
        ticket_file = "test-pipeline Bingo Tickets - (24 Tickets).pdf"
        self.update_extra_files(expected['docgen'][ticket_file])
        self.assert_dictionary_equal(expected['docgen'][ticket_file],
                                     docgen.output[ticket_file])

        results_file = "test-pipeline Ticket Results.pdf"
        self.update_extra_files(expected['docgen'][results_file])
        self.assert_dictionary_equal(expected['docgen'][results_file],
                                     docgen.output[results_file])

        listings_file = "test-pipeline Track Listing.pdf"
        self.update_extra_files(expected['docgen'][listings_file])
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
        if self.EXPECTED_OUTPUT is not None:
            destination = self.EXPECTED_OUTPUT / "generator-gameTracks.json"
            with destination.open('wt') as rjs:
                json.dump(result_game_tracks, rjs, indent=2, sort_keys=True)
        filename = self.fixture_filename("generator-gameTracks.json")
        with filename.open('rt', encoding='utf-8') as src:
            expected_game_tracks = json.load(src)
        for field in ['BingoTickets', 'Directories', 'Games', 'Songs', 'Tracks']:
            self.assertModelListEqual(expected_game_tracks[field],
                                      result_game_tracks[field], field)

    @staticmethod
    def update_extra_files(expected: Dict) -> None:
        """
        Update the any references to "Extra-Files" to an absolute path
        """
        for element in expected['elements']:
            if (isinstance(element, dict) and 'filename' in element and
                    element['filename'].startswith('Extra-Files')):
                element['filename'] = Assets.get_data_filename(
                    Path(element['filename']).name).as_posix()

    def assert_dictionary_equal(self, expected: Dict, actual: Dict,
                                path: str = '') -> None:
        """
        Assert that both dictionaries are the same
        """
        self.assertSequenceEqual(sorted(expected.keys()), sorted(actual.keys()))
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
                continue
            if isinstance(exp, (list, tuple)):
                self.assert_lists_equal(list(exp), list(act), f'{path}[{index}]')
                continue
            self.assertEqual(
                exp, act,
                f'{path}[{index}]: Expected "{act}" to equal "{exp}"')


if __name__ == "__main__":
    unittest.main()
