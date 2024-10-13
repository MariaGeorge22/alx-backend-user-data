#!/usr/bin/env python3
""" Session Authentication Expiry Management Class """

from datetime import datetime, timedelta
from os import getenv
import uuid
from api.v1.auth.session_auth import SessionAuth
from models.user import User


class SessionExpAuth(SessionAuth):
    """ Session Exp Auth Class """

    def __init__(self):
        """ initialization Method """
        super().__init__()
        try:
            self.session_duration = int(getenv("SESSION_DURATION"))
        except Exception:
            self.session_duration = 0

    def create_session(self, user_id=None):
        """ create expiry session """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None

        self.user_id_by_session_id[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now()
        }

        return session_id

    def user_id_for_session_id(self, session_id=None):
        """ Overload """

        if session_id is None:
            return None

        user = self.user_id_by_session_id.get(session_id)
        if user is None:
            return None

        user_id = user.get("user_id")
        if self.session_duration <= 0:
            return user_id

        created_at = user.get("created_at")
        if created_at is None:
            return None

        session_end = created_at + timedelta(seconds=self.session_duration)
        if session_end < datetime.now():
            return None

        return user_id
