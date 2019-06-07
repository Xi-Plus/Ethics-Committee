import telegram

from Kamisu66 import EthicsCommitteeExtension


class Bot_added_notification(EthicsCommitteeExtension):  # pylint: disable=W0223
    def __init__(self, notice_chat_id):
        self.notice_chat_id = notice_chat_id

    def main(self, EC):
        if not EC.update.message:
            return

        if EC.update.message.new_chat_members and EC.update.message.new_chat_members[0].id == EC.bot.id:
            message = '機器人被 <a href="tg://user?id={}">{}</a> 加入了群 {} {}'.format(
                EC.update.effective_user.id,
                EC.update.effective_user.full_name,
                EC.update.effective_chat.id,
                EC.update.effective_chat.title)
            EC.bot.send_message(chat_id=self.notice_chat_id,
                                text=message,
                                parse_mode=telegram.ParseMode.HTML)

        if EC.update.message.left_chat_member and EC.update.message.left_chat_member.id == EC.bot.id:
            message = '機器人被 <a href="tg://user?id={}">{}</a> 移出了群 {} {}'.format(
                EC.update.effective_user.id,
                EC.update.effective_user.full_name,
                EC.update.effective_chat.id,
                EC.update.effective_chat.title)
            EC.bot.send_message(chat_id=self.notice_chat_id,
                                text=message,
                                parse_mode=telegram.ParseMode.HTML)


def __mainclass__():
    return Bot_added_notification
