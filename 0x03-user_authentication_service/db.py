#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.session = DBSession()
        return self.session

    def add_user(self, email: str, hashed_password: str) -> User:
        """add a new user to the db"""
        new_user = User(email=email, hashed_password=hashed_password)
        session = self._session
        session.add(new_user)
        session.commit()
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """ returns the first row found in the users table
        as filtered by the method’s input arguments """

        try:
            result = self._session.query(User).filter_by(**kwargs).first()
        except InvalidRequestError:
            raise

        if result is None:
            raise NoResultFound

        return result

    def update_user(self, user_id: int, **kwargs) -> None:
        """ update the user’s attributes
        as passed in the method’s arguments """
        if not user_id:
            raise InvalidRequestError

        user = self.find_user_by(id=user_id)
        if not user:
            raise NoResultFound

        for key, value in kwargs.items():
            if not hasattr(user, key):
                raise ValueError
            setattr(user, key, value)

        self._session.commit()
