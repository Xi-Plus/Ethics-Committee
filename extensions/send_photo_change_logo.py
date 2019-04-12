import tempfile

import telegram

from Kamisu66 import EthicsCommitteeExtension


class SendPhotoChangeLogo(EthicsCommitteeExtension):
    def __init__(self, enabled_chat_id):
        self.enabled_chat_id = enabled_chat_id

    def main(self, EC):
        if EC.update.effective_chat.id not in self.enabled_chat_id:
            return

        if not EC.update.message:
            return

        if EC.update.message.photo:
            EC.update.effective_chat.send_action(
                telegram.ChatAction.UPLOAD_PHOTO)

            temp = tempfile.NamedTemporaryFile()
            EC.update.message.photo[-1].get_file().download(temp.name)

            EC.update.effective_chat.send_action(
                telegram.ChatAction.UPLOAD_PHOTO)

            EC.bot.set_chat_photo(
                chat_id=EC.update.effective_chat.id, photo=open(temp.name, 'rb'))


def __mainclass__():
    return SendPhotoChangeLogo
