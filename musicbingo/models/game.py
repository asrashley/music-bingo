"""
Database model for a Bingo Game
"""

from typing import List, Optional, cast

from sqlalchemy import Column  # type: ignore
from sqlalchemy.types import DateTime, String, Integer  # type: ignore
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
import sqlalchemy_jsonfield  # type: ignore

from musicbingo.options import Options
from musicbingo.palette import Palette

from .base import Base
from .modelmixin import ModelMixin, JsonObject
from .schemaversion import SchemaVersion
from .session import DatabaseSession

class Game(Base, ModelMixin):  # type: ignore
    """
    Database model for a Bingo Game
    """

    __plural__ = 'Games'
    __tablename__ = 'Game'
    __schema_version__ = 3

    pk = Column(Integer, primary_key=True)
    bingo_tickets = relationship("BingoTicket", backref="game",
                                 lazy='dynamic', cascade="all,delete")
    id = Column(String(64), unique=True, nullable=False)
    title = Column(String(256), nullable=False)
    start = Column(DateTime, unique=True, nullable=False)
    end = Column(DateTime, nullable=False)
    tracks = relationship("Track", backref="game", order_by="Track.number",
                          cascade="all, delete, delete-orphan", lazy='dynamic')
    # since 3
    options = Column('options',
                     sqlalchemy_jsonfield.JSONField(
                         # MariaDB does not support JSON for now
                         enforce_string=True,
                         # MariaDB connector requires additional parameters for correct UTF-8
                         enforce_unicode=False
                     ),
                     nullable=True)

    # pylint: disable=arguments-differ
    @classmethod
    def migrate_schema(cls, engine: Engine, sver: SchemaVersion) -> List[str]:
        """
        Migrate model to latest Schema
        :version: current detected version
        """
        version, existing_columns, column_types = sver.get_table(cls.__tablename__)
        cmds: List[str] = []
        if version < 3 and 'options' not in existing_columns:
            cmds.append(cls.add_column(engine, column_types, 'options'))
        return cmds

    @classmethod
    def lookup(cls, session: DatabaseSession, item: JsonObject) -> Optional["Game"]:
        """
        Search for a game in the database.
        Returns Game or None if not found.
        """
        game = Game.get(session, id=item['id'])
        return cast(Optional["Game"], game)

    def game_options(self, options: Options) -> JsonObject:
        """
        Get the options used for this game
        """
        opts = options.to_dict(only={'colour_scheme', 'columns', 'rows',
                                     'number_of_cards', 'include_artist'})
        if self.options:
            opts.update(self.options)
        opts['palette'] = Palette[opts['colour_scheme'].upper()]
        return opts
