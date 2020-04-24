"""
This file contains all of the database models.

"""
import copy
from datetime import datetime, timedelta
import enum
import json
from pathlib import Path
from random import shuffle
import secrets
import threading
import typing

from flask_login import UserMixin
from passlib.context import CryptContext
from pony.orm import Database, PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import perm, composite_key, db_session, select  # type: ignore
from pony.orm import user_groups_getter, commit, exists, show # type: ignore
from pony.orm import Json, flush # type: ignore

from .utils import flatten, from_isodatetime
from .primes import PRIME_NUMBERS

db = Database()

password_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
)

class Group(enum.IntFlag):
    users =   0x00000001
    creator = 0x00000002
    host =    0x00000004
    admin =   0x40000000


class User(db.Entity, UserMixin): # type: ignore
    __SALT_LENGTH=5

    pk = PrimaryKey(int, auto=True)
    username = Required(str, 32, unique=True)
    password = Required(str, hidden=True)
    email = Optional(str, unique=True)
    last_login = Optional(datetime)
    bingo_tickets = Set('BingoTicket')
    groups_mask = Required(int, size=32)

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
        return (self.groups_mask & Group.admin.value) == Group.admin.value

    def get_groups(self) -> typing.List[Group]:
        """
        get the list of groups assigned to this user
        """
        groups: List[Group] = []
        for group in list(Group):
            if self.groups_mask & group.value:
                groups.append(group)
        return groups

    def set_groups(self, groups: typing.List[Group]):
        value = 0
        for group in groups:
            value += group.value
        self.groups_mask = value

    groups = property(get_groups, set_groups)

    @classmethod
    def import_json(cls, users,
                    pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> typing.Dict[int, int]:
        pk_map: Dict[int, int] = {}
        for item in users:
            item['last_login'] = from_isodatetime(item['last_login'])
            user = User.get(username=item['username'])
            user_pk: typing.Optional[int] = item.get('pk', None)
            remove = ['bingo_tickets', 'groups']
            if user is None and user_pk and User.get(pk=user_pk) is not None:
                remove.append('pk')
            for field in remove:
                try:
                    del item[field]
                except KeyError:
                    pass
            if not 'groups_mask' in item:
                item['groups_mask'] = Group.users.value
            if user is None:
                user = User(**item)
            else:
                user.password = item['password']
                user.email = item['email']
                user.groups_mask = item['groups_mask']
            flush()
            if user_pk:
                pk_map[user_pk] = user.pk
        return pk_map

@user_groups_getter(User)
def get_groups(user: User) -> typing.List[str]:
    """
    get the list of groups assigned to this user
    """
    return [g.name for g in user.groups]

class BingoTicket(db.Entity): # type: ignore
    pk = PrimaryKey(int, auto=True)
    user = Optional(User)
    game = Required('Game')
    number = Required(int, unsigned=True)
    tracks = Set('Track')
    fingerprint = Required(str)  # calculated by multiplying the primes of each track on this ticket
    order = Optional(Json) # List[int] - order of tracks by pk
    checked = Optional(int, size=64, default=0) # bitmask of track order
    composite_key(game, number)

    def tracks_in_order(self) -> typing.List["Track"]:
        """
        Get the list of tracks, in the order they appear on the ticket
        """
        #if not self.order:
        #    self.order = list(select(track.pk for track in self.tracks).random(len(self.tracks)))
        tk_map = {}
        for trck in self.tracks:
            tk_map[trck.pk] = trck
            if self.order and trck.pk not in self.order:
                self.order.append(trck.pk)
        if not self.order:
            order = list(tk_map.keys())
            shuffle(order)
            self.order = order
        elif None in self.order:
            # work-around for bug that did not wait for Track.pk to be
            # calculated when generating order
            self.order = list(filter(lambda item: item is not None, self.order))
        tracks: typing.List[Track] = []
        for tpk in self.order:
            if tpk in tk_map:
                tracks.append(tk_map[tpk])
        return tracks

    @classmethod
    def import_json(cls, items, pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> typing.Dict[int, int]:
        pk_map: Dict[int, int] = {}
        for item in items:
            try:
                ticket = BingoTicket.get(pk=item['pk'])
            except KeyError:
                ticket = None
            game = Game.get(pk=item['game'])
            if not game:
                print('Warning: failed to find game {game} for ticket {pk}'.format(**item))
                continue
            user = None
            if item['user']:
                user = User.get(pk=item['user'])
                if not user:
                    print('Warning: failed to find user {user} for ticket {pk} in game {game}'.format(**item))
            tracks = []
            # The database field "order" has the list of Track primary keys.
            # The JSON representation of BingoTicket should have a property called
            # "tracks" which is an ordered list of Track.pk. If the JSON
            # file has an "order" property, it can be used as a fallback.
            if 'order' in item and 'tracks' not in item:
                item['tracks'] = item['order']
            for trk in item['tracks']:
                track = Track.get(pk=trk)
                if track is None and trk in pk_maps[Track]:
                    track = Track.get(pk=pk_maps[Track][trk])
                if not track:
                    print('Warning: failed to find track {trk} for ticket {pk} in game {game}'.format(trk=trk, **item))
                else:
                    tracks.append(track)
            item['game'] = game
            item['user'] = user
            item['tracks'] = tracks
            if 'order' not in item:
                item['order'] = [t.pk for t in item['tracks']]
            if ticket is None:
                ticket = BingoTicket(**item)
            else:
                for key, value in item.items():
                    if key not in ['pk']:
                        setattr(ticket, key, value)
            flush()
            pk_map[item['pk']] = ticket.pk
        return pk_map

class Game(db.Entity): # type: ignore
    pk = PrimaryKey(int, auto=True)
    bingo_tickets = Set(BingoTicket)
    id = Required(str, 64, unique=True)
    title = Required(str)
    start = Required(datetime, unique=True)
    end = Required(datetime)
    tracks = Set('Track')

    @classmethod
    def import_json(cls, items, pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> typing.Dict[int, int]:
        pk_map: Dict[int, int] = {}
        for item in items:
            game = cls.lookup(item, pk_maps)
            item['start'] = from_isodatetime(item['start'])
            item['end'] = from_isodatetime(item['end'])
            for field in ['bingo_tickets', 'tracks', 'options']:
                try:
                    del item[field]
                except KeyError:
                    pass
            if game is None:
                game = Game(**item)
            else:
                for key, value in item.items():
                    if key != 'pk':
                        setattr(game, key, value)
            flush()
            pk_map[item['pk']] = game.pk
        return pk_map

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Game"]:
        try:
            game = Game.get(pk=item['pk'])
        except KeyError:
            game = None
        if game is None:
            game = Game.get(id=item['id'])
        return game

class Directory(db.Entity): # type: ignore
    pk = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    songs = Set('Song')
    title = Required(str)
    artist = Optional(str)
    directories = Set('Directory', reverse='directory')
    directory = Optional('Directory', reverse='directories')

    @classmethod
    def import_json(cls, items, pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]])  -> typing.Dict[int, int]:
        pk_map: Dict[int, int] = {}
        for item in items:
            item = copy.copy(item)
            for field in ['directories', 'songs']:
                try:
                    del item[field]
                except KeyError:
                    pass
            directory = cls.lookup(item, pk_map)
            if item['directory']:
                item['directory'] = Directory.get(pk=item['directory'])
            if directory is None:
                directory = Directory(**item)
            else:
                for key, value in item.items():
                    if key not in ['pk', 'name']:
                        setattr(directory, key, value)
            flush()
            pk_map[item['pk']] = directory.pk
        for item in items:
            directory = cls.lookup(item, pk_map)
            if directory.directory is None and item['directory'] is not None:
                parent = Directory.get(pk=item['directory'])
                if parent is None and item['directory'] in pk_map:
                    parent = Directory.get(pk=pk_map[item['directory']])
                if parent is not None:
                    directory.directory = parent
                    flush()
        return pk_map

    @classmethod
    def lookup(cls, item, pk_map) -> typing.Optional["Directory"]:
        try:
            rv = Directory.get(pk=item['pk'])
            if rv is None and item['pk'] in pk_map:
                rv = Directory.get(pk=pk_map[item['pk']])
        except KeyError:
            rv = None
        if rv is None:
            rv = Directory.get(name=item['name'])
        return rv

class SongBase(db.Entity): # type: ignore
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

    @classmethod
    def import_json(cls, items, pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> typing.Dict[int, int]:
        pk_map: typing.Dict[int, int] = {}
        for item in items:
            song = cls.lookup(item, pk_maps)
            for key in list(item.keys()):
                value = item[key]
                if isinstance(value, (list, dict)) or key == 'classtype':
                    del item[key]
            cls.from_json(item, pk_maps)
            if song is None:
                song = cls(**item)
            else:
                for key, value in item.items():
                    if key != 'pk':
                        setattr(song, key, value)
            flush()
            if 'pk' in item:
                pk_map[item['pk']] = song.pk
        return pk_map

class Song(SongBase):
    directory = Required(Directory)
    composite_key(directory, SongBase.filename)

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Song"]:
        try:
            song = Song.get(pk=item['pk'])
        except KeyError:
            song = None
        return song

    @classmethod
    def from_json(cls, item, pk_maps):
        """
        converts any fields in item to Python objects
        """
        parent = Directory.get(pk=item['directory'])
        if parent is None and item['directory'] in pk_maps[Directory]:
            parent = Directory.get(pk=pk_maps[Directory][item['directory']])
        item['directory'] = parent


class Track(SongBase):
    number = Required(int, unsigned=True)
    bingo_tickets = Set(BingoTicket)
    start_time = Required(int, unsigned=True)
    game = Required(Game)
    composite_key(number, game)

    @classmethod
    def from_json(cls, item, pk_maps):
        """
        converts any fields in item to Python objects
        """
        if isinstance(item['start_time'], str):
            item['start_time'] = round(from_isodatetime(item['start_time']).total_seconds() * 1000)
        item['game'] = Game.get(pk=item['game'])
        if 'prime' in item:
            item['number'] = PRIME_NUMBERS.index(int(item['prime']))
            del item['prime']

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Track"]:
        try:
            track = Track.get(pk=item['pk'])
        except KeyError:
            track = None
        if track is not None:
            return track
        try:
            game = Game.get(pk=item['game'])
            if game is not None:
                if 'prime' in item:
                    item['number'] = PRIME_NUMBERS.index(int(item['prime']))
                    del item['prime']
                track = Track.get(number=item['number'], game=game)
        except KeyError:
            track = None
        return track

    @property
    def prime(self) -> int:
        return PRIME_NUMBERS[self.number]

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

def usage():
    print(f'Usage:\n    python -m musicbinfo.models [<options>] (dump|import) <filename>')

def main():
    #pylint: disable=import-outside-toplevel
    from musicbingo.options import Options
    import sys

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
