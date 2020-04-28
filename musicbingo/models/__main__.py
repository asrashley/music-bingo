import argparse
from pathlib import Path
import sys
from typing import Optional

from musicbingo.options import Options
from musicbingo.models import bind, import_database, export_database, show_database

class ModelOptions(Options):
    def __init__(self, 
                 filename: Optional[str] = None,
                 command: Optional[str] = None,
                 **kwargs):
        super(ModelOptions, self).__init__(**kwargs)
        self.filename = filename
        self.command = command
        
    @classmethod
    def argument_parser(cls) -> argparse.ArgumentParser:
        parser = Options.argument_parser(False)
        parser.add_argument(
            "--exists", action="store_true",
            help="Only import songs where the MP3 file exists")
        parser.add_argument(
            "command", type=str, choices=["export", "show", "import"],
            help="database command")
        parser.add_argument(
            "jsonfile", nargs='?',
            help="JSON filename for dump or import")
        return parser
        
def main():
    opts = ModelOptions.parse(sys.argv[1:])
    settings = opts.database_settings()
    bind(**settings)
    if opts.command == 'export':
        if opts.jsonfile is None:
            opts.usage()
            return 1
        filename = Path(opts.jsonfile).with_suffix('.json')
        print(f'Dumping database into file "{filename}"')
        export_database(filename)
        return 0
    elif opts.command == 'import':
        if opts.jsonfile is None:
            opts.usage()
            return 1
        filename = Path(opts.jsonfile)
        print(f'Importing database from file "{filename}"')
        import_database(opts, filename)
        return 0
    elif opts.command == 'show':
        show_database()
        return 0
    opts.usage()
    return 1

if __name__ == "__main__":
    main()
