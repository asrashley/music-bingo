from datetime import datetime
from enum import IntEnum
import typing

from sqlalchemy import (  # type: ignore
    Boolean, Column, DateTime, String, Integer,  # type: ignore
    ForeignKey, func, inspect)  # type: ignore
from sqlalchemy.orm import relationship, backref  # type: ignore
from sqlalchemy.orm.exc import NoResultFound # type: ignore
# from flask_jwt_extended import decode_token  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.user import User
from musicbingo.models.modelmixin import ModelMixin

class TokenType(IntEnum):
    access = 1
    refresh = 2

class Token(Base, ModelMixin):
    __tablename__ = 'Token'
    __plural__ = 'Tokens'
    __schema_version__ = 1

    pk = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False)
    token_type = Column(Integer, nullable=False)
    username = Column(String(32), nullable=False)
    user_pk = Column("user_pk", Integer, ForeignKey('User.pk'), nullable=True)
    user = relationship("User", backref="tokens")
    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires = Column(DateTime, nullable=True)
    revoked = Column(Boolean, nullable=False)

    @classmethod
    def migrate(cls, engine, mapper, version) -> typing.List[str]:
        return []

    @classmethod
    def add(cls, decoded_token, identity_claim, revoked, session):
        """
        Adds a new token to the database.
        """
        jti = decoded_token['jti']
        token_type = TokenType[decoded_token['type']]
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
    def is_revoked(cls, decoded_token, session):
        jti = decoded_token['jti']
        token_type = decoded_token['type']
        try:
            token = session.query(cls).filter_by(jti=jti).one()
            return token.revoked
        except NoResultFound:
            return token_type != 'access'

    @classmethod
    def prune_database(cls, session):
        """
        Delete tokens that have expired from the database.
        """
        now = datetime.now()
        expired = session.query(cls).filter(cls.expires < now).all()
        for token in expired:
            session.delete(token)
        session.commit()
