# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time

from clearlog_config import limit, tables  # pylint: disable=E0401
sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Kamisu66 import EthicsCommittee

EC = EthicsCommittee(0, 0)

print(limit)
timestamp = datetime.datetime.fromtimestamp(int(time.time() - limit)).strftime('%Y-%m-%d %H:%M:%S')

for table in tables:
    rows = EC.cur.execute("""DELETE FROM {} WHERE `time` < %s""".format(table), (timestamp))
    EC.db.commit()
    print("delete {} rows from {} table".format(rows, table))

del EC
