from Kamisu66 import load_extensions

extensions = []
webs = []

extensions.append(load_extensions('record')())

cfg = {
    'database': {
        'host': 'localhost',
        'user': '',
        'passwd': '',
        'db': 'EthicsCommittee',
        'charset': '',
    },
    'telegram': {
        'token': '',
        'botname': '',
        'botid': 0,
        'url': '',
        'max_connections': '5',
    },
}
