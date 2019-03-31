# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__))+"/../"))
import json
import configparser
from Kamisu66 import *
import time
import urllib.request
from change_invite_link_config import *

EC = EthicsCommittee("ChangeInviteLink", "ChangeInviteLink")

if len(sys.argv) < 2:
	exit("not given chat_id")

try:
	chat_id = int(sys.argv[1])
except ValueError as e:
	exit("chat_id not a value")

if chat_id not in change_groups:
	exit("chat_id not found")

group = change_groups[chat_id]

print(group)

url = "https://api.telegram.org/bot"+EC.token+"/exportChatInviteLink?chat_id="+str(chat_id)

try:
	res = urllib.request.urlopen(url).read().decode("utf8")
except urllib.error.HTTPError as e:
	exit(e.read().decode("utf8"))

res = json.loads(res)

link = res["result"]
text = group["message"]["text"].format(link)

print(text)

res = EC.editmessage(group["message"]["message_id"], text,
                     chat_id=group["message"]["chat_id"], parse_mode="")
print(res)

if res['ok'] is False and res['description'] == 'Bad Request: message to edit not found':
    res = EC.sendmessage(text,
                         chat_id=group["message"]["chat_id"], parse_mode="")
    print(res)
