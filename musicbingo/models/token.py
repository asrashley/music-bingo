"""
Database table for storing refresh tokens and expired access tokens
"""

from datetime import datetime
from enum import IntEnum
from typing import List

from sqlalchemy import (  # type: ignore
    Boolean, Column, DateTime, String, Integer,  # type: ignore
    ForeignKey, func)  # type: ignore
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy.orm.exc import NoResultFound  # type: ignore

from .base import Base
from .modelmixin import ModelMixin
from .schemaversion import SchemaVersion
from .session import DatabaseSession
from .user import User

class TokenType(IntEnum):
    """
    Enum used in Token.token_type column
    """
    ACCESS = 1
    REFRESH = 2
    GUEST = 3


class Token(Base, ModelMixin):
    """
    Database table for storing refresh tokens and expired access tokens
    """
    __tablename__ = 'Token'
    __plural__ = 'Tokens'
    __schema_version__ = 1

    pk = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False)
    token_type = Column(Integer, nullable=False)
    username = Column(String(32), nullable=False)
    user_pk = Column("user_pk", Integer, ForeignKey('User.pk'), nullable=True)
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires = Column(DateTime, nullable=True)
    revoked = Column(Boolean, nullable=False)
    user = relationship("User", back_populates="tokens")

    # pylint: disable=unused-argument, arguments-differ
    @classmethod
    def migrate_schema(cls, engine: Engine, sver: SchemaVersion) -> List[str]:
        """
        Migrate database Schema
        """
        return []

    @classmethod
    def add(cls, decoded_token, identity_claim: str, revoked: bool,
            session: DatabaseSession) -> None:
        """
        Adds a new token to the database.
        """
        jti = decoded_token['jti']
        token_type = TokenType[decoded_token['type'].upper()]
        user_identity = decoded_token[identity_claim]
        expires = datetime.fromtimestamp(decoded_token['exp'])

        user = session.query(User).filter_by(username=user_identity).one_or_none()
        db_token = Token(
            jti=jti,
            token_type=token_type.value,
            username=user_identity,
            user=user,
            expires=expires,
            revoked=revoked,
        )
        session.add(db_token)
        session.commit()

    @classmethod
    def is_revoked(cls, decoded_token, session: DatabaseSession) -> bool:
        """
        Has the specified token been revoked?
        """
        jti = decoded_token['jti']
        token_type = decoded_token['type']
        try:
            token = session.query(cls).filter_by(jti=jti).one()
            return token.revoked
        except NoResultFound:
            return token_type != 'access'

    @classmethod
    def prune_database(cls, session: DatabaseSession) -> None:
        """
        Delete tokens that have expired from the database.
        """
        now = datetime.now()
        expired = session.query(cls).filter(cls.expires < now).all()
        for token in expired:
            session.delete(token)
        session.commit()
