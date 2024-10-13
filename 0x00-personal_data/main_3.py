#!/usr/bin/env python3
"""
Main file
"""

import logging
import csv

get_logger = __import__('filtered_logger').get_logger
PII_FIELDS = __import__('filtered_logger').PII_FIELDS

print(get_logger.__annotations__.get('return'))
print("PII_FIELDS: {}".format(len(PII_FIELDS)))

logger = get_logger()
with open("user_data.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # print(row)
        msg = ""
        for k in row:
            msg += k + "=" + row[k] + ";"
        logger.info(msg=msg)
