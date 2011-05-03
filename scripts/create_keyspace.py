#!/usr/bin/env python
from pycassa.system_manager import *

KS = 'logsandra'

# Create keyspace
sys = SystemManager()
sys.create_keyspace(KS, 1)

# Create column families
sys.create_column_family(KS, 'entries')
sys.create_column_family(KS, 'by_date', LONG_TYPE)
