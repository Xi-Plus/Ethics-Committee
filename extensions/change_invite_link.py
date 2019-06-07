# -*- coding: utf-8 -*-
import argparse
import os
import sys

import telegram

from change_invite_link_config import change_groups
sys.path.insert(0, os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + '/../'))
from Kamisu66 import EthicsCommittee


parser = argparse.ArgumentParser()
parser.add_argument('group')
parser.add_argument('--no-message', dest='message', action='store_false')
parser.add_argument('--new-message', dest='new', action='store_true')
parser.set_defaults(message=True, new=False)
args = parser.parse_args()
print(args)

EC = EthicsCommittee(0, 0)

if args.group not in change_groups:
    exit('chat not found')

group = change_groups[args.group]

print(group)

link = EC.bot.export_chat_invite_link(chat_id=group['chat_id'])
print(link)

if args.message:
    text = group['message']['text'].format(link)
else:
    text = group['message']['no_text'].format(link)

print(text)

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
    if args.new:
        res = EC.bot.send_message(
            chat_id=group['message']['chat_id'],
            message_id=group['message']['message_id'],
            text=text,
            parse_mode='',
        )
        print(res)
