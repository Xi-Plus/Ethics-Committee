import json
import traceback

from Kamisu66 import EthicsCommitteeExtension


class AntiFlood(EthicsCommitteeExtension):
    def __init__(self, enable_chats):
        self.enable_chats = enable_chats

    def main(self, EC):
        update = EC.update

        chat = update.effective_chat
        chat_id = chat.id
        chat_title = chat.title
        if chat_id not in self.enable_chats:
            return

        user = update.effective_user
        if not user:
            return

        user_id = user.id
        full_name = user.full_name

        message = update.effective_message
        date = int(message.date.timestamp())

        for msglimit, timelimit in self.enable_chats[chat_id]:
            EC.cur.execute(
                """SELECT COUNT(*)  FROM `message` WHERE `chat_id` = %s AND `user_id` = %s AND `date` > %s""",
                (chat_id, user_id, int(date - timelimit)))
            count = EC.cur.fetchone()[0]

            EC.log("[anti_flood] {}({}) {}({}) limit: {} msg/{} s count: {} msg".format(chat_title,
                                                                chat_id, full_name, user_id, msglimit, timelimit, count))


def __mainclass__():
    return AntiFlood
