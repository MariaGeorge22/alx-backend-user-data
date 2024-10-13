#!/usr/bin/env python3
""" Authentication Management Class """

from os import getenv
import re
from typing import List, TypeVar

User = TypeVar('User')


class Auth:
    """ Auth Class """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """ returns False """
        if path and path[-1] != "/":
            path += "/"

        return path is None \
            or not excluded_paths \
            or not any(map(lambda p:
                           (p[-1] == "*" and
                            re.match("^" + re.escape(p[:-1]), path))
                           or p == path, excluded_paths))

    def authorization_header(self, request=None) -> str:
        """ returns None """
        HEADER = 'Authorization'
        if not request:
            return None
        return request.headers.get(HEADER)

    def current_user(self, request=None) -> User:
        """ returns None """
        return None

    def session_cookie(self, request=None):
        """ returns a cookie value from a request """
        if request is None:
            return None
        session_name = getenv("SESSION_NAME")
        return request.cookies.get(session_name)
