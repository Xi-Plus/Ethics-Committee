# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"/../"))
import json
import configparser
from Kamisu66 import *
import time
import urllib.request
from ImpureCat_config import delconfigs

EC = EthicsCommittee(0, 0)

dellimit = int(time.time()-86400*2)

EC.cur.execute("""DELETE FROM `message` WHERE `date` < %s""", (int(time.time()-86400*14)))
EC.db.commit()

for delconfig in delconfigs:
	chat_id = delconfig[0]
	deltime = int(time.time()-delconfig[1])
	print(chat_id, deltime)
	EC.cur.execute("""SELECT * FROM `message` WHERE `chat_id` = %s AND `date` < %s AND `date` > %s AND `deleted` = 0 ORDER BY `date`""", (chat_id, str(deltime), str(dellimit)))
	rows = EC.cur.fetchall()
	for row in rows:
		message_id = row[2]
		print(row, message_id)
		EC.deletemessage(chat_id, message_id)
