from Kamisu66 import EthicsCommittee
import re
import traceback
import requests
import subprocess
import time
import json
import argparse
import shlex
import contextlib
import io
from Equivset import Equivset
from groups import *
from spam_ban_config import *


def main(data):
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]

        if chat_id not in (global_ban_chat + test_chat + global_ban_cmd_chat):
            return

        mode = []
        text = ""
        if "text" in message:
            text += message["text"]
            mode.append("text")
        if "photo" in message:
            mode.append("photo")
        if "document" in message:
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
        try:
            textnorm = Equivset(text)
            # EC.log("[spam_ban] Equivset ok {}".format(text2))
            textnorm = text + "\n" + textnorm
        except Exception as e:
            # EC.log("[spam_ban] Equivset fail {}".format(text))
            EC.log(traceback.format_exc())

        try:
            message_id = message["message_id"]
            date = message["date"]

            EC.cur.execute("""SELECT COUNT(*) FROM `message` WHERE `user_id` = %s AND `type` != 'new_chat_member'""", (user_id))
            user_msg_cnt = int(EC.cur.fetchall()[0][0])

            message_deleted = False

            # action list start
            def action_ban_all_chat(user_id, duration=604800):
                EC.log("[spam_ban] kick {} in {}".format(user_id, ", ".join(map(str, global_ban_chat))))
                for ban_chat_id in global_ban_chat:
                    url = "https://api.telegram.org/bot"+EC.token+"/kickChatMember?chat_id="+str(ban_chat_id)+"&user_id="+str(user_id)+"&until_date="+str(int(time.time()+duration))
                    subprocess.Popen(['curl', '-s', url])

            def action_unban_all_chat(user_id):
                EC.log("[spam_ban] unban {} in {}".format(user_id, ", ".join(map(str, global_ban_chat))))
                for ban_chat_id in global_ban_chat:
                    url = "https://api.telegram.org/bot"+EC.token+"/unbanChatMember?chat_id="+str(ban_chat_id)+"&user_id="+str(user_id)
                    subprocess.Popen(['curl', '-s', url])

            def action_del_all_msg(user_id):
                global message_deleted
                message_deleted = True

                EC.cur.execute("""SELECT `chat_id`, `message_id`, `type` FROM `message` WHERE `user_id` = %s AND `date` > %s""", (user_id, int(time.time()-delete_limit)))
                rows = EC.cur.fetchall()
                EC.log("[spam_ban] find {} messages to delete".format(len(rows)))
                for row in rows:
                    if int(row[0]) in global_ban_chat:
                        EC.log("[spam_ban] delete {} ({}) in {}".format(row[1], row[2], row[0]))
                        EC.deletemessage(row[0], row[1])

            def action_warn(message_id=None, text=warn_text):
                if message_deleted:
                    EC.log("[spam_ban] warn {} in {} {} skiped, msg deleted.".format(user_id, chat_id, textnorm))
                    return

                EC.log("[spam_ban] warn {} in {} {}".format(user_id, chat_id, textnorm))
                EC.sendmessage(text, reply=message_id)

            def action_log_admin(hashtag, admin_user_id, admin_name, action, ban_user_id, reason):
                message = '{0} 所有群組 <a href="tg://user?id={1}">{2}</a> via ECbot {3} <a href="tg://user?id={4}">{4}</a>\n理由：{5}'.format(
                        hashtag,
                        admin_user_id,
                        admin_name,
                        action,
                        ban_user_id,
                        reason
                    )
                EC.log("[spam_ban] message {}".format(message))
                EC.sendmessage(chat_id=log_chat_id, message=message, parse_mode="HTML")

            def action_log_bot(ban_user_id, reason):
                message = '#封 #自動 所有群組(from {0}) ECbot banned <a href="tg://user?id={1}">{1}</a>\n理由：{2}'.format(
                        groups_name[chat_id],
                        ban_user_id,
                        reason
                    )
                EC.log("[spam_ban] message {}".format(message))
                EC.sendmessage(chat_id=log_chat_id, message=message, parse_mode="HTML")

            # action list end
            # function start

            def parse_duration(duration):
                duration = duration.lower()
                if duration in ['inf', 'indef', 'infinite', 'infinity', 'indefinite', 'never']:
                    return 0
                m = re.search(r'^(\d+)$', duration)
                if m:
                    return int(duration)
                m = re.search(r'^(\d+)(s|min|h|d|w|m)$', duration)
                if m:
                    number = int(m.group(1))
                    unit = m.group(2)
                    multiple = {
                        's': 1,
                        'min': 60,
                        'h': 60*60,
                        'd': 60*60*24,
                        'w': 60*60*24*7,
                        'm': 60*60*24*30
                    }
                    return number * multiple[unit]
                return None

            # function end

            if 'text' in mode and text.startswith('/') and chat_id in global_ban_cmd_chat:
                EC.log('[spam_ban] {}'.format(text))
                cmd = shlex.split(text)
                action = cmd[0]
                cmd = cmd[1:]
                action = action[1:]
                action = re.sub(r'@Kamisu66EthicsCommitteeBot$', '', action)
                action = action.lower()
                if action in ['globalban', 'globalunban']:
                    parser = argparse.ArgumentParser(prog='/{0}@Kamisu66EthicsCommitteeBot'.format(action), usage='%(prog)s user [-d 時長] [-r 原因] [-h]')
                    parser.add_argument('user', type=str, default=None, nargs='?', help='被用戶ID，不指定時需回覆訊息')
                    parser.add_argument('-d', type=str, metavar='時長', default='1w', help='接受單位為秒的整數，或是<整數><單位>的格式，例如：60s, 1min, 2h, 3d, 4w, 5m。預設：%(default)s')
                    parser.add_argument('-r', type=str, metavar='原因', default='未給理由', help='預設：%(default)s')
                    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
                        try:
                            args = parser.parse_args(cmd)
                        except SystemExit as e:
                            output = buf.getvalue()
                            EC.sendmessage(output, reply=message_id, parse_mode='')
                        else:
                            if user_id in global_ban_admin:
                                ban_user_id = args.user
                                if ban_user_id is None and "reply_to_message" in message:
                                    ban_user_id = message["reply_to_message"]["from"]["id"]
                                if ban_user_id is None:
                                    EC.sendmessage('需要回覆訊息或用參數指定封鎖目標', reply=message_id)
                                else:
                                    reason = args.r
                                    duration = parse_duration(args.d)
                                    if duration is None:
                                        EC.sendmessage('指定的時長無效', reply=message_id)
                                    
                                    elif action == "globalban":
                                        action_ban_all_chat(ban_user_id, duration)
                                        action_del_all_msg(ban_user_id)
                                        action_log_admin('#封', user_id, message["from"]["first_name"], 'banned', ban_user_id, reason)

                                    elif action == "globalunban":
                                        action_unban_all_chat(ban_user_id)
                                        action_log_admin('#解', user_id, message["from"]["first_name"], 'unbanned', ban_user_id, reason)
                                    
                                    # EC.deletemessage(chat_id, message_id)
                            else:
                                EC.log('[spam_ban] {} /globalban not premission'.format(user_id))
                                EC.sendmessage('你沒有權限', reply=message_id)
                            
            if "text" in mode:
                if user_msg_cnt <= 5:
                    if chat_id in ban_text_chat and re.search(ban_text_regex, textnorm, flags=re.I):
                        action_ban_all_chat(user_id)
                        action_del_all_msg(user_id)
                        action_log_bot(user_id, '宣傳文字')

                    elif chat_id in warn_text_chat and re.search(warn_text_regex, textnorm, flags=re.I):
                        action_warn(message_id)

                if chat_id in test_chat:
                    spam_type = []
                    if re.search(ban_username_regex, textnorm, flags=re.I):
                        spam_type.append("ban_username")
                    if re.search(warn_username_regex, textnorm, flags=re.I):
                        spam_type.append("warn_username")
                    if re.search(ban_text_regex, textnorm, flags=re.I):
                        spam_type.append("ban_text")
                    if re.search(warn_text_regex, textnorm, flags=re.I):
                        spam_type.append("warn_text")
                    if len(spam_type) > 0:
                        EC.log("[spam_ban] test pass text={} type={}".format(textnorm, ", ".join(spam_type)))
                        EC.sendmessage("spam type = {}".format(", ".join(spam_type)), reply=message_id, parse_mode="")

            if "username" in mode:
                if chat_id in ban_username_chat and re.search(ban_username_regex, textnorm, flags=re.I):
                    action_ban_all_chat(user_id)
                    action_del_all_msg(user_id)
                    action_log_bot(user_id, '宣傳性用戶名')

                elif chat_id in warn_username_chat and re.search(warn_username_regex, textnorm, flags=re.I):
                    action_warn(message_id)

            if "photo" in mode:
                if chat_id in ban_photo_chat:
                    if user_msg_cnt <= 5:
                        action_ban_all_chat(user_id)
                        action_log_bot(user_id, '於 @wikipedia_zh 發送圖片')

            if "forward" in mode and not message_deleted:
                if user_msg_cnt <= 5:
                    EC.sendmessage('https://t.me/{}/{}'.format(message["chat"]["username"], message_id), chat_id=warn_forward_chat_id, parse_mode="HTML")
                    EC.log("[spam_ban] forward {}".format(json.dumps(message)))
                    if "forward_from_chat" in message and message["forward_from_message_id"] < 10:
                        action_warn(message_id)

        except Exception as e:
            traceback.print_exc()
            EC.log("[spam_ban] "+traceback.format_exc())


def web():
    html = """
        <style>
            table {
                border-collapse: collapse;
            }
            th, td {
                vertical-align: top;
                border: 1px solid black;
                padding: 3px;
            }
        </style>
       <table>
       <tr>
       <td>variable</td>
       <td>value</td>
       </tr>
       """
    html += "<tr><td>ban_text_regex</td><td>{}</td></td>".format(ban_text_regex)
    temp = []
    for chat_id in ban_text_chat:
        if chat_id in groups_name:
            temp.append("{} ({})".format(chat_id, groups_name[chat_id]))
        else:
            temp.append("{}".format(chat_id))
    html += "<tr><td>ban_text_chat</td><td>{}</td></td>".format("<br>".join(temp))

    html += "<tr><td>ban_username_regex</td><td>{}</td></td>".format(ban_username_regex)
    temp = []
    for chat_id in ban_username_chat:
        if chat_id in groups_name:
            temp.append("{} ({})".format(chat_id, groups_name[chat_id]))
        else:
            temp.append("{}".format(chat_id))
    html += "<tr><td>ban_username_chat</td><td>{}</td></td>".format("<br>".join(temp))

    html += "<tr><td>warn_text_regex</td><td>{}</td></td>".format(warn_text_regex)
    temp = []
    for chat_id in warn_text_chat:
        if chat_id in groups_name:
            temp.append("{} ({})".format(chat_id, groups_name[chat_id]))
        else:
            temp.append("{}".format(chat_id))
    html += "<tr><td>warn_text_chat</td><td>{}</td></td>".format("<br>".join(temp))

    html += "<tr><td>warn_username_regex</td><td>{}</td></td>".format(warn_username_regex)
    temp = []
    for chat_id in warn_username_chat:
        if chat_id in groups_name:
            temp.append("{} ({})".format(chat_id, groups_name[chat_id]))
        else:
            temp.append("{}".format(chat_id))
    html += "<tr><td>warn_username_chat</td><td>{}</td></td>".format("<br>".join(temp))

    html += "<tr><td>warn_text</td><td>{}</td></td>".format(warn_text)

    temp = []
    for chat_id in ban_photo_chat:
        if chat_id in groups_name:
            temp.append("{} ({})".format(chat_id, groups_name[chat_id]))
        else:
            temp.append("{}".format(chat_id))
    html += "<tr><td>ban_photo_chat</td><td>{}</td></td>".format("<br>".join(temp))

    temp = []
    for chat_id in global_ban_chat:
        if chat_id in groups_name:
            temp.append("{} ({})".format(chat_id, groups_name[chat_id]))
        else:
            temp.append("{}".format(chat_id))
    html += "<tr><td>global_ban_chat</td><td>{}</td></td>".format("<br>".join(temp))

    html += "<tr><td>global_ban_admin</td><td>{}</td></td>".format("<br>".join(map(str, global_ban_admin)))

    html += "<tr><td>log_chat_id</td><td>{}</td></td>".format(log_chat_id)
    html += "<tr><td>delete_limit</td><td>{}</td></td>".format(delete_limit)

    return html
