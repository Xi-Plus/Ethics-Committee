import telegram

from Kamisu66 import EthicsCommitteeExtension


class GetUserId(EthicsCommitteeExtension):  # pylint: disable=W0223
    def main(self, EC):
        if not EC.update.message:
            return

        if not EC.update.message.reply_to_message:
            return

        if EC.update.message.text == '/getid':
            response = '<a href="tg://user?id={0}">{0}</a>'.format(
                EC.update.message.reply_to_message.from_user.id
            )
            EC.update.message.reply_text(
                text=response,
                quote=True,
                parse_mode=telegram.ParseMode.HTML,
            )


def __mainclass__():
    return GetUserId
