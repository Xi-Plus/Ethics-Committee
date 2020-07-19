from Kamisu66 import load_extensions

extensions = []
webs = {}


# record
RECORD_CHAT_IDS = [
    -1001234567890,
    -1001234567891,
]
EXT_record = load_extensions('record')(full_log_chat_id=RECORD_CHAT_IDS)


# log
EXT_log = load_extensions('log')()


extensions.append(EXT_record)

webs['log'] = EXT_log
