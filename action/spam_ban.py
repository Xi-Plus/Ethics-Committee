import argparse
import contextlib
import io
import json
import re
import shlex
import subprocess
import time
import traceback

from Equivset import Equivset
from groups import groups_name
from Kamisu66 import EthicsCommittee
from spam_ban_config import *

MODULE_NAME = 'spam_ban'
PERMISSION_GLOBALBAN = MODULE_NAME + '_global_ban'


def main(data):
    if "message" in data or "edited_message" in data:
        if "message" in data:
            message = data["message"]
        elif "edited_message" in data:
            message = data["edited_message"]
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
        except Exception:
            # EC.log("[spam_ban] Equivset fail {}".format(text))
            EC.log(traceback.format_exc())

        try:
            message_id = message["message_id"]

            EC.cur.execute(
                """SELECT SUM(`count`) AS `count` FROM `message_count` WHERE `user_id` = %s AND `type` != 'new_chat_member' AND `type` NOT LIKE 'edited_%%'""", (user_id))
            rows = EC.cur.fetchall()
            if rows[0][0] is None:
                user_msg_cnt = 0
            else:
                user_msg_cnt = int(rows[0][0])

            message_deleted = False

            # action list start
            def action_ban_all_chat(user_id, duration=604800):
                EC.log("[spam_ban] kick {} in {}".format(
                    user_id, ", ".join(map(str, global_ban_chat))))
                for ban_chat_id in global_ban_chat:
                    url = "https://api.telegram.org/bot" + EC.token + "/kickChatMember?chat_id=" + \
                        str(ban_chat_id) + "&user_id=" + str(user_id) + \
                        "&until_date=" + str(int(time.time() + duration))
                    subprocess.Popen(['curl', '-s', url])

            def action_unban_all_chat(user_id):
                EC.log("[spam_ban] unban {} in {}".format(
                    user_id, ", ".join(map(str, global_ban_chat))))
                for ban_chat_id in global_ban_chat:
                    url = "https://api.telegram.org/bot{0}/unbanChatMember?chat_id={1}&user_id={2}".format(
                        EC.token, ban_chat_id, user_id)
                    subprocess.Popen(['curl', '-s', url])

            def action_del_all_msg(user_id):
                global message_deleted
                message_deleted = True

                EC.cur.execute("""SELECT `chat_id`, `message_id`, `type` FROM `message` WHERE `user_id` = %s AND `date` > %s""", (user_id, int(
                    time.time() - delete_limit)))
                rows = EC.cur.fetchall()
                EC.log("[spam_ban] find {} messages to delete".format(len(rows)))
                for row in rows:
                    if int(row[0]) in global_ban_chat:
                        EC.log("[spam_ban] delete {} ({}) in {}".format(
                            row[1], row[2], row[0]))
                        EC.deletemessage(row[0], row[1])

            def action_warn(message_id=None, text=warn_text):
                if message_deleted:
                    EC.log("[spam_ban] warn {} in {} {} skiped, msg deleted.".format(
                        user_id, chat_id, textnorm))
                    return

                EC.log("[spam_ban] warn {} in {} {}".format(
                    user_id, chat_id, textnorm))
                EC.sendmessage(text, reply=message_id)

            def action_log_admin(hashtag, admin_user_id, admin_name, action, ban_user_id, reason, duration):
                message = '{0} 所有群組 <a href="tg://user?id={1}">{2}</a> via ECbot {3} <a href="tg://user?id={4}">{4}</a> 期限為{6}\n理由：{5}'.format(
                    hashtag,
                    admin_user_id,
                    admin_name,
                    action,
                    ban_user_id,
                    reason,
                    duration
                )
                EC.log("[spam_ban] message {}".format(message))
                EC.sendmessage(chat_id=log_chat_id,
                               message=message, parse_mode="HTML")

            def action_log_bot(ban_user_id, reason, duration):
                message = '#封 #自動 所有群組(from {0}) ECbot banned <a href="tg://user?id={1}">{1}</a> 期限為{3}\n理由：{2}'.format(
                    groups_name[chat_id],
                    ban_user_id,
                    reason,
                    duration
                )
                EC.log("[spam_ban] message {}".format(message))
                EC.sendmessage(chat_id=log_chat_id,
                               message=message, parse_mode="HTML")

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
                        'h': 60 * 60,
                        'd': 60 * 60 * 24,
                        'w': 60 * 60 * 24 * 7,
                        'm': 60 * 60 * 24 * 30
                    }
                    return number * multiple[unit]
                return None

            def duration_text(duration):
                if duration == 0:
                    return '永久'
                res = ""
                if duration // (60 * 60 * 24) >= 1:
                    res += '{}日'.format(int(duration // (60 * 60 * 24)))
                    duration %= 60 * 60 * 24
                if duration // (60 * 60) >= 1:
                    res += '{}小時'.format(int(duration // (60 * 60)))
                    duration %= 60 * 60
                if duration // 60 >= 1:
                    res += '{}分'.format(int(duration // 60))
                    duration %= 60
                if duration >= 1:
                    res += '{}秒'.format(int(duration))
                return res

            # function end

            if 'text' in mode and text.startswith('/') and chat_id in global_ban_cmd_chat:
                cmd = shlex.split(text)
                action = cmd[0]
                cmd = cmd[1:]
                action = action[1:]
                action = re.sub(r'@Kamisu66EthicsCommitteeBot$', '', action)
                action = action.lower()
                if action in ['globalban', 'globalunban']:
                    if EC.check_permission(user_id, PERMISSION_GLOBALBAN, 0):
                        parser = argparse.ArgumentParser(
                            prog='/{0}'.format(action),
                            usage='%(prog)s user [-d 時長] [-r 原因] [-h]')
                        parser.add_argument(
                            'user', type=str, default=None, nargs='?', help='被用戶ID，不指定時需回覆訊息')
                        parser.add_argument('-d', type=str, metavar='時長', default='1w',
                                            help='接受單位為秒的整數，或是<整數><單位>的格式，例如：60s, 1min, 2h, 3d, 4w, 5m。預設：%(default)s')
                        parser.add_argument(
                            '-r', type=str, metavar='原因', default='未給理由', help='預設：%(default)s')
                        ok, args = EC.parse_command(parser, cmd)
                        if ok:
                            ban_user_id = args.user
                            if ban_user_id is None and "reply_to_message" in message:
                                ban_user_id = message["reply_to_message"]["from"]["id"]
                            if ban_user_id is None:
                                EC.sendmessage(
                                    '需要回覆訊息或用參數指定封鎖目標', reply=message_id)
                            else:
                                reason = args.r
                                duration = parse_duration(args.d)
                                if duration is None:
                                    EC.sendmessage(
                                        '指定的時長無效', reply=message_id)

                                elif action == "globalban":
                                    action_ban_all_chat(
                                        ban_user_id, duration)
                                    action_del_all_msg(ban_user_id)
                                    action_log_admin(
                                        '#封', user_id,
                                        message["from"]["first_name"],
                                        'banned', ban_user_id, reason,
                                        duration_text(duration)
                                    )

                                elif action == "globalunban":
                                    action_unban_all_chat(ban_user_id)
                                    action_log_admin(
                                        '#解', user_id,
                                        message["from"]["first_name"],
                                        'unbanned', ban_user_id, reason,
                                        duration_text(duration)
                                    )

                                EC.deletemessage(chat_id, message_id)
                        else:
                            EC.sendmessage(
                                args, reply=message_id, parse_mode='')
                    else:
                        EC.log(
                            '[spam_ban] {} /globalban not premission'.format(user_id))
                        EC.sendmessage('你沒有權限', reply=message_id)

            if "text" in mode:
                if user_msg_cnt <= 5:
                    if chat_id in ban_text_chat and re.search(ban_text_regex, textnorm, flags=re.I):
                        action_ban_all_chat(user_id, 604800)
                        action_del_all_msg(user_id)
                        action_log_bot(user_id, '宣傳文字', duration_text(604800))

                    elif chat_id in warn_text_chat and re.search(warn_text_regex, textnorm, flags=re.I):
                        action_warn(message_id)

                if chat_id in test_chat and re.search(r'/test', text):
                    spam_type = []
                    if re.search(ban_username_regex, textnorm, flags=re.I):
                        spam_type.append("ban_username")
                    if re.search(warn_username_regex, textnorm, flags=re.I):
                        spam_type.append("warn_username")
                    if re.search(ban_text_regex, textnorm, flags=re.I):
                        spam_type.append("ban_text")
                    if re.search(warn_text_regex, textnorm, flags=re.I):
                        spam_type.append("warn_text")
                    EC.log("[spam_ban] test pass text={} type={}".format(
                        textnorm, ", ".join(spam_type)))
                    EC.sendmessage("textnorm = {}\nspam type = {}".format(
                        textnorm,
                        ", ".join(spam_type)),
                        reply=message_id, parse_mode="")

            if "username" in mode:
                if chat_id in ban_username_chat and re.search(ban_username_regex, textnorm, flags=re.I):
                    action_ban_all_chat(user_id, 604800)
                    action_del_all_msg(user_id)
                    action_log_bot(user_id, '宣傳性用戶名', duration_text(604800))

                elif chat_id in warn_username_chat and re.search(warn_username_regex, textnorm, flags=re.I):
                    action_warn(message_id)

            if "photo" in mode:
                if chat_id in ban_photo_chat:
                    if user_msg_cnt <= 5:
                        action_ban_all_chat(user_id, 604800)
                        action_log_bot(
                            user_id, '發送圖片', duration_text(604800))

            if "forward" in mode and not message_deleted:
                if user_msg_cnt <= 5:
                    EC.sendmessage('https://t.me/{}/{}'.format(
                        message["chat"]["username"], message_id), chat_id=warn_forward_chat_id, parse_mode="HTML")
                    EC.log("[spam_ban] forward {}".format(json.dumps(message)))
                    if "forward_from_chat" in message and message["forward_from_message_id"] < 10:
                        action_warn(message_id)

        except Exception:
            traceback.print_exc()
            EC.log("[spam_ban] " + traceback.format_exc())


def web():
    EC = EthicsCommittee(MODULE_NAME + '_web', MODULE_NAME + '_web')

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

    temp = """<table>
        <tr>
        <td>chat</td>
        <td>ban_text</td>
        <td>ban_username</td>
        <td>warn_text</td>
        <td>warn_username</td>
        <td>ban_photo</td>
        <td>global_ban</td>
        </tr>
        """

    chats = list(set(ban_username_chat + warn_username_chat + ban_text_chat
                     + warn_text_chat + ban_photo_chat + global_ban_chat))
    groups_keys = list(groups.keys())
    groups_values = list(groups.values())
    chats.sort(key=lambda v: groups_keys[groups_values.index(v)].lower())
    for chat_id in chats:
        temp += '<tr>'
        if chat_id in groups_name:
            temp += '<td>{} ({})</td>'.format(chat_id, groups_name[chat_id])
        else:
            temp += '<td>{}</td>'.format(chat_id)
        for chat_setting in [ban_text_chat, ban_username_chat,
                             warn_text_chat, warn_username_chat,
                             ban_photo_chat, global_ban_chat]:
            temp += '<td>'
            if chat_id in chat_setting:
                temp += '&#10003;'
            temp += '</td>'
        temp += '</tr>'
    temp += '</table>'

    html += '<tr><td>chats</td><td>{}</td></td>'.format(temp)

    html += "<tr><td>ban_text_regex</td><td>{}</td></td>".format(
        ban_text_regex)

    html += "<tr><td>ban_username_regex</td><td>{}</td></td>".format(
        ban_username_regex)

    html += "<tr><td>warn_text_regex</td><td>{}</td></td>".format(
        warn_text_regex)

    html += "<tr><td>warn_username_regex</td><td>{}</td></td>".format(
        warn_username_regex)

    html += "<tr><td>warn_text</td><td>{}</td></td>".format(warn_text)

    users = EC.list_users_with_permission(PERMISSION_GLOBALBAN)
    html += "<tr><td>global_ban_admin</td><td>{}</td></td>".format(
        "<br>".join(map(str, users)))

    html += "<tr><td>log_chat_id</td><td>{}</td></td>".format(log_chat_id)
    html += "<tr><td>delete_limit</td><td>{}</td></td>".format(delete_limit)

    return html
