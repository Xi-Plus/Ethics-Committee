# -*- coding: utf-8 -*-
import datetime
import time
from Kamisu66 import *

EC = EthicsCommittee("", "")

timestamp = datetime.datetime.fromtimestamp(int(time.time()-600)).strftime('%Y-%m-%d %H:%M:%S')

rows = EC.cur.execute("""DELETE FROM EC_log WHERE `time` < %s""", (timestamp))
EC.db.commit()
print(f"delete {rows} rows")
