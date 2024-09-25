import functools

from flask import redirect, url_for, flash, Flask
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError

from src.database import Session


class Controllers:
    """
        **Controllers**
            registers controllers
    """

    def __init__(self, session_maker=Session):
        self.sessions = [session_maker() for _ in range(20)]

    def get_session(self) -> Session:
        if self.sessions:
            return self.sessions.pop()
        self.sessions = [Session() for _ in range(20)]
        return self.get_session()
