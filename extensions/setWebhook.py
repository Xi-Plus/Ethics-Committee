# -*- coding: utf-8 -*-
import argparse
import os
import sys
import urllib.request

import requests

sys.path.insert(0, os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Kamisu66 import EthicsCommittee


EC = EthicsCommittee(0, 0)

parser = argparse.ArgumentParser()
parser.add_argument('action', default='set')
parser.add_argument('--url', default=EC.url)
parser.add_argument('--max_connections', default=EC.max_connections)
args = parser.parse_args()
print(args)

if args.action == 'set':
    url = "https://api.telegram.org/bot{0}/setWebhook?url={1}&max_connections={2}".format(
        EC.token, args.url, args.max_connections)
elif args.action == 'delete':
    url = "https://api.telegram.org/bot{0}/deleteWebhook".format(EC.token)
elif args.action == 'get':
    url = "https://api.telegram.org/bot{0}/getWebhookInfo".format(EC.token)
else:
    exit('unknown action.')

response = requests.get(url)
print(response.text)
