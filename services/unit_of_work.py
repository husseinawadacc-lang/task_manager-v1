"""
Unit Of Work Pattern
====================

Responsible for managing database transactions.

Responsibilities:

- create database session
- commit transaction
- rollback on error
- close session

Storage layer MUST NOT manage transactions.
"""

from db.session import SessionLocal

class UnitOfWork:
    """
    Transaction manager used by services.
    """

    def __init__(self):

        # session will be created later
        self.session = None

    def __enter__(self):

        # create database session
        self.session = SessionLocal()

        return self.session

    def __exit__(self, exc_type, exc, tb):

        if exc_type is None:
            # no error occurred → commit
            self.session.commit()

        else:
            # error occurred → rollback
            self.session.rollback()

        # always close session
        self.session.close()