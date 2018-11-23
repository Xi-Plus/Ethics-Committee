from Kamisu66 import EthicsCommittee
import re
import traceback
import requests
import subprocess
import time
import json
from groups import *
from spam_ban_config import *


def main(data):
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]

        all_chat = list(set(ban_username_chat + warn_username_chat + ban_text_chat + warn_text_chat))
        if chat_id not in (all_chat + test_chat):
            return

        mode = []
        text = ""
        if "text" in message:
            text += message["text"]
            mode.append("text")
        if "photo" in message:
            mode.append("photo")
        if "caption" in message:
            text += message["caption"]
            mode.append("text")
        if "new_chat_member" in message:
            text += message["from"]["first_name"]
            if "last_name" in message["from"]:
                text += " " + message["from"]["last_name"]
            mode.append("username")
        if "forward_from_chat" in message:
            mode.append("forward")
        if "forward_from" in message:
            mode.append("forward")
        if len(mode) == 0:
            return

        EC = EthicsCommittee(chat_id, user_id)
        message_id = message["message_id"]
        date = message["date"]
        try:
            if "text" in mode and re.match(r"/globalban@Kamisu66EthicsCommitteeBot", text):
                if user_id in globalbanuser:
                    m = re.match(r"/globalban@Kamisu66EthicsCommitteeBot (\d+)(?:\n(.+))?", text)
                    ban_user_id = ""
                    reason = "未給理由"
                    if m is not None:
                        ban_user_id = int(m.group(1))
                        if m.group(2) is not None and m.group(2) != "":
                            reason = m.group(2)
                    elif "reply_to_message" in message:
                        ban_user_id = message["reply_to_message"]["from"]["id"]
                        m = re.match(r"/globalban@Kamisu66EthicsCommitteeBot(?:\n(.+))?", text)
                        if m is not None and m.group(1) is not None and m.group(1) != "":
                            reason = m.group(1)
                    if ban_user_id != "":
                        EC.deletemessage(EC.chat_id, message_id)

                        EC.cur.execute("""SELECT `chat_id`, `message_id`, `type` FROM `EC_message` WHERE `user_id` = %s AND `date` > %s""", (ban_user_id, int(time.time()-delete_limit)))
                        rows = EC.cur.fetchall()
                        EC.log("[spam_ban] find {} messages to delete".format(len(rows)))
                        for row in rows:
                            if int(row[0]) in all_chat:
                                EC.log("[spam_ban] delete {} ({}) in {}".format(row[1], row[2], row[0]))
                                EC.deletemessage(row[0], row[1])

                        EC.log("[spam_ban] kick {} in {}".format(ban_user_id, ", ".join(map(str, all_chat))))
                        for ban_chat_id in all_chat:
                            url = "https://api.telegram.org/bot"+EC.token+"/kickChatMember?chat_id="+str(ban_chat_id)+"&user_id="+str(ban_user_id)+"&until_date="+str(int(time.time()+86400*7))
                            subprocess.Popen(['curl', '-s', url])

                        message = '#封 所有群組 <a href="tg://user?id={0}">{1}</a> via ECbot banned <a href="tg://user?id={2}">{2}</a>\n理由：{3}'.format(
                                user_id,
                                message["from"]["first_name"],
                                ban_user_id,
                                reason
                            )
                        EC.log("[spam_ban] message {}".format(message))
                        EC.sendmessage(chat_id=log_chat_id, message=message, parse_mode="HTML")
                else:
                    EC.log("[spam_ban] {} /globalban not premission".format(user_id))
            if "forward" in mode:
                EC.cur.execute("""SELECT COUNT(*) FROM `EC_message` WHERE `user_id` = %s""", (user_id))
                cnt = int(EC.cur.fetchall()[0][0])
                if cnt < 5:
                    EC.sendmessage("@xiplus", reply=message_id)
                    EC.log("[spam_ban] forward {}".format(json.dumps(message)))
            if "text" in mode:
                EC.cur.execute("""SELECT COUNT(*) FROM `EC_message` WHERE `user_id` = %s""", (user_id))
                cnt = int(EC.cur.fetchall()[0][0])
                if cnt < 5:
                    if chat_id in ban_text_chat and re.search(ban_text_regex, text, flags=re.I):
                        EC.cur.execute("""SELECT `chat_id`, `message_id`, `type` FROM `EC_message` WHERE `user_id` = %s AND `date` > %s""", (user_id, int(time.time()-delete_limit)))
                        rows = EC.cur.fetchall()
                        EC.log("[spam_ban] find {} messages to delete".format(len(rows)))
                        for row in rows:
                            if int(row[0]) in all_chat:
                                EC.log("[spam_ban] delete {} ({}) in {}".format(row[1], row[2], row[0]))
                                EC.deletemessage(row[0], row[1])

                        EC.log("[spam_ban] kick {} in {}".format(user_id, ", ".join(map(str, ban_text_chat))))
                        for ban_chat_id in all_chat:
                            url = "https://api.telegram.org/bot"+EC.token+"/kickChatMember?chat_id="+str(ban_chat_id)+"&user_id="+str(user_id)+"&until_date="+str(int(time.time()+86400*7))
                            subprocess.Popen(['curl', '-s', url])

                        message = '#封 #自動 所有群組(from {0}) ECbot banned <a href="tg://user?id={1}">{1}</a>\n理由：宣傳文字'.format(
                                groups_name[chat_id],
                                user_id
                            )
                        EC.log("[spam_ban] message {}".format(message))
                        EC.sendmessage(chat_id=log_chat_id, message=message, parse_mode="HTML")

                    elif chat_id in warn_text_chat and re.search(warn_text_regex, text, flags=re.I):
                        EC.log("[spam_ban] warn {} in {} {}".format(user_id, chat_id, text))
                        EC.sendmessage(warn_text, reply=message_id)

                if chat_id in test_chat:
                    spam_type = []
                    if re.search(ban_username_regex, text, flags=re.I):
                        spam_type.append("ban_username")
                    if re.search(warn_username_regex, text, flags=re.I):
                        spam_type.append("warn_username")
                    if re.search(ban_text_regex, text, flags=re.I):
                        spam_type.append("ban_text")
                    if re.search(warn_text_regex, text, flags=re.I):
                        spam_type.append("warn_text")
                    if len(spam_type) > 0:
                        EC.sendmessage("spam type = {}".format(", ".join(spam_type)), reply=message_id, parse_mode="")

            if "username" in mode:
                if chat_id in ban_username_chat and re.search(ban_username_regex, text, flags=re.I):
                    EC.deletemessage(chat_id, message_id)

                    EC.log("[spam_ban] kick {} in {}".format(user_id, ", ".join(map(str, ban_username_chat))))
                    for ban_chat_id in all_chat:
                        url = "https://api.telegram.org/bot"+EC.token+"/kickChatMember?chat_id="+str(ban_chat_id)+"&user_id="+str(user_id)+"&until_date="+str(int(time.time()+86400*7))
                        subprocess.Popen(['curl', '-s', url])

                    message = '#封 #自動 所有群組(from {0}) ECbot banned <a href="tg://user?id={1}">{1}</a>\n理由：宣傳性用戶名'.format(
                            groups_name[chat_id],
                            user_id
                        )
                    EC.log("[spam_ban] message {}".format(message))
                    EC.sendmessage(chat_id=log_chat_id, message=message, parse_mode="HTML")

                elif chat_id in warn_username_chat and re.search(warn_username_regex, text, flags=re.I):
                    EC.log("[spam_ban] warn {} in {} {}".format(user_id, chat_id, text))
                    EC.sendmessage(warn_text, reply=message_id)

            if "photo" in mode:
                if chat_id in ban_photo_chat:
                    EC.cur.execute("""SELECT COUNT(*) FROM `EC_message` WHERE `user_id` = %s""", (user_id))
                    cnt = int(EC.cur.fetchall()[0][0])
                    if cnt < 5:
                        EC.log("[spam_ban] kick {} in {}".format(user_id, ", ".join(map(str, ban_photo_chat))))
                        for ban_chat_id in all_chat:
                            url = "https://api.telegram.org/bot"+EC.token+"/kickChatMember?chat_id="+str(ban_chat_id)+"&user_id="+str(user_id)+"&until_date="+str(int(time.time()+86400*7))
                            subprocess.Popen(['curl', '-s', url])

                        message = '#封 #自動 所有群組(from {0}) ECbot banned <a href="tg://user?id={1}">{1}</a>\n理由：於 @wikipedia_zh 發送圖片'.format(
                                groups_name[chat_id],
                                user_id
                            )
                        EC.log("[spam_ban] message {}".format(message))
                        EC.sendmessage(chat_id=log_chat_id, message=message, parse_mode="HTML")

        except Exception as e:
            traceback.print_exc()
            EC.log("[spam_ban] "+traceback.format_exc())
