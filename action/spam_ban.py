from Kamisu66 import EthicsCommittee
import re
import traceback
import requests
import subprocess
import time
from groups import *
from spam_ban_config import *


def main(data):
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]

        if chat_id not in (ban_username_chat+warn_username_chat+ban_text_chat+warn_text_chat):
            return

        if "text" in message:
            text = message["text"]
            mode = "text"
        elif "caption" in message:
            text = message["caption"]
            mode = "text"
        elif "new_chat_member" in message:
            text = message["from"]["first_name"]
            if "last_name" in message["from"]:
                text += " " + message["from"]["last_name"]
            mode = "username"
        else:
            return

        EC = EthicsCommittee(chat_id, user_id)
        message_id = message["message_id"]
        date = message["date"]
        try:
            if mode == "text" and re.match(r"/globalban@Kamisu66EthicsCommitteeBot", text):
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
                        if m is not None and m.group(1) != "":
                            reason = m.group(1)
                    if ban_user_id != "":
                        EC.deletemessage(EC.chat_id, message_id)

                        EC.cur.execute("""SELECT `chat_id`, `message_id` FROM `EC_message` WHERE `user_id` = %s AND `type` = 'new_chat_member'""", (ban_user_id))
                        rows = EC.cur.fetchall()
                        for row in rows:
                            EC.log("[spam_ban] delete {} in {}".format(row[1], row[0]))
                            EC.deletemessage(row[0], row[1])
                        for ban_chat_id in ban_username_chat:
                            EC.log("[spam_ban] kick {} in {}".format(ban_user_id, ban_chat_id))

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
            elif re.search(bad_regex, text):
                if mode == "text":
                    if chat_id in ban_text_chat:
                        EC.cur.execute("""SELECT COUNT(*) FROM `EC_message` WHERE `user_id` = %s""", (user_id))
                        cnt = int(EC.cur.fetchall()[0][0])
                        if cnt < 5:
                            EC.log("[spam_ban] kick {} in {} {}".format(user_id, chat_id, text))

                            url = "https://api.telegram.org/bot"+EC.token+"/kickChatMember?chat_id="+str(chat_id)+"&user_id="+str(user_id)+"&until_date="+str(int(time.time()+86400*7))
                            subprocess.Popen(['curl', '-s', url])

                            message = '#封 #自動 {0} ECbot banned <a href="tg://user?id={1}">{1}</a>\n理由：宣傳文字'.format(
                                    groups_name[chat_id],
                                    user_id
                                )
                            EC.log("[spam_ban] message {}".format(message))
                            EC.sendmessage(chat_id=log_chat_id, message=message, parse_mode="HTML")

                    elif chat_id in warn_text_chat:
                        EC.cur.execute("""SELECT COUNT(*) FROM `EC_message` WHERE `chat_id` = %s AND `user_id` = %s""", (chat_id, user_id))
                        cnt = int(EC.cur.fetchall()[0][0])
                        if cnt < 5 or chat_id in [groups['xiplustestbot']]:
                            EC.log("[spam_ban] warn {} in {} {}".format(user_id, chat_id, text))
                            EC.sendmessage(warn_text, reply=message_id)

                elif mode == "username":
                    if chat_id in ban_username_chat:
                        EC.deletemessage(chat_id, message_id)

                        for ban_chat_id in ban_username_chat:
                            EC.log("[spam_ban] kick {} in {} {}".format(user_id, ban_chat_id, text))

                            url = "https://api.telegram.org/bot"+EC.token+"/kickChatMember?chat_id="+str(ban_chat_id)+"&user_id="+str(user_id)+"&until_date="+str(int(time.time()+86400*7))
                            subprocess.Popen(['curl', '-s', url])

                        message = '#封 #自動 所有群組(from {0}) ECbot banned <a href="tg://user?id={1}">{1}</a>\n理由：宣傳性用戶名'.format(
                                groups_name[chat_id],
                                user_id
                            )
                        EC.log("[spam_ban] message {}".format(message))
                        EC.sendmessage(chat_id=log_chat_id, message=message, parse_mode="HTML")

                    elif chat_id in warn_username_chat:
                        EC.log("[spam_ban] warn {} in {} {}".format(user_id, chat_id, text))
                        EC.sendmessage(warn_text, reply=message_id)

        except Exception as e:
            traceback.print_exc()
            EC.log("[spam_ban] "+traceback.format_exc())
