#!/usr/bin/env python3
""" Auth module """

import uuid
import bcrypt
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from db import DB, User


def _hash_password(password: str) -> str:
    """ Returns a hashed password """

    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def _generate_uuid() -> str:
    """ Returns a string representation of a new UUID """

    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """ Registers a new user and saves it to the database.
        """
        if not (email and password):
            raise InvalidRequestError

        try:
            already_exists = self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            return self._db.add_user(email, _hash_password(password))

    def valid_login(self, email: str, password: str) -> bool:
        """ Try locating the user by email.
        If it exists, check the password with bcrypt.checkpw.
        If it matches return True. In any other case, return False """

        try:
            user = self._db.find_user_by(email=email)
            return bcrypt.checkpw(password.encode('utf-8'),
                                  user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """  takes an email string argument
        and returns the session ID as a string """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            user.session_id = session_id
            self._db.session.commit()
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> User:
        """ If the session ID is None or no user is found, return None.
        Otherwise return the corresponding user. """
        if session_id is None:
            return None

        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

        return user

    def destroy_session(self, user_id: int):
        """  updates the corresponding user’s session ID to None. """
        if user_id is None:
            raise InvalidRequestError

        try:
            self._db.update_user(user_id, session_id=None)
        except NoResultFound:
            raise

    def get_reset_password_token(self, email: str) -> str:
        """ Find the user corresponding to the email.
        If the user does not exist, raise a ValueError exception.
        If it exists, generate a UUID
        and update the user’s reset_token database field.
        Return the token. """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError

        reset_token = _generate_uuid()
        user.reset_token = reset_token
        self._db.session.commit()

        return reset_token

    def update_password(self, reset_token: str, password: str):
        """ Use the reset_token to find the corresponding user.
        If it does not exist, raise a ValueError exception.
        Otherwise, hash the password
        and update the user’s hashed_password field
        with the new hashed password
        and the reset_token field to None. """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        new_hashed_password = _hash_password(password)

        self._db.update_user(user.id,
                             hashed_password=new_hashed_password,
                             reset_token=None)
