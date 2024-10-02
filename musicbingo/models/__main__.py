"""
Main entrypoint for database management commands.

It can be used with:
    python -m musicbingo.models

"""

import sys

from .management import DatabaseManagement

def main() -> int:
    """
    entry point for database management commands
    """
    mgmt = DatabaseManagement()
    return mgmt.run(sys.argv[1:])

if __name__ == "__main__":
    main()
