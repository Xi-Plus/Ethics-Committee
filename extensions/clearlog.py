# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time

from clearlog_config import limit  # pylint: disable=E0401
sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Kamisu66 import EthicsCommittee

EC = EthicsCommittee(0, 0)

print(limit)
timestamp = datetime.datetime.fromtimestamp(int(time.time() - limit)).strftime('%Y-%m-%d %H:%M:%S')

rows = EC.cur.execute("""DELETE FROM log WHERE `time` < %s""", (timestamp))
EC.db.commit()
print(f"delete {rows} rows")
