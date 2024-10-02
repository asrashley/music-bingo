"""
holder for sqlalchemy declaritive base
"""
from sqlalchemy.orm import DeclarativeBase, registry

mapper_registry = registry()
class Base(DeclarativeBase):
    """
    Base class for all database models
    """
