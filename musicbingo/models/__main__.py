"""
Various model management commands
"""

import argparse
from pathlib import Path
import logging
import sys
from typing import Optional

from musicbingo.options import Options
from musicbingo.progress import TextProgress
from musicbingo.models import show_database, export_game, export_database
from musicbingo.models.db import DatabaseConnection, session_scope
from musicbingo.models.importer import Importer
from musicbingo.models.game import Game

class ModelOptions(Options):
    """
    Various model management commands
    """
    def __init__(self,
                 jsonfile: Optional[str] = None,
                 command: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.jsonfile = jsonfile
        self.command = command

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
        export_cmd = sub_parsers.add_parser("export", help="Export database")
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
            "jsonfile",
            help="JSON filename to import")
        import_game_cmd.add_argument(
            "game_id", nargs='?', default='',
            help="ID of game")
        sub_parsers.add_parser("migrate", help="Migrate database with debug")
        sub_parsers.add_parser("show", help="Display database")
        return parser


# pylint: disable=too-many-return-statements,too-many-statements
def main():
    """
    entry point for database management commands
    """
    logging.getLogger().setLevel(logging.INFO)
    log_format = (r"%(relativeCreated)06d:%(levelname)s:" +
                  "%(filename)s@%(lineno)d:%(funcName)s  %(message)s")
    logging.basicConfig(format=log_format)
    opts = ModelOptions.parse(sys.argv[1:])
    if opts.command == 'migrate':
        logging.getLogger().setLevel(logging.DEBUG)
        DatabaseConnection.bind(opts.database, debug=True, echo=True)
        return 0
    DatabaseConnection.bind(opts.database)
    if opts.command == 'export':
        if opts.jsonfile is None:
            opts.usage()
            return 1
        filename = Path(opts.jsonfile).with_suffix('.json')
        logging.info('Dumping database into file "%s"', filename)
        export_database(filename, TextProgress())
        return 0
    if opts.command == 'export-game':
        if opts.jsonfile is None or opts.game_id is None:
            opts.usage()
            return 1
        filename = Path(opts.jsonfile).with_suffix('.json')
        print(f'Dumping game "{opts.game_id}" to file "{filename}"')
        export_game(opts.game_id, filename)
        return 0
    if opts.command == 'export-all-games':
        if opts.jsonfile is None:
            opts.usage()
            return 1
        if '{id}' not in opts.jsonfile:
            opts.usage()
            return 1
        with session_scope() as session:
            for game in session.query(Game):
                name = opts.jsonfile.format(id=game.id)
                filename = Path(name).with_suffix('.json')
                print(f'Dumping game "{game.id}" to file "{filename}"')
                export_game(game.id, filename)
        return 0
    if opts.command == 'import':
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
    if opts.command == 'import-gametracks':
        if opts.jsonfile is None:
            opts.usage()
            return 1
        filename = Path(opts.jsonfile)
        progress = TextProgress()
        with session_scope() as session:
            imp = Importer(opts, session, progress)
            imp.import_game_tracks(filename, opts.game_id)
            print(imp.added)
        return 0
    if opts.command == 'show':
        # pylint: disable=no-value-for-parameter
        show_database()
        return 0
    opts.usage()
    return 1


if __name__ == "__main__":
    main()
