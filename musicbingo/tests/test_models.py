"""
Unit tests for database models using the version 1 Schema.
"""

import copy
import io
import json
import os
from pathlib import Path
import subprocess
import unittest

from pony.orm import db_session  # type: ignore

os.environ["DBVER"] = "1"

from musicbingo import models

class TestV1Schema(unittest.TestCase):

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
