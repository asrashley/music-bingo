from datetime import datetime, timedelta
import enum
import typing

from flask_login import UserMixin
from passlib.context import CryptContext
from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import perm, composite_key, db_session, select  # type: ignore
from pony.orm import user_groups_getter, flush # type: ignore

from musicbingo.models.db import db
from musicbingo.utils import flatten, from_isodatetime, parse_date, make_naive_utc

class Group(enum.IntFlag):
    users =   0x00000001
    creator = 0x00000002
    host =    0x00000004
    admin =   0x40000000

password_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
)


def max_with_none(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return max(a,b)

class User(db.Entity, UserMixin): # type: ignore
    __plural__ = 'Users'

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
                    options,
                    pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> None:
        pk_map: Dict[int, int] = {}
        pk_maps[User] = pk_map
        for item in users:
            item['last_login'] = parse_date(item['last_login'])
            assert isinstance(item['last_login'], datetime)
            # Pony doesn't work correctly with timezone aware datetime
            # see: https://github.com/ponyorm/pony/issues/434
            item['last_login'] = make_naive_utc(item['last_login'])
            user = User.get(username=item['username'])
            user_pk: typing.Optional[int] = item.get('pk', None)
            remove = ['bingo_tickets', 'groups']
            if user is None and user_pk and User.exists(pk=user_pk):
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
                if isinstance(user.last_login, str):
                    user.last_login = parse_date(user.last_login)
                user.last_login = max_with_none(user.last_login, item['last_login'])
            flush()
            if user_pk:
                pk_map[user_pk] = user.pk

@user_groups_getter(User)
def get_groups(user: User) -> typing.List[str]:
    """
    get the list of groups assigned to this user
    """
    return [g.name for g in user.groups]
