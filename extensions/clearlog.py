# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"/../"))
import datetime
import time
from Kamisu66 import *
from clearlog_config import limit

EC = EthicsCommittee("", "")

print(limit)
timestamp = datetime.datetime.fromtimestamp(int(time.time()-limit)).strftime('%Y-%m-%d %H:%M:%S')

rows = EC.cur.execute("""DELETE FROM log WHERE `time` < %s""", (timestamp))
EC.db.commit()
print(f"delete {rows} rows")
