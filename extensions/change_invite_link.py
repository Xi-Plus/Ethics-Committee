# -*- coding: utf-8 -*-
import argparse
import json
import os
import sys

import telegram

from change_invite_link_config import *
sys.path.insert(0, os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + '/../'))
from Kamisu66 import EthicsCommittee


parser = argparse.ArgumentParser()
parser.add_argument('chat_id', type=int)
parser.add_argument('--no-message', dest='message', action='store_false')
parser.set_defaults(message=True)
args = parser.parse_args()
print(args)

chat_id = args.chat_id

EC = EthicsCommittee(0, 0)

if chat_id not in change_groups:
    exit('chat_id not found')

group = change_groups[chat_id]

print(group)

link = EC.bot.export_chat_invite_link(chat_id=chat_id)

text = group['message']['text'].format(link)

print(text)

if args.message:
    try:
        res = EC.bot.edit_message_text(
            chat_id=group['message']['chat_id'],
            message_id=group['message']['message_id'],
            text=text,
            parse_mode='',
        )
        print(res)
    except telegram.TelegramError as e:
        print(e.message)
        res = EC.bot.send_message(
            chat_id=group['message']['chat_id'],
            message_id=group['message']['message_id'],
            text=text,
            parse_mode='',
        )
        print(res)
