#!/usr/bin/env python3
""" Basic Authentication Management Class """

import base64
import binascii
from typing import Tuple, TypeVar
from api.v1.auth.auth import Auth
import models.user

User = TypeVar('User')


class BasicAuth(Auth):
    """ Basic Auth Class """

    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """ returns the Base64 part of the Authorization header
        for a Basic Authentication """
        if not (authorization_header
                and isinstance(authorization_header, str)
                and authorization_header.startswith("Basic ")):
            return None
        return authorization_header[6:]

    def decode_base64_authorization_header(
            self, base64_authorization_header: str) -> str:
        """  returns the decoded value of
        a Base64 string base64_authorization_header """
        if not (base64_authorization_header
                and isinstance(base64_authorization_header, str)):
            return None

        try:
            return base64.b64decode(base64_authorization_header).decode()
        except (UnicodeDecodeError, binascii.Error):
            return None

    def extract_user_credentials(
            self, decoded_base64_authorization_header: str) -> Tuple[str, str]:
        """ returns the user email and password
        from the Base64 decoded value """
        if not (decoded_base64_authorization_header
                and isinstance(decoded_base64_authorization_header, str)
                and decoded_base64_authorization_header.find(":") != -1):
            return (None, None)

        user, password = decoded_base64_authorization_header.split(":", 1)
        return (user, password)

    def user_object_from_credentials(self,
                                     user_email: str, user_pwd: str) -> User:
        """ returns the User instance based on his email and password """

        if not ((
            user_email and isinstance(user_email, str)
        ) and (
            user_pwd and isinstance(user_pwd, str)
        )):
            return None
        try:
            users = models.user.User.search({
                "email": user_email,
            })
            if not users:
                return None

            for current_user in users:
                if current_user.is_valid_password(user_pwd):
                    return current_user

            return None
        except Exception:
            return None

    def current_user(self, request=None) -> User:
        """ overloads Auth and retrieves the User instance for a request """
        header = self.authorization_header(request)
        extracted_header = self.extract_base64_authorization_header(header)
        decoded_header = self.decode_base64_authorization_header(
            extracted_header)
        credentials = self.extract_user_credentials(decoded_header)
        return self.user_object_from_credentials(*credentials)
    # def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
    #     """ returns False """
    #     if path and path[-1] != "/":
    #         path += "/"

    #     return path is None \
    #         or not excluded_paths \
    #         or not (path in excluded_paths)

    # def authorization_header(self, request=None) -> str:
    #     """ returns None """
    #     HEADER = 'Authorization'
    #     if not request:
    #         return None
    #     return request.headers.get(HEADER)

    # def current_user(self, request=None) -> User:
    #     """ returns None """
    #     return None
