import argparse
import json
import re
import shlex
import time
import traceback

import telegram

from Equivset import Equivset
from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class Spam_ban(EthicsCommitteeExtension):
    MODULE_NAME = 'spam_ban'

    PERMISSION_GLOBALBAN = MODULE_NAME + '_global_ban'
    PERMISSION_GRANT = MODULE_NAME + '_grant'
    PERMISSION_SETTING = MODULE_NAME + '_setting'

    SETTING_BAN_TEXT = MODULE_NAME + '_ban_text'
    SETTING_BAN_USERNAME = MODULE_NAME + '_ban_username'
    SETTING_WARN_TEXT = MODULE_NAME + '_warn_text'
    SETTING_WARN_USERNAME = MODULE_NAME + '_warn_username'
    SETTING_BAN_PHOTO = MODULE_NAME + '_ban_photo'
    SETTING_GLOBAL_BAN = MODULE_NAME + '_global_ban'
    SETTING_GLOBAL_BAN_CMD = MODULE_NAME + '_global_ban_cmd'
    SETTING_TEST = MODULE_NAME + '_test'

    CMD_GLOBALBAN = r'^global_?ban$'
    CMD_GLOBALUNBAN = r'^global_?unban$'
    CMD_GRANT = r'^grant_?global_?ban$'
    CMD_REVOKE = r'^revoke_?global_?ban$'
    CMD_ENABLE_BAN_TEXT = r'^enable_?ban_?text$'
    CMD_ENABLE_BAN_USERNAME = r'^enable_?ban_?username$'
    CMD_ENABLE_WARN_TEXT = r'^enable_?warn_?text$'
    CMD_ENABLE_WARN_USERNAME = r'^enable_?warn_?username$'
    CMD_ENABLE_GLOBALBAN = r'^enable_?global_?ban$'
    CMD_DISABLE_BAN_TEXT = r'^disable_?ban_?text$'
    CMD_DISABLE_BAN_USERNAME = r'^disable_?ban_?username$'
    CMD_DISABLE_WARN_TEXT = r'^disable_?warn_?text$'
    CMD_DISABLE_WARN_USERNAME = r'^disable_?warn_?username$'
    CMD_DISABLE_GLOBALBAN = r'^disable_?global_?ban$'

    EC = None
    chat_id = None
    user_id = None
    is_reply = None
    first_name = None
    reply_to_user_id = None
    reply_to_full_name = None
    message_id = None
    textnorm = None
    message_deleted = False

    def __init__(self, ban_text_regex, ban_username_regex, warn_text_regex, warn_username_regex, warn_text, log_chat_id, warn_forward_chat_id, delete_limit):
        self.ban_text_regex = ban_text_regex
        self.ban_username_regex = ban_username_regex
        self.warn_text_regex = warn_text_regex
        self.warn_username_regex = warn_username_regex
        self.warn_text = warn_text
        self.log_chat_id = log_chat_id
        self.warn_forward_chat_id = warn_forward_chat_id
        self.delete_limit = delete_limit

        self.EC = EthicsCommittee(0, 0)
        self.ban_text_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_BAN_TEXT)]
        self.ban_username_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_BAN_USERNAME)]
        self.warn_text_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_WARN_TEXT)]
        self.warn_username_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_WARN_USERNAME)]
        self.ban_photo_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_BAN_PHOTO)]
        self.global_ban_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_GLOBAL_BAN)]
        self.global_ban_cmd_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_GLOBAL_BAN_CMD)]
        self.test_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_TEST)]

        self.EC.cur.execute(
            """SELECT `chat_id`, `title` FROM `group_name` WHERE `chat_id` IN ('{}')""".format(
                "', '".join(
                    [str(v) for v in (
                        self.ban_text_chat + self.ban_username_chat + self.warn_text_chat
                        + self.warn_username_chat + self.ban_photo_chat + self.global_ban_chat)]
                )))
        rows = self.EC.cur.fetchall()
        self.group_name = {}
        for row in rows:
            self.group_name[int(row[0])] = row[1]

    def main(self, EC):
        self.EC = EC
        data = EC.data
        if "message" in data or "edited_message" in data:
            if "message" in data:
                message = data["message"]
            elif "edited_message" in data:
                message = data["edited_message"]
            self.chat_id = message["chat"]["id"]
            self.user_id = message["from"]["id"]
            self.message_id = message["message_id"]

            self.first_name = message["from"]["first_name"]
            full_name = message["from"]["first_name"]
            if "last_name" in message["from"]:
                full_name += " " + message["from"]["last_name"]
            if "reply_to_message" in message:
                self.is_reply = True
                self.reply_to_user_id = message["reply_to_message"]["from"]["id"]
                self.reply_to_full_name = message["reply_to_message"]["from"]["first_name"]
                if "last_name" in message["reply_to_message"]["from"]:
                    self.reply_to_full_name += ' ' + \
                        message["reply_to_message"]["from"]["last_name"]

            if 'text' in message and message['text'].startswith('/'):
                cmd = shlex.split(message['text'])
                action = cmd[0]
                cmd = cmd[1:]
                action = action[1:]
                action = re.sub(r'@{}$'.format(
                    re.escape(EC.bot.username)), '', action)
                action = action.lower()
                self.is_reply = 'reply_to_message' in message

                self.handle_cmd(action, cmd)

            if self.chat_id not in self.global_ban_chat + self.test_chat + self.global_ban_cmd_chat:
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

            try:
                textnorm = Equivset(text)
                # EC.log("[spam_ban] Equivset ok {}".format(text2))
                textnorm = text + "\n" + textnorm
                self.textnorm = textnorm
            except Exception:
                # EC.log("[spam_ban] Equivset fail {}".format(text))
                EC.log(traceback.format_exc())

            try:
                EC.cur.execute(
                    """SELECT SUM(`count`) AS `count` FROM `message_count` WHERE `user_id` = %s AND `type` != 'new_chat_member' AND `type` NOT LIKE 'edited_%%'""", (self.user_id))
                rows = EC.cur.fetchall()
                if rows[0][0] is None:
                    user_msg_cnt = 0
                else:
                    user_msg_cnt = int(rows[0][0])

                if "text" in mode:
                    if user_msg_cnt <= 5:
                        if self.chat_id in self.ban_text_chat and re.search(self.ban_text_regex, textnorm, flags=re.I):
                            self.action_ban_all_chat(self.user_id, 604800)
                            self.action_del_all_msg(self.user_id)
                            self.action_log_bot(self.user_id, '宣傳文字',
                                                self.duration_text(604800))

                        elif self.chat_id in self.warn_text_chat and re.search(self.warn_text_regex, textnorm, flags=re.I):
                            self.action_warn(self.message_id)

                    if self.chat_id in self.test_chat and re.search(r'/test', text):
                        spam_type = []
                        if re.search(self.ban_username_regex, textnorm, flags=re.I):
                            spam_type.append("ban_username")
                        if re.search(self.warn_username_regex, textnorm, flags=re.I):
                            spam_type.append("warn_username")
                        if re.search(self.ban_text_regex, textnorm, flags=re.I):
                            spam_type.append("ban_text")
                        if re.search(self.warn_text_regex, textnorm, flags=re.I):
                            spam_type.append("warn_text")
                        EC.log("[spam_ban] test pass text={} type={}".format(
                            textnorm, ", ".join(spam_type)))
                        EC.sendmessage(
                            "textnorm = {}\nspam type = {}".format(
                                textnorm,
                                ", ".join(spam_type)),
                            reply=self.message_id, parse_mode="")

                if "username" in mode:
                    if self.chat_id in self.ban_username_chat and re.search(self.ban_username_regex, textnorm, flags=re.I):
                        self.action_ban_all_chat(self.user_id, 604800)
                        self.action_del_all_msg(self.user_id)
                        self.action_log_bot(self.user_id, '宣傳性用戶名',
                                            self.duration_text(604800))

                    elif self.chat_id in self.warn_username_chat and re.search(self.warn_username_regex, textnorm, flags=re.I):
                        self.action_warn(self.message_id)

                if "photo" in mode:
                    if self.chat_id in self.ban_photo_chat:
                        if user_msg_cnt <= 5:
                            self.action_ban_all_chat(self.user_id, 604800)
                            self.action_log_bot(
                                self.user_id, '發送圖片', self.duration_text(604800))

                if "forward" in mode and not self.message_deleted:
                    if user_msg_cnt <= 5:
                        EC.sendmessage('https://t.me/{}/{}'.format(
                            message["chat"]["username"], self.message_id), chat_id=self.warn_forward_chat_id, parse_mode="HTML")
                        EC.log("[spam_ban] forward {}".format(
                            json.dumps(message)))
                        if "forward_from_chat" in message and message["forward_from_message_id"] < 10:
                            self.action_warn(self.message_id)

            except Exception:
                traceback.print_exc()
                EC.log("[spam_ban] " + traceback.format_exc())

    def handle_cmd(self, action, cmd):
        if self.chat_id in self.global_ban_chat + self.global_ban_cmd_chat:
            if re.search(self.CMD_GLOBALBAN, action):
                self.cmd_globalban(action, cmd)

            if re.search(self.CMD_GLOBALUNBAN, action):
                self.cmd_globalunban(action, cmd)

            if re.search(self.CMD_GRANT, action):
                self.cmd_grant()

            if re.search(self.CMD_REVOKE, action):
                self.cmd_revoke()

        if re.search(self.CMD_ENABLE_BAN_TEXT, action):
            self.cmd_setting_enable(self.SETTING_BAN_TEXT)

        if re.search(self.CMD_ENABLE_BAN_USERNAME, action):
            self.cmd_setting_enable(self.SETTING_BAN_USERNAME)

        if re.search(self.CMD_ENABLE_WARN_TEXT, action):
            self.cmd_setting_enable(self.SETTING_WARN_TEXT)

        if re.search(self.CMD_ENABLE_WARN_USERNAME, action):
            self.cmd_setting_enable(self.SETTING_WARN_USERNAME)

        if re.search(self.CMD_ENABLE_GLOBALBAN, action):
            self.cmd_setting_enable(self.SETTING_GLOBAL_BAN)

        if re.search(self.CMD_DISABLE_BAN_TEXT, action):
            self.cmd_setting_disable(self.SETTING_BAN_TEXT)

        if re.search(self.CMD_DISABLE_BAN_USERNAME, action):
            self.cmd_setting_disable(self.SETTING_BAN_USERNAME)

        if re.search(self.CMD_DISABLE_WARN_TEXT, action):
            self.cmd_setting_disable(self.SETTING_WARN_TEXT)

        if re.search(self.CMD_DISABLE_WARN_USERNAME, action):
            self.cmd_setting_disable(self.SETTING_WARN_USERNAME)

        if re.search(self.CMD_DISABLE_GLOBALBAN, action):
            self.cmd_setting_disable(self.SETTING_GLOBAL_BAN)

    def cmd_globalban(self, action, cmd):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GLOBALBAN, 0):
            self.EC.log(
                '[spam_ban] {} /globalban no premission'.format(self.user_id))
            self.EC.sendmessage('你沒有權限進行全域封鎖的動作', reply=self.message_id)
            return

        parser = argparse.ArgumentParser(
            prog='/{0}'.format(action),
            usage='%(prog)s user [-d 時長] [-r 原因] [-h]')
        parser.add_argument(
            'user', type=str, default=None, nargs='?', help='欲封鎖用戶ID，不指定時需回覆訊息')
        parser.add_argument('-d', type=str, metavar='時長', default='1w',
                            help='接受單位為秒的整數，或是<整數><單位>的格式，例如：60s, 1min, 2h, 3d, 4w, 5m。預設：%(default)s')
        parser.add_argument(
            '-r', type=str, metavar='原因', default='Spam', help='預設：%(default)s')
        ok, args = self.EC.parse_command(parser, cmd)

        if not ok:
            self.EC.sendmessage(args, reply=self.message_id, parse_mode='')
            return

        ban_user_id = args.user
        if ban_user_id is None and self.is_reply:
            ban_user_id = self.reply_to_user_id
        if ban_user_id is None:
            self.EC.sendmessage('需要回覆訊息或用參數指定封鎖目標', reply=self.message_id)
            return

        ban_user_id = int(ban_user_id)
        reason = args.r
        duration = self.parse_duration(args.d)
        if duration is None:
            self.EC.sendmessage('指定的時長無效', reply=self.message_id)
            return

        if ban_user_id == self.EC.bot.id:
            self.EC.sendmessage('你不能對機器人執行此操作', reply=self.message_id)
            return

        failed = self.action_ban_all_chat(ban_user_id, duration)
        self.action_del_all_msg(ban_user_id)
        self.action_log_admin(
            '#封', self.user_id,
            self.first_name,
            'banned', ban_user_id, reason,
            self.duration_text(duration),
            failed,
        )
        self.EC.deletemessage(self.chat_id, self.message_id)

    def cmd_globalunban(self, action, cmd):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GLOBALBAN, 0):
            self.EC.log(
                '[spam_ban] {} /globalunban no premission'.format(self.user_id))
            self.EC.sendmessage('你沒有權限進行全域解除封鎖的動作',
                                reply=self.message_id)
            return

        parser = argparse.ArgumentParser(
            prog='/{0}'.format(action),
            usage='%(prog)s user [-r 原因] [-h]')
        parser.add_argument(
            'user', type=str, default=None, nargs='?', help='欲解除封鎖用戶ID，不指定時需回覆訊息')
        parser.add_argument(
            '-r', type=str, metavar='原因', default='無原因', help='預設：%(default)s')
        ok, args = self.EC.parse_command(parser, cmd)

        if not ok:
            self.EC.sendmessage(args, reply=self.message_id, parse_mode='')
            return

        ban_user_id = args.user
        if ban_user_id is None and self.is_reply:
            ban_user_id = self.reply_to_user_id
        if ban_user_id is None:
            self.EC.sendmessage('需要回覆訊息或用參數指定解除封鎖目標', reply=self.message_id)
            return

        ban_user_id = int(ban_user_id)
        reason = args.r

        if ban_user_id == self.EC.bot.id:
            self.EC.sendmessage('你不能對機器人執行此操作', reply=self.message_id)
            return

        failed = self.action_unban_all_chat(ban_user_id)
        self.action_log_admin(
            '#解', self.user_id,
            self.first_name,
            'unbanned', ban_user_id, reason,
            self.duration_text(0),
            failed,
        )
        self.EC.deletemessage(self.chat_id, self.message_id)

    def cmd_grant(self):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GRANT, 0):
            self.EC.sendmessage('你沒有權限進行授予權限的動作', reply=self.message_id)
            return

        if not self.is_reply:
            self.EC.sendmessage('你需要回應一則訊息以授予權限', reply=self.message_id)
            return

        ok = self.EC.add_permission(
            self.reply_to_user_id, self.PERMISSION_GLOBALBAN, 0)
        if ok:
            self.EC.sendmessage('已授予 {} 全域封鎖的權限'.format(
                self.reply_to_full_name), reply=self.message_id)
        else:
            self.EC.sendmessage('{} 已有全域封鎖的權限'.format(
                self.reply_to_full_name), reply=self.message_id)

    def cmd_revoke(self):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GRANT, 0):
            self.EC.sendmessage('你沒有權限進行解除權限', reply=self.message_id)
            return

        if not self.is_reply:
            self.EC.sendmessage('你需要回應一則訊息以解除權限', reply=self.message_id)
            return

        ok = self.EC.remove_permission(
            self.reply_to_user_id, self.PERMISSION_GLOBALBAN, 0)
        if ok:
            self.EC.sendmessage('已解除 {} 全域封鎖的權限'.format(
                self.reply_to_full_name), reply=self.message_id)
        else:
            self.EC.sendmessage('{} 沒有全域封鎖的權限'.format(
                self.reply_to_full_name), reply=self.message_id)

    def cmd_setting_enable(self, setting):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_SETTING, 0):
            self.EC.sendmessage('你沒有權限變更自動封鎖設定', reply=self.message_id)
            return

        cm = self.EC.bot.get_chat_member(self.chat_id, self.EC.bot.id)
        if not cm.can_delete_messages or not cm.can_restrict_members:
            self.EC.sendmessage(
                '請先授予機器人"Delete messages"和"Ban users"後才能啟用此功能', reply=self.message_id)
            return

        rows = self.EC.list_setting_in_group(self.chat_id, setting)
        if rows:
            self.EC.sendmessage('本群早已啟用 {}'.format(setting),
                                reply=self.message_id,
                                parse_mode='')
        else:
            ok = self.EC.add_group_setting(self.chat_id, setting, 'enable')
            self.EC.sendmessage('本群已啟用 {}'.format(setting),
                                reply=self.message_id,
                                parse_mode='')

    def cmd_setting_disable(self, setting):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_SETTING, 0):
            self.EC.sendmessage('你沒有權限變更自動封鎖設定', reply=self.message_id)
            return

        rows = self.EC.list_setting_in_group(self.chat_id, setting)
        if rows:
            ok = self.EC.remove_group_setting(self.chat_id, setting)
            self.EC.sendmessage('本群已停用 {}'.format(setting),
                                reply=self.message_id,
                                parse_mode='')
        else:
            self.EC.sendmessage('本群並未啟用 {}'.format(setting),
                                reply=self.message_id,
                                parse_mode='')

    # action list start
    def action_ban_all_chat(self, user_id, duration=604800):
        self.EC.log("[spam_ban] kick {} in {}".format(
            user_id, ", ".join(map(str, self.global_ban_chat))))
        until_date = int(time.time() + duration)
        failed = 0
        for ban_chat_id in self.global_ban_chat:
            try:
                self.EC.bot.kick_chat_member(
                    chat_id=ban_chat_id, user_id=user_id, until_date=until_date)
            except telegram.error.BadRequest as e:
                self.EC.log(e.message)
                failed += 1
        return failed

    def action_unban_all_chat(self, user_id):
        self.EC.log("[spam_ban] unban {} in {}".format(
            user_id, ", ".join(map(str, self.global_ban_chat))))
        failed = 0
        for ban_chat_id in self.global_ban_chat:
            try:
                self.EC.bot.unban_chat_member(
                    chat_id=ban_chat_id, user_id=user_id)
            except telegram.error.BadRequest as e:
                self.EC.log(e.message)
                failed += 1
        return failed

    def action_del_all_msg(self, user_id):
        self.message_deleted = True

        self.EC.cur.execute("""SELECT `chat_id`, `message_id`, `type` FROM `message` WHERE `user_id` = %s AND `date` > %s""", (user_id, int(
            time.time() - self.delete_limit)))
        rows = self.EC.cur.fetchall()
        self.EC.log(
            "[spam_ban] find {} messages to delete".format(len(rows)))
        for row in rows:
            if int(row[0]) in self.global_ban_chat:
                self.EC.log("[spam_ban] delete {} ({}) in {}".format(
                    row[1], row[2], row[0]))
                self.EC.deletemessage(row[0], row[1])

    def action_warn(self, message_id=None, text=None):
        if text is None:
            text = self.warn_text
        if self.message_deleted:
            self.EC.log("[spam_ban] warn {} in {} {} skiped, msg deleted.".format(
                self.user_id, self.chat_id, self.textnorm))
            return
        self.message_deleted = True

        self.EC.log("[spam_ban] warn {} in {} {}".format(
            self.user_id, self.chat_id, self.textnorm))
        self.EC.sendmessage(text, reply=message_id)
        self.EC.sendmessage('/globalban {}'.format(self.user_id))

    def action_log_admin(self, hashtag, admin_user_id, admin_name, action, ban_user_id, reason, duration, failed):
        message = '{0} 所有群組 <a href="tg://user?id={1}">{2}</a> via ECbot {3} <a href="tg://user?id={4}">{4}</a> 期限為{6}，{7}成功，{8}失敗\n理由：{5}'.format(
            hashtag,
            admin_user_id,
            admin_name,
            action,
            ban_user_id,
            reason,
            duration,
            len(self.global_ban_chat) - failed,
            failed,
        )
        self.EC.log("[spam_ban] message {}".format(message))
        self.EC.sendmessage(chat_id=self.log_chat_id,
                            message=message, parse_mode="HTML")

    def action_log_bot(self, ban_user_id, reason, duration):
        message = '#封 #自動 所有群組(from {0}) ECbot banned <a href="tg://user?id={1}">{1}</a> 期限為{3}\n理由：{2}'.format(
            self.EC.get_group_name(self.chat_id),
            ban_user_id,
            reason,
            duration
        )
        self.EC.log("[spam_ban] message {}".format(message))
        self.EC.sendmessage(chat_id=self.log_chat_id,
                            message=message, parse_mode="HTML")
    # action list end

    # function start
    def parse_duration(self, duration):
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

    def duration_text(self, duration):
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

    def web(self):
        EC = EthicsCommittee(0, 0)

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

        chats = list(set(self.ban_username_chat + self.warn_username_chat + self.ban_text_chat
                         + self.warn_text_chat + self.ban_photo_chat + self.global_ban_chat))
        for chat_id in chats:
            temp += '<tr>'
            if chat_id in self.group_name:
                temp += '<td>{} ({})</td>'.format(chat_id,
                                                  self.group_name[chat_id])
            else:
                temp += '<td>{}</td>'.format(chat_id)
            for chat_setting in [self.ban_text_chat, self.ban_username_chat,
                                 self.warn_text_chat, self.warn_username_chat,
                                 self.ban_photo_chat, self.global_ban_chat]:
                temp += '<td>'
                if chat_id in chat_setting:
                    temp += '&#10003;'
                temp += '</td>'
            temp += '</tr>'
        temp += '</table>'

        html += '<tr><td>chats</td><td>{}</td></td>'.format(temp)

        html += "<tr><td>ban_text_regex</td><td>{}</td></td>".format(
            self.ban_text_regex)

        html += "<tr><td>ban_username_regex</td><td>{}</td></td>".format(
            self.ban_username_regex)

        html += "<tr><td>warn_text_regex</td><td>{}</td></td>".format(
            self.warn_text_regex)

        html += "<tr><td>warn_username_regex</td><td>{}</td></td>".format(
            self.warn_username_regex)

        html += "<tr><td>warn_text</td><td>{}</td></td>".format(self.warn_text)

        users = EC.list_users_with_permission(self.PERMISSION_GLOBALBAN)
        html += "<tr><td>global_ban_admin</td><td>{}</td></td>".format(
            "<br>".join(map(str, users)))

        html += "<tr><td>log_chat_id</td><td>{}</td></td>".format(
            self.log_chat_id)
        html += "<tr><td>delete_limit</td><td>{}</td></td>".format(
            self.delete_limit)

        return html


def __mainclass__():
    return Spam_ban
