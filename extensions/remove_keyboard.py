import telegram

from Kamisu66 import EthicsCommitteeExtension


class RemoveKeyboard(EthicsCommitteeExtension):
    def __init__(self, enabled_chat_id):
        self.enabled_chat_id = enabled_chat_id

    def main(self, EC):
        if EC.update.effective_chat.id not in self.enabled_chat_id:
            return

        if not EC.update.message:
            return

        if EC.update.message.text == '/rmkb':
            message = EC.update.message.reply_text(
                text='移除鍵盤中...',
                quote=True,
                reply_markup=telegram.ForceReply())
            EC.update.message.reply_text(
                text='已移除鍵盤',
                quote=True,
                reply_markup=telegram.ReplyKeyboardRemove())
            message.delete()


def __mainclass__():
    return RemoveKeyboard
