#!/usr/bin/env python3
"""First Task"""


from os import environ
import re
from typing import List
import logging
from mysql.connector import connect, connection

PII_FIELDS = ('name', 'email',
              'phone',
              'ssn', 'password')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """function that returns the log message obfuscated"""
    for field in fields:
        # must be non greedy, to stop at first separator
        regex = r"{}=.*?{}".format(field, separator)
        message = re.sub(regex,
                         f"{field}={redaction}{separator}",
                         message)
    return message


def get_logger() -> logging.Logger:
    """function that returns a logging object"""
    name = "user_data"
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = RedactingFormatter(fields=PII_FIELDS)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # print(logger)
    return logger


def get_db() -> connection.MySQLConnection:
    """function that returns a database connection object"""
    user = environ.get('PERSONAL_DATA_DB_USERNAME', 'root')
    password = environ.get('PERSONAL_DATA_DB_PASSWORD', '')
    host = environ.get('PERSONAL_DATA_DB_HOST', 'localhost')
    db = environ.get('PERSONAL_DATA_DB_NAME')
    db_connection = connect(
        user=user,
        password=password,
        host=host,
        database=db
    )
    return db_connection


def main():
    """obtain a database connection using get_db
    and retrieve all rows in the users table
    and display each row under a filtered format like this"""
    attribs = [
        'name', 'email', 'phone',
        'ssn', 'password', 'ip',
        'last_login', 'user_agent'
    ]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    logger = get_logger()
    for row in cursor:
        msg = "; ".join([f"{attrib}={str(row[i])}"
                         for i, attrib in enumerate(attribs)])
        msg += ";"
        logger.info(msg)
    cursor.close()
    db.close()


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """constructor"""
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """filter values in incoming log records using filter_datum"""
        redacted = filter_datum(self.fields, "***", record.getMessage(), ";")
        record.message = redacted
        record.asctime = self.formatTime(record, self.datefmt)
        return self.formatMessage(record)
        # NotImplementedError


if __name__ == "__main__":
    """Main Executable"""
    main()
