"""
Various model management commands
"""

import argparse
import glob
from pathlib import Path
import logging
from typing import List, Optional, Set, cast

from sqlalchemy import func # type: ignore

from musicbingo.options import Options
from musicbingo.progress import TextProgress
from musicbingo.models import show_database, export_game, export_database
from musicbingo.models.db import DatabaseConnection, session_scope
from musicbingo.models.importer import Importer
from musicbingo.models.directory import Directory
from musicbingo.models.game import Game
from musicbingo.models.modelmixin import JsonObject
from musicbingo.models.song import Song
from musicbingo.models.user import User

class ModelOptions(Options):
    """
    Various model management commands
    """
    def __init__(self,
                 jsonfile: Optional[str] = None,
                 command: Optional[str] = None,
                 tables: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.jsonfile = jsonfile
        self.command = command
        self.tables = tables

    @classmethod
    def argument_parser(cls, include_clip_directory=True) -> argparse.ArgumentParser:
        """
        Adds extra arguments for database management
        """
        parser = Options.argument_parser(False)
        parser.add_argument(
            "--exists", action="store_true",
            help="Only import songs where the MP3 file exists")
        sub_parsers = parser.add_subparsers(dest="command", help="Database command")
        sub_parsers.add_parser("cleanup", help="Clean-up un-used directories from database")
        export_cmd = sub_parsers.add_parser("export", help="Export database")
        export_cmd.add_argument("--tables", help="tables to export")
        export_cmd.add_argument(
            "jsonfile",
            help="JSON filename for output")
        export_game_cmd = sub_parsers.add_parser(
            "export-game", help="Export one game from database")
        export_game_cmd.add_argument(
            "game_id",
            help="ID of game")
        export_game_cmd.add_argument(
            "jsonfile",
            help="JSON filename for output")
        export_all_games_cmd = sub_parsers.add_parser(
            "export-all-games", help="Export all games from database")
        export_all_games_cmd.add_argument(
            "jsonfile",
            help='JSON filename template for output (e.g. "games-{id}.json")')
        import_cmd = sub_parsers.add_parser("import", help="Import database")
        import_cmd.add_argument(
            "jsonfile",
            help="JSON filename to import")
        import_game_cmd = sub_parsers.add_parser(
            "import-gametracks", help="Import data from gameTracks.json")
        import_game_cmd.add_argument(
            "jsonfile", nargs="+",
            help="JSON filename to import")
        import_game_cmd.add_argument(
            "game_id", nargs='?', default='',
            help="ID of game")
        sub_parsers.add_parser("migrate", help="Migrate database with debug")
        show_cmd = sub_parsers.add_parser("show", help="Display database")
        show_cmd.add_argument("--tables", help="tables to display")
        change_password_cmd = sub_parsers.add_parser(
            "change-password", help="Change user's password")
        change_password_cmd.add_argument(
            "username",
            help='Username or email address of account to modify')
        change_password_cmd.add_argument(
            "password",
            help='New password')
        return parser

class DatabaseManagement:
    """
    Various model management commands
    """

    def run(self, args: List[str]) -> int:
        """
        Main entry point
        """
        logging.getLogger().setLevel(logging.INFO)
        log_format = (r"%(relativeCreated)06d:%(levelname)s:" +
                      "%(filename)s@%(lineno)d:%(funcName)s  %(message)s")
        logging.basicConfig(format=log_format)
        opts = ModelOptions.parse(args)
        if opts.command is None:
            # TODO: find better way to call parser print_help
            ModelOptions.parse(["-h"])
            return False
        if opts.command != 'migrate':
            DatabaseConnection.bind(opts.database, echo=False)
        cmd = opts.command.replace('-','_')
        if cmd == 'import':
            cmd = 'import_cmd'
        return getattr(self, cmd)(opts)

    # pylint: disable=unused-argument
    @staticmethod
    def cleanup(opts: ModelOptions) -> int:
        """
        Remove directories that do not contain any songs
        """
        empty: Set[int] = set()
        with session_scope() as session:
            query = session.query(
                Directory.pk, Directory.name, func.count(Song.pk)).select_from(
                    Directory).outerjoin(Song).group_by(Directory.pk)
            for item in query:
                pk, name, count = item
                if count == 0:
                    children = session.query(Directory).filter(Directory.parent_pk==pk).count()
                    if children == 0:
                        print(f'Deleting {pk}: {name}')
                        empty.add(pk)
            if empty:
                session.query(Directory).filter(
                    Directory.pk.in_(empty)).delete(synchronize_session=False)
        return 0

    @staticmethod
    def migrate(opts: ModelOptions) -> int:
        """
        Apply any database schema migrations.
        Migrations are handled automatically, but using this manual command
        allows it to be run with debug enabled
        """
        logging.getLogger().setLevel(logging.DEBUG)
        DatabaseConnection.bind(opts.database, debug=True, echo=True)
        return 0

    @staticmethod
    def export(opts: ModelOptions) -> int:
        """
        Export database
        """
        if opts.jsonfile is None:
            opts.usage()
            return 1
        filename = Path(opts.jsonfile).with_suffix('.json')
        logging.info('Dumping database into file "%s"', filename)
        req_tables = None
        if opts.tables:
            req_tables = set(opts.tables.split(','))
        with session_scope() as session:
            export_database(filename, opts, TextProgress(), session, req_tables)
        return 0

    @staticmethod
    def export_game(opts: ModelOptions) -> int:
        """
        Export one game from database
        """
        if opts.jsonfile is None or opts.game_id is None:
            opts.usage()
            return 1
        filename = Path(opts.jsonfile).with_suffix('.json')
        print(f'Dumping game "{opts.game_id}" to file "{filename}"')
        export_game(opts.game_id, filename)
        return 0

    @staticmethod
    def export_all_games(opts: ModelOptions) -> int:
        """
        Export all games.
        The command line parameter must be a template such as "game-{id}"
        """
        if opts.jsonfile is None:
            opts.usage()
            return 1
        if '{id}' not in opts.jsonfile:
            opts.usage()
            return 1
        game_ids = []
        with session_scope() as session:
            for game in session.query(Game):
                game_ids.append(game.id)
        for game_id in game_ids:
            name = opts.jsonfile.format(id=game_id)
            filename = Path(name).with_suffix('.json')
            print(f'Dumping game "{game_id}" to file "{filename}"')
            export_game(game_id, filename)
        return 0

    @staticmethod
    def import_cmd(opts: ModelOptions) -> int:
        """
        Import into database.
        """
        if opts.jsonfile is None:
            opts.usage()
            return 1
        filename = Path(opts.jsonfile)
        progress = TextProgress()
        with session_scope() as session:
            imp = Importer(opts, session, progress)
            imp.import_database(filename)
            print(imp.added)
        return 0

    @staticmethod
    def import_gametracks(opts: ModelOptions) -> int:
        """
        Import a game from a gameTracks file.
        If "jsonfile" contains wildcards, it will be expanded and
        each match will be imported
        """
        if opts.jsonfile is None:
            opts.usage()
            return 1
        files = []
        if opts.game_id:
            files.append(opts.jsonfile)
        else:
            for name in opts.jsonfile:
                files += glob.glob(name)
        totals: JsonObject = {}
        for jsonfile in files:
            filename = Path(jsonfile)
            progress = TextProgress()
            with session_scope() as session:
                imp = Importer(opts, session, progress)
                imp.import_game_tracks(filename, opts.game_id)
                print(imp.added)
                for key, count in imp.added.items():
                    totals[key] = totals.get(key, 0) + count
        print(totals)
        return 0

    @staticmethod
    def show(opts: ModelOptions) -> int:
        """
        Show contents of database
        """
        # pylint: disable=no-value-for-parameter
        tables = None
        if opts.tables:
            tables = set(opts.tables.split(','))
        with session_scope() as session:
            show_database(session, tables)
        return 0

    @staticmethod
    def change_password(opts: ModelOptions) -> int:
        """
        Reset a user's password
        """
        with session_scope() as session:
            user = User.get(session, username=opts.username)
            if user is None:
                user = User.get(session, email=opts.username)
            if user is None:
                print(f'Unknown user {opts.username}')
                return False
            cast(User, user).set_password(opts.password)
            print(f'Password for "{opts.username}" has been updated')
            return True
