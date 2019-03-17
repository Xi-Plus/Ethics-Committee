import random
import time
import traceback

import requests

from Kamisu66 import EthicsCommittee
from read_only_config import adminList, banGroupIds, deleteGroupIds


def main(data):
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_id = data["message"]["from"]["id"]

        if chat_id not in deleteGroupIds:
            return

        EC = EthicsCommittee(chat_id, user_id)
        message_id = data["message"]["message_id"]
        date = data["message"]["date"]
        isDelete = True
        isBan = False
        try:
            if "text" in data["message"]:
                isBan = True
                if "NODEL" in data["message"]["text"].upper() and user_id in adminList:
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
                EC.deletemessage(chat_id, message_id)
                if isBan and chat_id in banGroupIds and user_id not in adminList:
                    EC.cur.execute("""SELECT COUNT(*) FROM `message` WHERE `chat_id` = %s AND `user_id` = %s AND `date` > %s""",
                                   (chat_id, user_id, int(time.time() - 86400)))
                    cnt = int(EC.cur.fetchall()[0][0])
                    url = "https://api.telegram.org/bot" + EC.token + "/restrictChatMember?chat_id=" + \
                        str(chat_id) + "&user_id=" + str(user_id) + "&until_date=" + \
                        str(int(time.time() + random.randint(120, 300) * (1.5**cnt)))
                    response = requests.get(url)
        except Exception as e:
            traceback.print_exc()
            EC.log(traceback.format_exc())
