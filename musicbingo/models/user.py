from datetime import datetime, timedelta
import typing

from flask_login import UserMixin  # type: ignore
from passlib.context import CryptContext  # type: ignore
from sqlalchemy import (  # type: ignore
    Column, DateTime, String, Integer,  # type: ignore
    ForeignKey, func, inspect)  # type: ignore
from sqlalchemy.orm import relationship, backref  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.importsession import ImportSession
from musicbingo.models.modelmixin import ModelMixin
from musicbingo.models.group import Group
from musicbingo.utils import flatten, from_isodatetime, parse_date, make_naive_utc

password_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
)


def max_with_none(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b)


class User(Base, ModelMixin, UserMixin):  # type: ignore
    __tablename__ = 'User'
    __plural__ = 'Users'
    __schema_version__ = 3

    __SALT_LENGTH = 5
    __RESET_TOKEN_LENGTH = 16

    pk = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    groups_mask = Column(Integer, nullable=False, default=Group.users.value)
    bingo_tickets = relationship('BingoTicket')
    # since v3
    reset_date = Column(DateTime, nullable=True)
    # since v3
    reset_token = Column(String(__RESET_TOKEN_LENGTH * 2), nullable=True)

    @classmethod
    def migrate(cls, engine, columns, version) -> typing.List[str]:
        print(f'User.migrate({version})')
        insp = inspect(engine)
        existing_columns = [col['name'] for col in insp.get_columns(cls.__tablename__)]
        cmds = []
        if version < 3:
            for name in ['reset_date', 'reset_token']:
                if name not in existing_columns:
                    cmds.append(cls.add_column(engine, columns, name))
        return cmds

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

    def is_member_of(self, group: Group):
        """
        Check if the user is a member of the specified group
        """
        return (self.groups_mask & group.value) == group.value

    def has_permission(self, group: Group):
        """
        Check if the user has the permission associated with a group
        """
        return ((self.groups_mask & group.value) == group.value or
                self.is_admin)

    def get_groups(self) -> typing.List[Group]:
        """
        get the list of groups assigned to this user
        """
        groups: typing.List[Group] = []
        for group in list(Group):
            if self.groups_mask & group.value:
                groups.append(group)
        return groups

    def set_groups(self, groups: typing.List[typing.Union[Group, str]]):
        value = 0
        for group in groups:
            if isinstance(group, str):
                group = Group[group]
            value += group.value
        self.groups_mask = value

    groups = property(get_groups, set_groups)

    def generate_reset_token(self):
        self.reset_date = datetime.datetime.now()
        self.reset_token = secrets.token_urlsafe(self.__RESET_TOKEN_LENGTH)

    @classmethod
    def import_json(cls, imp: ImportSession, data: typing.List) -> None:
        pk_map: typing.Dict[int, int] = {}
        imp.set_map("User", pk_map)
        for item in data:
            if item['last_login']:
                item['last_login'] = parse_date(item['last_login'])
                assert isinstance(item['last_login'], datetime)
                # Pony doesn't work correctly with timezone aware datetime
                # see: https://github.com/ponyorm/pony/issues/434
                item['last_login'] = make_naive_utc(item['last_login'])
            user = typing.cast(
                typing.Optional[User], User.get(
                    imp.session, username=item['username']))
            user_pk: typing.Optional[int] = None
            try:
                user_pk = item['pk']
                del item['pk']
            except KeyError:
                pass
            remove = ['bingo_tickets', 'groups']
            # if user is None and user_pk and User.does_exist(imp.session, pk=user_pk):
            if user is None and user_pk and User.get(imp.session, pk=user_pk) is not None:
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
                imp.add(user)
            else:
                user.password = item['password']
                user.email = item['email']
                user.groups_mask = item['groups_mask']
                if isinstance(user.last_login, str):
                    user.last_login = parse_date(user.last_login)
                user.last_login = max_with_none(user.last_login, item['last_login'])
            imp.commit()
            if user_pk:
                pk_map[user_pk] = user.pk
