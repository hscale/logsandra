import random
import datetime
import time
import struct
import uuid
import json
import pycassa
from pycassa.util import convert_uuid_to_time
from pycassa.cassandra.ttypes import NotFoundException
from collections import defaultdict

__all__ = ['CassandraClient']

class CassandraClient(object):

    def __init__(self, ident, host, port, timeout):
        self.ident = ident
        self.pool = pycassa.ConnectionPool('logsandra', ['%s:%s' % (host, port)], timeout=int(timeout))
        self.by_keyword = pycassa.ColumnFamily(self.pool, 'keyword')

    def add_log(self, date, entry, source, keywords):
        date = date.replace(tzinfo=None)
        datestr = date.strftime('%Y-%m-%d %H:%M:%S')

        col_val = json.dumps({'date': datestr, 'entry': entry, 'source': source})
        for keyword in keywords:
            self.by_keyword.insert(keyword, {date: col_val})

    def get_date_count(self, keyword, end_date='', count=100):
        if end_date:
            end_date = end_date / 1000000
        try:
            result = self.by_keyword.get(keyword, column_start=end_date,
                                         column_count=count, column_reversed=True)
        except NotFoundException:
            return [], None

        hour_buckets = defaultdict(int)
        timestamp = None
        for u, value in result.items():
            timestamp = convert_uuid_to_time(u)
            date = datetime.datetime.fromtimestamp(timestamp)
            hours = datetime.datetime(date.year, date.month, date.day, date.hour, 0, 0)
            hour_buckets[hours] += 1

        counts = []
        for hour in sorted(hour_buckets.keys(), reverse=True):
            counts.append((str(hour), hour_buckets[hour]))
        return counts, int(timestamp * 1000000) - 1

    def get_by_keyword(self, keyword, column_start='', column_finish='', count=30, action_next=None, action_prev=None):
        if action_next and action_prev:
            raise AttributeError('action_next and action_prev is mutually exclusive')


        if column_start:
            column_reversed = False
        else:
            column_reversed = True

        if action_next:
            action_next = action_next / 1000000
            column_start = action_next
            column_reversed = False
        elif action_prev:
            action_prev = action_prev / 1000000
            if column_start:
                column_finish = column_start / 1000000
            column_start = action_prev
            column_reversed = True

        try:
            result = self.by_keyword.get(keyword,
                    column_reversed=column_reversed, column_count=count,
                    column_start=column_start, column_finish=column_finish)
        except NotFoundException:
            return [], None, None

        keys = map(lambda x: int(convert_uuid_to_time(x) * 1000000), result.keys())
        entries = map(json.loads, result.values())
        if column_reversed:
            keys.reverse()
            entries.reverse()

        if len(entries) == count:
            return_next = keys[-1] + 1
            return_prev = keys[0] - 1
        else:
            if action_prev:
                return_next = keys[-1] + 1
                return_prev = None
            elif action_next:
                return_next = None
                return_prev = keys[0] - 1

        return entries, return_prev, return_next
