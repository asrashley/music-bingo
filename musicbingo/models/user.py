"""
Database model for a user of the app
"""
from typing import AbstractSet, List, Optional, Union

from passlib.context import CryptContext  # type: ignore
from sqlalchemy import (  # type: ignore
    Column, DateTime, String, Integer,
)
from sqlalchemy.orm import relationship  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject
from musicbingo.models.group import Group

password_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
)


class User(Base, ModelMixin):  # type: ignore
    """
    Database model for a user of the app
    """
    __tablename__ = 'User'
    __plural__ = 'Users'
    __schema_version__ = 4

    __SALT_LENGTH = 5
    __RESET_TOKEN_LENGTH = 16

    pk = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String, nullable=False)
    # See http://tools.ietf.org/html/rfc5321#section-4.5.3 for email length limit
    email = Column(String(256), unique=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    groups_mask = Column(Integer, nullable=False, default=Group.users.value)
    # since v4
    reset_expires = Column(DateTime, nullable=True)
    # since v3
    reset_token = Column(String(__RESET_TOKEN_LENGTH * 2), nullable=True)
    bingo_tickets = relationship('BingoTicket', back_populates="user", lazy='dynamic')
    tokens = relationship("Token", back_populates="user", lazy='dynamic')

    @classmethod
    def migrate_schema(cls, engine, existing_columns, column_types,
                       version) -> List[str]:
        """
        Migrate database Schema
        """
        cmds = []
        if version < 4:
            for name in ['reset_expires', 'reset_token']:
                if name not in existing_columns:
                    cmds.append(cls.add_column(engine, column_types, name))
        return cmds

    def to_dict(self, exclude: Optional[AbstractSet[str]] = None,
                only: Optional[AbstractSet[str]] = None,
                with_collections: bool = False) -> JsonObject:
        """
        Convert this model into a dictionary
        :exclude: set of attributes to exclude
        :only: set of attributes to include
        """
        if exclude is None:
            exclude = set({'tokens'})
        return super(User, self).to_dict(exclude=exclude,
                                         only=only, with_collections=with_collections)

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
        """
        Perform one-way hash of supplied plain text password
        """
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

    def get_groups(self) -> List[Group]:
        """
        get the list of groups assigned to this user
        """
        groups: List[Group] = []
        for group in list(Group):
            if self.groups_mask & group.value:
                groups.append(group)
        return groups

    def set_groups(self, groups: List[Union[Group, str]]) -> None:
        """
        set list of groups for this user
        """
        value = 0
        for group in groups:
            if isinstance(group, str):
                group = Group[group]
            value += group.value
        self.groups_mask = value

    groups = property(get_groups, set_groups)
