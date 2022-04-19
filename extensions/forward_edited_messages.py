import telegram
from Kamisu66 import EthicsCommitteeExtension


class ForwardEditedMessages(EthicsCommitteeExtension):  # pylint: disable=W0223
    def __init__(self, chat_ids):
        self.chat_ids = chat_ids

    def main(self, EC):
        update = EC.update

        chat = update.effective_chat
        chat_id = chat.id

        if chat_id not in self.chat_ids:
            return

        user = update.effective_user
        if user:
            user_id = user.id
            full_name = user.full_name
        else:
            user_id = 0
            full_name = ''

        message = update.effective_message

        if update.edited_message:
            msg_types = ['text', 'sticker', 'document', 'audio', 'voice', 'photo', 'video', 'caption', 'video_note', 'poll']
            for msg_type in msg_types:
                if getattr(message, msg_type):
                    response = '<a href="tg://user?id={0}">{1}</a> edited {2} {3}'.format(
                        user_id,
                        full_name,
                        msg_type,
                        message.link,
                    )

                    EC.bot.send_message(
                        chat_id=self.chat_ids[chat_id],
                        text=response,
                        parse_mode=telegram.ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                    break


def __mainclass__():
    return ForwardEditedMessages
