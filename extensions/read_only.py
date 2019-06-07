import random
import time
import traceback

import telegram

from Kamisu66 import EthicsCommitteeExtension


class Read_only(EthicsCommitteeExtension):  # pylint: disable=W0223
    def __init__(self, deleteGroupIds, banGroupIds):
        self.deleteGroupIds = deleteGroupIds
        self.banGroupIds = banGroupIds

    def main(self, EC):
        data = EC.data
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            user_id = data["message"]["from"]["id"]

            if chat_id not in self.deleteGroupIds:
                return

            chat_member = EC.update.effective_chat.get_member(
                EC.update.effective_user.id)
            is_admin = chat_member.status in [
                chat_member.ADMINISTRATOR, chat_member.CREATOR]
            isDelete = True
            isBan = False
            try:
                if "text" in data["message"]:
                    isBan = True
                    if "NODEL" in data["message"]["text"].upper() and is_admin:
                        isDelete = False
                elif "left_chat_member" in data["message"]:
                    isDelete = False
                elif "pinned_message" in data["message"]:
                    isDelete = False
                elif "new_chat_title" in data["message"]:
                    isDelete = False
                elif "new_chat_photo" in data["message"]:
                    isDelete = False
                elif "delete_chat_photo" in data["message"]:
                    isDelete = False
                if isDelete:
                    try:
                        EC.update.message.delete()
                    except telegram.error.BadRequest as e:
                        EC.log('Delete {} in {} failed: {}'.format(
                            EC.update.message.message_id, EC.update.message.chat_id, e.message
                        ))

                    if isBan and chat_id in self.banGroupIds and not is_admin:
                        EC.cur.execute("""SELECT COUNT(*) FROM `message` WHERE `chat_id` = %s AND `user_id` = %s AND `date` > %s""",
                                       (chat_id, user_id, int(time.time() - 86400)))
                        cnt = int(EC.cur.fetchall()[0][0])

                        try:
                            until_date = int(
                                time.time() + random.randint(120, 300) * (1.5**cnt))
                            EC.bot.restrict_chat_member(
                                chat_id, user_id, until_date=until_date)
                        except telegram.error.BadRequest as e:
                            EC.log('Restrict {} in {} failed: {}'.format(
                                user_id, chat_id, e.message
                            ))
            except Exception as e:
                traceback.print_exc()
                EC.log(traceback.format_exc())


def __mainclass__():
    return Read_only
