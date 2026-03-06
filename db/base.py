# db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all ORM models.

    Any class that inherits from Base
    will be registered in SQLAlchemy metadata.
    """
    pass