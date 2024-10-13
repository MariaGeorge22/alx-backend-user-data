#!/usr/bin/env python3
"""Second Task"""

import bcrypt


def hash_password(password: str) -> bytes:
    """function that takes a password string
    and returns a hashed password string"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """function that expects 2 arguments and returns a boolean"""
    return bcrypt.checkpw(password.encode(), hashed_password)
