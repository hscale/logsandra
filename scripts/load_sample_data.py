#!/usr/bin/env python
import sys
import os

sys.path.append(os.path.join(os.path.dirname('__file__'), '..', 'src'))

from random import randint
from datetime import datetime, timedelta

from logsandra.model.client import CassandraClient

client = CassandraClient('test', 'localhost', 9160, 3)

keywords = ['foo', 'bar', 'baz']
print "Loading sample data for the following keywords:", ', '.join(keywords)

today = datetime.now()
for i in range(1000):
    d = today + timedelta(randint(-7, -1), randint(-3600*24, 3600*24))
    client.add_log(d, 'test entry', 'here', [keywords[i % len(keywords)]])
