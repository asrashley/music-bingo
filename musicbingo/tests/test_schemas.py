"""
Unit tests of JSON Schemas used to check input files
"""

import json
import unittest

from fastjsonschema.exceptions import JsonSchemaException  # type: ignore

from musicbingo.schemas import JsonSchema, validate_json
from .fixture import fixture_filename

class TestOptions(unittest.TestCase):
    """tests of the JSON Schemas"""

    # pylint: disable=no-self-use
    def test_v1_game_tracks(self):
        """
        Check validating a v1 game file
        """
        json_filename = fixture_filename("gameTracks-v1.json")
        with json_filename.open('rt', encoding='utf-8') as src:
            source = json.load(src)
        validate_json(JsonSchema.GAME_TRACKS_V1_V2, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V3, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V4, source)

    # pylint: disable=no-self-use
    def test_v1_bug_game_tracks(self):
        """
        Check validating a v1 game file that has the album name bug
        """
        json_filename = fixture_filename("gameTracks-v1-bug.json")
        with json_filename.open('rt', encoding='utf-8') as src:
            source = json.load(src)
        validate_json(JsonSchema.GAME_TRACKS_V1_V2, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V3, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V4, source)

    # pylint: disable=no-self-use
    def test_v2_game_tracks(self):
        """
        Check validating a v2 game file
        """
        json_filename = fixture_filename("gameTracks-v2.json")
        with json_filename.open('rt', encoding='ascii') as src:
            source = json.load(src)
        validate_json(JsonSchema.GAME_TRACKS_V1_V2, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V3, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V4, source)

    # pylint: disable=no-self-use
    def test_v3_game_tracks(self):
        """
        Check validating a v3 game file
        """
        json_filename = fixture_filename("gameTracks-v3.json")
        with json_filename.open('rt', encoding='utf-8') as src:
            source = json.load(src)
        validate_json(JsonSchema.GAME_TRACKS_V3, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V1_V2, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V4, source)

    # pylint: disable=no-self-use
    def test_v4_game_tracks(self):
        """
        Check validating a v4 game file
        """
        json_filename = fixture_filename("gameTracks-v4.json")
        with json_filename.open('rt', encoding='utf-8') as src:
            source = json.load(src)
        validate_json(JsonSchema.GAME_TRACKS_V4, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V1_V2, source)
        with self.assertRaises(JsonSchemaException):
            validate_json(JsonSchema.GAME_TRACKS_V3, source)

    # pylint: disable=no-self-use
    def test_game_tracks(self):
        """
        Check validating all versions of game file
        """
        for version in range(1, 5):
            json_filename = fixture_filename(f"gameTracks-v{version}.json")
            with json_filename.open('rt', encoding='utf-8') as src:
                source = json.load(src)
            validate_json(JsonSchema.GAME_TRACKS, source)
            with self.assertRaises(JsonSchemaException):
                validate_json(JsonSchema.DATABASE, source)

    # pylint: disable=no-self-use
    def test_database_versions(self):
        """
        Check validating a v1 .. v5 database file
        """
        for version in range(1, 6):
            json_filename = fixture_filename(f"tv-themes-v{version}.json")
            # print(json_filename)
            with json_filename.open('rt', encoding='utf-8') as src:
                source = json.load(src)
            try:
                validate_json(JsonSchema.DATABASE, source)
            except JsonSchemaException as err:
                print(dir(err))
                print(err.message)
                print(err.path)
                print(err.definition)
                raise
            if version < 5:
                json_filename = fixture_filename(f"gameTracks-v{version}.json")
                with json_filename.open('rt', encoding='utf-8') as src:
                    source = json.load(src)
                with self.assertRaises(JsonSchemaException):
                    validate_json(JsonSchema.DATABASE, source)

if __name__ == "__main__":
    unittest.main()
