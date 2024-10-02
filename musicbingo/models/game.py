"""
Database model for a Bingo Game
"""

import datetime
from typing import List, Optional, cast, TYPE_CHECKING

from sqlalchemy.types import DateTime, String, Integer
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.expression import TextClause
import sqlalchemy_jsonfield  # type: ignore

from musicbingo.options import Options
from musicbingo.utils import flatten

from .base import Base
from .modelmixin import ModelMixin, JsonObject
from .schemaversion import SchemaVersion
from .session import DatabaseSession

if TYPE_CHECKING:
    from .bingoticket import BingoTicket
    from .track import Track

class Game(Base, ModelMixin):  # type: ignore
    """
    Database model for a Bingo Game
    """

    __plural__ = 'Games'
    __tablename__ = 'Game'
    __schema_version__ = 3

    pk: Mapped[int] = mapped_column(Integer, primary_key=True)
    id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    start: Mapped[datetime.datetime] = mapped_column(DateTime, unique=True, nullable=False)
    end: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    bingo_tickets: Mapped[list["BingoTicket"]] = relationship(
        "BingoTicket", backref="game", lazy='dynamic', cascade="all,delete")
    tracks: Mapped[list["Track"]] = relationship("Track", backref="game", order_by="Track.number",
                          cascade="all, delete, delete-orphan", lazy='dynamic')
    # since 3
    options: Mapped[JsonObject | None] = mapped_column('options',
                     sqlalchemy_jsonfield.JSONField(
                         # MariaDB does not support JSON for now
                         enforce_string=True,
                         # MariaDB connector requires additional parameters for correct UTF-8
                         enforce_unicode=False
                     ),
                     nullable=True)

    # pylint: disable=arguments-differ
    @classmethod
    def migrate_schema(cls, engine: Engine, sver: SchemaVersion) -> List[TextClause]:
        """
        Migrate model to latest Schema
        :version: current detected version
        """
        version, existing_columns, column_types = sver.get_table(cls.__tablename__)
        cmds: List[TextClause] = []
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
        opts = options.to_dict(only={'colour_scheme', 'columns', 'rows', 'sort_order',
                                     'number_of_cards', 'include_artist',
                                     'checkbox', 'page_size', 'cards_per_page'})
        if self.options:
            opts.update(self.options)
        return flatten(opts)
