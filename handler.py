import logging

from config_extension_new import extensions_new  # pylint: disable=E0401
from Kamisu66new import EthicsCommittee
from telethon import events


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

bot = EthicsCommittee().start()

for extension in extensions_new:
    extension.prepare(bot)
    bot.add_event_handler(extension.main, events.NewMessage)

print('Server ready!')
bot.run_until_disconnected()
