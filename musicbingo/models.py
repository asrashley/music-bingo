"""
This file contains all of the database models.

"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
from typing import List

from flask_login import UserMixin
from passlib.context import CryptContext
from pony.orm import Database, PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import perm, composite_key, db_session, select  # type: ignore
from pony.orm import user_groups_getter, commit, exists, show # type: ignore

from .utils import flatten

db = Database()

password_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
)

class Group(db.Entity):
    pk = PrimaryKey(int, auto=True)
    name = Required(str, 32, unique=True)
    users = Set('User')

class User(db.Entity, UserMixin):
    __SALT_LENGTH=5

    pk = PrimaryKey(int, auto=True)
    username = Required(str, 32, unique=True)
    password = Required(str, hidden=True)
    email = Optional(str, unique=True)
    last_login = Optional(datetime)
    bingo_tickets = Set('BingoTicket')
    groups = Set(Group)

    def get_id(self):
        """
        This method must return a unicode that uniquely identifies this user.
        """
        return self.username

    def set_password(self, password: str) -> None:
        """
        Set the password of this user.
        The password is converted using a one-way hash to make it hard to reverse
        """
        self.password = self.hash_password(password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return password_context.hash(password)

    def check_password(self, password: str) -> bool:
        """
        Check the given password is correct
        """
        try:
            if not password_context.verify(password, self.password):
                return False
        except ValueError:
            if self.password == password:
                # upgrade the non-hashed plaintext password
                self.set_password(password)
                return True
            return False
        if password_context.needs_update(self.password):
            # password is valid but using a deprecated hash
            self.set_password(password)
        return True

    @property
    def is_admin(self) -> bool:
        """
        Is this user an admin?
        """
        admin = Group.get(name='admin')
        return admin in self.groups

@user_groups_getter(User)
def get_groups(user: User) -> List[str]:
    """
    get the list of groups assigned to this user
    """
    return [g.name for g in user.groups]

class BingoTicket(db.Entity):
    pk = PrimaryKey(int, auto=True)
    user = Optional(User)
    game = Required('Game')
    number = Required(int, unsigned=True)
    tracks = Set('Track')
    fingerprint = Required(str)  # calculated by multiplying the primes of each track on this ticket
    composite_key(game, number)


class Game(db.Entity):
    pk = PrimaryKey(int, auto=True)
    bingo_tickets = Set(BingoTicket)
    id = Required(str, 64, unique=True)
    title = Required(str)
    start = Required(datetime, unique=True)
    end = Required(datetime)
    tracks = Set('Track')


class Directory(db.Entity):
    pk = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    songs = Set('Song')
    title = Required(str)
    artist = Optional(str)
    directories = Set('Directory', reverse='directory')
    directory = Optional('Directory', reverse='directories')


class SongBase(db.Entity):
    pk = PrimaryKey(int, auto=True)
    filename = Required(str)  # relative to directory
    title = Required(str)
    artist = Optional(str)
    duration = Required(int, default=0, unsigned=True)
    channels = Required(int, unsigned=True)
    sample_rate = Required(int, unsigned=True)
    sample_width = Required(int, unsigned=True)
    bitrate = Required(int, unsigned=True)
    album = Optional(str)


class Song(SongBase):
    directory = Required(Directory)
    composite_key(directory, SongBase.filename)


class Track(SongBase):
    prime = Required(str)
    bingo_tickets = Set(BingoTicket)
    start_time = Required(timedelta)
    game = Required(Game)
    composite_key(prime, game)


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
        db.bind(**bind_args)
        db.generate_mapping(create_tables=True)
        with db_session:
            admin = Group.get(name="admin")
            if admin is None:
                admin = Group(name="admin")
                commit()
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
        for table in [Group, User, Game, BingoTicket, Track, Directory, Song]:
            print(table.__name__)
            contents = []
            for item in table.select():
                data = item.to_dict(with_collections=True)
                contents.append(flatten(data))
            output.write(f'"{table.__name__}":')
            json.dump(contents, output, indent='  ')
            comma = ','
            if table != Song:
                output.write(',')
            output.write('\n')
        output.write('}\n')


def main():
    #pylint: disable=import-outside-toplevel
    from musicbingo.options import Options
    import sys

    opts = Options.parse(sys.argv[1:])
    settings = opts.database_settings()
    bind(**settings)
    filename = Path(settings['filename']).with_suffix('.json')
    print(filename)
    dump_database(filename)

if __name__ == "__main__":
    main()
