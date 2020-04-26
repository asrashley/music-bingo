from pathlib import Path
import sys

from musicbingo.options import Options
from musicbingo.models import bind, import_database, dump_database

def usage():
    print(f'Usage:\n    python -m musicbinfo.models [<options>] (dump|import) <filename>')

def main():

    if len(sys.argv) < 3:
        usage()
        return 1
    opts = Options.parse(sys.argv[1:-2])
    settings = opts.database_settings()
    bind(**settings)
    filename = Path(sys.argv[-1]).with_suffix('.json')
    if sys.argv[-2] == 'dump':
        print(f'Dumping database into file "{filename}"')
        dump_database(filename)
        return 0
    if sys.argv[-2] == 'import':
        print(f'Importing database from file "{filename}"')
        import_database(filename)
        return 0
    usage()
    return 1

if __name__ == "__main__":
    main()
