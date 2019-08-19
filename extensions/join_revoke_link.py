from Kamisu66 import EthicsCommitteeExtension


class JoinRevokeLink(EthicsCommitteeExtension):  # pylint: disable=W0223
    def __init__(self, revoke_chat_ids):
        self.revoke_chat_ids = revoke_chat_ids

    def main(self, EC):
        if not EC.update.message:
            return

        if not EC.update.message.new_chat_members:
            return

        chat_id = EC.update.effective_chat.id
        if chat_id in self.revoke_chat_ids:
            EC.bot.export_chat_invite_link(chat_id=chat_id)
            EC.log('[jrl] revoke link for {}'.format(chat_id))


def __mainclass__():
    return JoinRevokeLink
