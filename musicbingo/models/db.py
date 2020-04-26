import os

from pony.orm import Database

schema_version = int(os.environ.get("DBVER", "2"), 10)

db = Database()

