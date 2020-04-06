import re
import time

import telegram
from Kamisu66 import EthicsCommitteeExtension


class BanMySelf(EthicsCommitteeExtension):  # pylint: disable=W0223
    MODULE_NAME = 'ban_my_self'

    COMMAND = r'^/banmyself@Kamisu66EthicsCommitteeBot$'
    DURATION = 60

    def __init__(self, enabled_chat_id):
        self.enabled_chat_id = enabled_chat_id

    def main(self, EC):
        update = EC.update

        if update.effective_chat.id not in self.enabled_chat_id:
            return

        if not update.message or not update.message.text:
            return

        if re.search(self.COMMAND, update.message.text):
            EC.bot.delete_message(update.effective_chat.id, update.message.message_id)

            chatMember = update.effective_chat.get_member(update.effective_user.id)
            if chatMember.status not in [chatMember.ADMINISTRATOR, chatMember.CREATOR]:
                try:
                    until_date = until_date = int(time.time() + self.DURATION)
                    EC.bot.kick_chat_member(
                        chat_id=update.effective_chat.id,
                        user_id=update.effective_user.id,
                        until_date=until_date,
                    )
                except telegram.error.BadRequest as e:
                    EC.log('[ban_my_self] restrict {} in {} failed: {}'.format(
                        update.effective_user.id, update.effective_chat.id, e.message))
            else:
                EC.log('[ban_my_self] skip restrict {} in {}'.format(
                    update.effective_user.id, update.effective_chat.id))


def __mainclass__():
    return BanMySelf
