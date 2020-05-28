"""
Database model for a user of the app
"""
from sqlalchemy import (  # type: ignore
    Column, String, Integer,
)

from .base import Base
from .modelmixin import ModelMixin

class SchemaVersion(Base, ModelMixin):
    __tablename__ = 'SchemaVersion'
    __plural__ = 'SchemaVersions'

    table = Column(String(32), primary_key=True, nullable=False)
    version = Column(Integer, nullable=False)
