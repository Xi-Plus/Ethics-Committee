# -*- coding: utf-8 -*-
import argparse
import os
import sys

import requests

import telegram
sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../'))
from Kamisu66 import EthicsCommittee
from wiki_admins_config import CHATS, TGNAME  # pylint: disable=E0401


parser = argparse.ArgumentParser()
parser.add_argument('group')
parser.add_argument('--dry-run', dest='dry_run', action='store_true')
parser.add_argument('--new-message', dest='new', action='store_true')
parser.add_argument('--empty-message', dest='empty', action='store_true')
parser.set_defaults(dry_run=False, new=False, empty=False)
args = parser.parse_args()
print(args)

EC = EthicsCommittee(0, 0)

if args.group not in CHATS:
    exit('chat not found')

setting = CHATS[args.group]

print(setting)

text = ''
if args.empty:
    text = '(empty)'
else:
    for group in setting['groups']:
        print(group[0])
        text += '{}:\n'.format(group[1])
        for site in setting['sites']:
            domain = site[0]
            sitename = site[1]

            print(sitename)

            text2 = ''

            api = 'https://{}/w/api.php'.format(domain)

            # sysop
            payload = {
                "action": "query",
                "format": "json",
                "list": "allusers",
                "augroup": group[0]
            }
            res = r = requests.get(api, params=payload).json()
            for user in res['query']['allusers']:
                if user['name'] in TGNAME:
                    print('\t', TGNAME[user['name']])
                    if TGNAME[user['name']].startswith('@'):
                        text2 += ' ' + TGNAME[user['name']]
                    else:
                        text2 += ' <a href="tg://user?id={}">{}</a>'.format(TGNAME[user['name']], user['name'])
                else:
                    print('\t', user['name'])

            if text2:
                text += '<a href="https://{}/w/index.php?title=Special:ListUsers&group={}">{}</a>:{}\n'.format(
                    domain, group[0], sitename, text2)

        if len(group) >= 3:
            text += group[2]

print(text)

if args.dry_run:
    exit()

try:
    if args.empty:
        res = EC.bot.send_message(
            chat_id=setting['message']['chat_id'],
            message_id=setting['message']['message_id'],
            text=setting['message']['text'].format(text),
            parse_mode=telegram.ParseMode.HTML,
        )
        print(res)
    elif args.new:
        res = EC.bot.send_message(
            chat_id=setting['message']['chat_id'],
            message_id=setting['message']['message_id'],
            text=setting['message']['text'].format(text),
            parse_mode=telegram.ParseMode.HTML,
        )
        print(res)
    else:
        res = EC.bot.edit_message_text(
            chat_id=setting['message']['chat_id'],
            message_id=setting['message']['message_id'],
            text=setting['message']['text'].format(text),
            parse_mode=telegram.ParseMode.HTML,
        )
        print(res)
except telegram.TelegramError as e:
    print(e.message)
