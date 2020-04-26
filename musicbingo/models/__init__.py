"""
This file contains all of the database models.

"""
import copy
from datetime import datetime, timedelta
import json
from pathlib import Path
import secrets
import threading
import typing

from pony.orm import Database, PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import perm, composite_key, db_session, select  # type: ignore
from pony.orm import user_groups_getter, commit, exists, show # type: ignore
from pony.orm import Json, flush # type: ignore

from musicbingo.utils import flatten, from_isodatetime

from musicbingo.models.db import db

from musicbingo.models.v1 import BingoTicket, Directory, Game, Group, Song, Track, User 

with db.set_perms_for(User, BingoTicket, Game, Track):
    perm('view', group='anybody').exclude(User.password, User.email)

__setup = False
__bind_lock = threading.Lock()

def bind(**bind_args):
    """
    setup database to be able to use it
    """
    global __setup
    global __bind_lock
    with __bind_lock:
        if __setup == True:
            return
        basedir = Path(__file__).parents[1]
        print('bind database', bind_args)
        db.bind(**bind_args)
        db.generate_mapping(create_tables=True)
        with db_session:
            admin = User.get(username="admin")
            if admin is None:
                password = secrets.token_urlsafe(14)
                groups_mask = Group.admin.value + Group.users.value
                admin = User(username="admin", email="admin@music.bingo",
                             groups_mask=groups_mask,
                             password=User.hash_password(password))
                #TODO: investigate why groups_mask not working when
                #creating admin account
                admin.set_groups([Group.admin, Group.users])
                print(f'Created admin account "{admin.username}" ({admin.email}) with password "{password}"')
        __setup = True

@db_session(sql_debug=True, show_values=True)
def show_database():
    """
    Display entire contents of database
    """
    for table in [User, Game, BingoTicket, Track, Directory, Song]:
        table.select().show()


@db_session
def dump_database(filename: Path) -> None:
    """
    Output entire contents of database as JSON
    """
    with filename.open('w') as output:
        output.write('{\n')
        for table in [User, Game, BingoTicket, Track, Directory, Song]:
            print(table.__name__)
            contents = []
            for item in table.select():
                data = item.to_dict(with_collections=True)
                contents.append(flatten(data))
            output.write(f'"{table.__name__}s":')
            json.dump(contents, output, indent='  ')
            comma = ','
            if table != Song:
                output.write(',')
            output.write('\n')
        output.write('}\n')

@db_session
def import_database(filename: Path) -> None:
    """
    Import JSON file into database
    """
    with filename.open('r') as input:
        data = json.load(input)

    pk_maps: typing.Dict[typing.Type[db.Entity], Dict[int, int]] = {}
    for table in [User, Directory, Song, Game, Track, BingoTicket ]:
        print(table.__name__)
        if table.__name__ in data:
            pk_maps[table] = table.import_json(data[table.__name__], pk_maps)
        elif f'{table.__name__}s' in data:
            pk_maps[table] = table.import_json(data[f'{table.__name__}s'], pk_maps)
        commit()

