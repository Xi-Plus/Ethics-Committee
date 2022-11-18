import argparse
import json
import os
import re
import shlex
import subprocess
import time
import traceback

import requests
import telegram
from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension


class Spam_ban(EthicsCommitteeExtension):
    MODULE_NAME = 'spam_ban'

    PERMISSION_GLOBALBAN = MODULE_NAME + '_global_ban'
    PERMISSION_GRANT = MODULE_NAME + '_grant'
    PERMISSION_SETTING = MODULE_NAME + '_setting'
    PERMISSION_RULE = MODULE_NAME + '_rule'

    SETTING_BAN_TEXT = MODULE_NAME + '_ban_text'
    SETTING_BAN_USERNAME = MODULE_NAME + '_ban_username'
    SETTING_WARN_TEXT = MODULE_NAME + '_warn_text'
    SETTING_WARN_USERNAME = MODULE_NAME + '_warn_username'
    SETTING_BAN_YOUTUBE_LINK = MODULE_NAME + '_ban_youtube_link'
    SETTING_BAN_PHOTO = MODULE_NAME + '_ban_photo'
    SETTING_WARN_FORWARD = MODULE_NAME + '_warn_forward'
    SETTING_GLOBAL_BAN = MODULE_NAME + '_global_ban'
    SETTING_GLOBAL_BAN_CMD = MODULE_NAME + '_global_ban_cmd'
    SETTING_TEST = MODULE_NAME + '_test'
    SETTING_REGEX_BAN_TEXT = MODULE_NAME + '_regex_ban_text'
    SETTING_REGEX_BAN_USERNAME = MODULE_NAME + '_regex_ban_username'
    SETTING_REGEX_WARN_TEXT = MODULE_NAME + '_regex_warn_text'
    SETTING_REGEX_WARN_USERNAME = MODULE_NAME + '_regex_warn_username'

    GROUP_SET = 'globalban'

    CMD_SINGLEBAN = r'^single_?ban$'
    CMD_GLOBALBAN = r'^global_?ban$'
    CMD_GLOBALUNBAN = r'^global_?unban$'
    CMD_GLOBALRESTRICT = r'^global_?restrict$'
    CMD_GLOBALUNRESTRICT = r'^global_?unrestrict$'
    CMD_GRANT = r'^grant_?global_?ban$'
    CMD_REVOKE = r'^revoke_?global_?ban$'
    CMD_ENABLE_BAN_TEXT = r'^enable_?ban_?text$'
    CMD_ENABLE_BAN_USERNAME = r'^enable_?ban_?username$'
    CMD_ENABLE_WARN_TEXT = r'^enable_?warn_?text$'
    CMD_ENABLE_WARN_USERNAME = r'^enable_?warn_?username$'
    CMD_ENABLE_BAN_YOUTUBE_LINK = r'^enable_?ban_?youtube_?link$'
    CMD_ENABLE_WARN_FORWARD = r'^enable_?warn_?forward$'
    CMD_ENABLE_GLOBALBAN = r'^enable_?global_?ban$'
    CMD_DISABLE_BAN_TEXT = r'^disable_?ban_?text$'
    CMD_DISABLE_BAN_USERNAME = r'^disable_?ban_?username$'
    CMD_DISABLE_WARN_TEXT = r'^disable_?warn_?text$'
    CMD_DISABLE_WARN_USERNAME = r'^disable_?warn_?username$'
    CMD_DISABLE_BAN_YOUTUBE_LINK = r'^disable_?ban_?youtube_?link$'
    CMD_DISABLE_WARN_FORWARD = r'^disable_?warn_?forward$'
    CMD_DISABLE_GLOBALBAN = r'^disable_?global_?ban$'
    CMD_ADD_RULE_BAN_TEXT = r'^add_?spam_?rule_?ban_?text$'
    CMD_ADD_RULE_BAN_USERNAME = r'^add_?spam_?rule_?ban_?username$'
    CMD_ADD_RULE_WARN_TEXT = r'^add_?spam_?rule_?warn_?text$'
    CMD_ADD_RULE_WARN_USERNAME = r'^add_?spam_?rule_?warn_?username$'
    CMD_REMOVE_RULE_BAN_TEXT = r'^remove_?spam_?rule_?ban_?text$'
    CMD_REMOVE_RULE_BAN_USERNAME = r'^remove_?spam_?rule_?ban_?username$'
    CMD_REMOVE_RULE_WARN_TEXT = r'^remove_?spam_?rule_?warn_?text$'
    CMD_REMOVE_RULE_WARN_USERNAME = r'^remove_?spam_?rule_?warn_?username$'
    CMD_TEST_RULE = r'^/test_?spam_?rule '

    TEST_LIMIT = 1000
    RATE_LIMIT_WARN = 0.02
    RATE_LIMIT_DISALLOW = 0.05

    DEFAULT_REASON = 'Spam'
    DEFAULT_DURATION = '1w'
    AUTO_DURATION = '1w'

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

    def __init__(self, warn_text, ban_youtube_link_regex, log_chat_id, warn_forward_new_chat_limit, warn_forward_chat_id, delete_limit):
        self.EC = EthicsCommittee(0, 0)

        self._load_setting_from_database()

        self.warn_text = warn_text
        self.ban_youtube_link_regex = ban_youtube_link_regex
        self.log_chat_id = log_chat_id
        self.warn_forward_new_chat_limit = warn_forward_new_chat_limit
        self.warn_forward_chat_id = warn_forward_chat_id
        self.delete_limit = delete_limit

    def _load_setting_from_database(self):
        self.EC.cur.execute("""SET SESSION group_concat_max_len=1048576""")

        self.EC.cur.execute(
            """SELECT GROUP_CONCAT(`value` ORDER BY `value` SEPARATOR '|') FROM `group_setting` WHERE `key` = %s GROUP BY ''""",
            (self.SETTING_REGEX_BAN_TEXT))
        self.ban_text_regex = self.EC.cur.fetchone()[0]

        self.EC.cur.execute(
            """SELECT GROUP_CONCAT(`value` ORDER BY `value` SEPARATOR '|') FROM `group_setting` WHERE `key` IN (%s, %s) GROUP BY ''""",
            (self.SETTING_REGEX_BAN_TEXT, self.SETTING_REGEX_BAN_USERNAME))
        self.ban_username_regex = self.EC.cur.fetchone()[0]

        self.EC.cur.execute(
            """SELECT GROUP_CONCAT(`value` ORDER BY `value` SEPARATOR '|') FROM `group_setting` WHERE `key` IN (%s, %s) GROUP BY ''""",
            (self.SETTING_REGEX_WARN_TEXT, self.SETTING_REGEX_BAN_TEXT))
        self.warn_text_regex = self.EC.cur.fetchone()[0]

        self.EC.cur.execute(
            """SELECT GROUP_CONCAT(`value` ORDER BY `value` SEPARATOR '|') FROM `group_setting` WHERE `key` IN (%s, %s, %s, %s) GROUP BY ''""",
            (self.SETTING_REGEX_WARN_TEXT, self.SETTING_REGEX_WARN_USERNAME, self.SETTING_REGEX_BAN_TEXT, self.SETTING_REGEX_BAN_USERNAME))
        self.warn_username_regex = self.EC.cur.fetchone()[0]

        self.ban_text_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_BAN_TEXT)]
        self.ban_username_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_BAN_USERNAME)]
        self.warn_text_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_WARN_TEXT)]
        self.warn_username_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_WARN_USERNAME)]
        self.ban_youtube_link_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_BAN_YOUTUBE_LINK)]
        self.ban_photo_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_BAN_PHOTO)]
        self.warn_forward_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_WARN_FORWARD)]
        self.global_ban_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_GLOBAL_BAN)]
        self.global_ban_cmd_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_GLOBAL_BAN_CMD)]
        self.test_chat = [
            int(row[0]) for row in self.EC.list_group_with_setting(self.SETTING_TEST)]

        self.EC.cur.execute(
            """SELECT `chat_id`, `title`, `username` FROM `group_name` WHERE `chat_id` IN ('{}')""".format(
                "', '".join(
                    [str(v) for v in (
                        self.ban_text_chat + self.ban_username_chat + self.warn_text_chat
                        + self.warn_username_chat + self.ban_photo_chat + self.ban_youtube_link_chat
                        + self.warn_forward_chat + self.global_ban_chat + self.global_ban_cmd_chat)]
                )))
        rows = self.EC.cur.fetchall()
        self.group_name = {}
        self.group_username = {}
        for row in rows:
            self.group_name[int(row[0])] = row[1]
            self.group_username[int(row[0])] = row[2]

    def main(self, EC):
        self.EC = EC
        self.update = update = EC.update
        if update.message or update.edited_message:
            if update.message:
                message = update.message
            elif update.edited_message:
                message = update.edited_message
            self.chat_id = update.effective_chat.id
            self.user_id = update.effective_user.id
            self.message_id = message.message_id

            self.first_name = update.effective_user.first_name
            full_name = update.effective_user.full_name
            if message.reply_to_message:
                self.is_reply = True
                self.reply_to_user_id = message.reply_to_message.from_user.id
                self.reply_to_full_name = message.reply_to_message.from_user.full_name
            else:
                self.is_reply = False

            if message.text and message.text.startswith('/'):
                try:
                    cmd = shlex.split(message.text, posix=True)
                    action = cmd[0]
                    cmd = cmd[1:]
                    action = action[1:]
                    action = re.sub(r'@{}$'.format(
                        re.escape(EC.bot.username)), '', action)
                    action = action.lower()

                    self.handle_cmd(action, cmd)
                except ValueError:
                    pass

            if self.chat_id not in self.global_ban_chat + self.test_chat + self.global_ban_cmd_chat:
                return

            mode = []
            text = ""
            if message.text:
                text += message.text
                mode.append("text")
            if message.photo:
                mode.append("photo")
            if message.document:
                text += message.document.file_name
                mode.append("text")
                mode.append("photo")
            if message.caption:
                text += message.caption
                mode.append("text")
            if message.forward_from_chat:
                mode.append("forward")
            if message.forward_from:
                mode.append("forward")

            textnorm = ''
            try:
                textnorm = self._Equivset(re.sub(self.CMD_TEST_RULE, '', text))
                # EC.log("[spam_ban] Equivset ok {}".format(text2))
            except Exception:
                # EC.log("[spam_ban] Equivset fail {}".format(text))
                EC.log(traceback.format_exc())

            self.textnorm = textnorm
            to_check_text = [text, textnorm]

            try:
                EC.cur.execute(
                    """SELECT SUM(`count`) AS `count` FROM `message_count` WHERE `user_id` = %s AND `type` = 'text'""", (self.user_id))
                rows = EC.cur.fetchall()
                if rows[0][0] is None:
                    user_msg_cnt = 0
                else:
                    user_msg_cnt = int(rows[0][0])

                if "text" in mode:
                    if user_msg_cnt <= 5:
                        if self.chat_id in self.ban_text_chat and self.check_regex(self.ban_text_regex, to_check_text):
                            self.action_all_in_one(self.chat_id, self.user_id, self.message_id, '宣傳文字')

                        elif self.chat_id in self.warn_text_chat and self.check_regex(self.warn_text_regex, to_check_text):
                            self.action_warn(self.message_id)

                        if self.chat_id in self.ban_youtube_link_chat:
                            m = re.search(
                                r'(https?://(youtu.be/|www.youtube.com/watch\?v=)[A-Za-z0-9\-]+)', text)
                            if m:
                                EC.log(
                                    '[spam_ban] find youtube link {}'.format(m.group(1)))
                                ythtml = requests.get(m.group(1)).text
                                if re.search(self.ban_youtube_link_regex, ythtml):
                                    self.action_all_in_one(self.chat_id, self.user_id, self.message_id, '傳送特定YouTube頻道連結')

                    if self.chat_id in self.test_chat and re.search(self.CMD_TEST_RULE, text):
                        text1 = re.sub(self.CMD_TEST_RULE, '', text)
                        text2 = self._Equivset(text1)
                        to_check_text = [text1, text2]
                        self.EC.cur.execute(
                            """SELECT `key`, `value` FROM `group_setting` WHERE `key` LIKE %s""",
                            ('spam_ban_regex_%'))
                        all_rules = self.EC.cur.fetchall()
                        rows = []
                        for row in all_rules:
                            if self.check_regex(row[1], to_check_text):
                                rows.append(row)
                        response = '測試文字：{} 正規化文字：{}\n'.format(text1, text2)
                        if rows:
                            response += '符合以下規則：\n'
                            for row in rows:
                                response += '{} （{}）\n'.format(row[1], row[0].replace('spam_ban_regex_', ''))
                        else:
                            response += '查無符合規則'

                        EC.log("[spam_ban] test result: {}".format(response))
                        EC.sendmessage(response, reply=self.message_id, parse_mode="")

                # Check username every time
                if user_msg_cnt <= 5:
                    if self.chat_id in self.ban_username_chat and self.check_regex(self.ban_username_regex, to_check_text):
                        self.action_all_in_one(self.chat_id, self.user_id, self.message_id, '宣傳性用戶名')

                    elif self.chat_id in self.warn_username_chat and self.check_regex(self.warn_username_regex, to_check_text):
                        self.action_warn(self.message_id)

                if "photo" in mode:
                    if self.chat_id in self.ban_photo_chat:
                        if user_msg_cnt <= 5:
                            self.action_all_in_one(self.chat_id, self.user_id, self.message_id, '發送圖片')

                if "forward" in mode and not self.message_deleted:
                    if user_msg_cnt <= 5:
                        EC.sendmessage(
                            'https://t.me/{}/{}'.format(
                                message["chat"]["username"],
                                self.message_id,
                            ),
                            chat_id=self.warn_forward_chat_id,
                            parse_mode="HTML"
                        )
                        EC.sendmessage(
                            '/global_ban {}'.format(
                                self.user_id,
                            ),
                            chat_id=self.warn_forward_chat_id,
                            parse_mode="HTML"
                        )
                        EC.log("[spam_ban] forward {}".format(
                            json.dumps(message)))
                        if ("forward_from_chat" in message and self.chat_id in self.warn_forward_chat
                                and message["forward_from_message_id"] < self.warn_forward_new_chat_limit):
                            self.action_warn(self.message_id)

            except Exception:
                traceback.print_exc()
                EC.log("[spam_ban] " + traceback.format_exc())

    def handle_cmd(self, action, cmd):
        if self.chat_id in self.global_ban_chat + self.global_ban_cmd_chat:
            if re.search(self.CMD_GLOBALBAN, action):
                self.cmd_globalban(action, cmd)

            if re.search(self.CMD_SINGLEBAN, action):
                self.cmd_globalban(action, cmd, self.chat_id)

            if re.search(self.CMD_GLOBALUNBAN, action):
                self.cmd_globalunban(action, cmd)

            if re.search(self.CMD_GLOBALRESTRICT, action):
                self.cmd_globalrestrict(action, cmd)

            if re.search(self.CMD_GLOBALUNRESTRICT, action):
                self.cmd_globalunrestrict(action, cmd)

            if re.search(self.CMD_GRANT, action):
                self.cmd_grant()

            if re.search(self.CMD_REVOKE, action):
                self.cmd_revoke()

            if re.search(self.CMD_ADD_RULE_BAN_TEXT, action):
                self.cmd_add_rule(action, cmd, self.SETTING_REGEX_BAN_TEXT)

            if re.search(self.CMD_ADD_RULE_BAN_USERNAME, action):
                self.cmd_add_rule(action, cmd, self.SETTING_REGEX_BAN_USERNAME)

            if re.search(self.CMD_ADD_RULE_WARN_TEXT, action):
                self.cmd_add_rule(action, cmd, self.SETTING_REGEX_WARN_TEXT)

            if re.search(self.CMD_ADD_RULE_WARN_USERNAME, action):
                self.cmd_add_rule(action, cmd, self.SETTING_REGEX_WARN_USERNAME)

            if re.search(self.CMD_REMOVE_RULE_BAN_TEXT, action):
                self.cmd_remove_rule(action, cmd, self.SETTING_REGEX_BAN_TEXT)

            if re.search(self.CMD_REMOVE_RULE_BAN_USERNAME, action):
                self.cmd_remove_rule(action, cmd, self.SETTING_REGEX_BAN_USERNAME)

            if re.search(self.CMD_REMOVE_RULE_WARN_TEXT, action):
                self.cmd_remove_rule(action, cmd, self.SETTING_REGEX_WARN_TEXT)

            if re.search(self.CMD_REMOVE_RULE_WARN_USERNAME, action):
                self.cmd_remove_rule(action, cmd, self.SETTING_REGEX_WARN_USERNAME)

        if re.search(self.CMD_ENABLE_BAN_TEXT, action):
            self.cmd_setting_enable(self.SETTING_BAN_TEXT)

        if re.search(self.CMD_ENABLE_BAN_USERNAME, action):
            self.cmd_setting_enable(self.SETTING_BAN_USERNAME)

        if re.search(self.CMD_ENABLE_WARN_TEXT, action):
            self.cmd_setting_enable(self.SETTING_WARN_TEXT)

        if re.search(self.CMD_ENABLE_WARN_USERNAME, action):
            self.cmd_setting_enable(self.SETTING_WARN_USERNAME)

        if re.search(self.CMD_ENABLE_BAN_YOUTUBE_LINK, action):
            self.cmd_setting_enable(self.SETTING_BAN_YOUTUBE_LINK)

        if re.search(self.CMD_ENABLE_WARN_FORWARD, action):
            self.cmd_setting_enable(self.SETTING_WARN_FORWARD)

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

        if re.search(self.CMD_DISABLE_BAN_YOUTUBE_LINK, action):
            self.cmd_setting_disable(self.SETTING_BAN_YOUTUBE_LINK)

        if re.search(self.CMD_DISABLE_WARN_FORWARD, action):
            self.cmd_setting_disable(self.SETTING_WARN_FORWARD)

        if re.search(self.CMD_DISABLE_GLOBALBAN, action):
            self.cmd_setting_disable(self.SETTING_GLOBAL_BAN)

    def cmd_globalban(self, action, cmd, single=None):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GLOBALBAN, 0):
            self.EC.log(
                '[spam_ban] {} /globalban no premission'.format(self.user_id))
            self.EC.sendmessage('你沒有權限進行全域封鎖的動作', reply=self.message_id)
            return

        parser = argparse.ArgumentParser(prog='/{0}'.format(action))
        parser.add_argument(
            'user', type=str, default=None, nargs='?', help='欲封鎖用戶ID，不指定時需回覆訊息')
        parser.add_argument(
            '-d', type=str, metavar='時長',
            help='接受單位為秒的整數，或是<整數><單位>的格式，例如：60s, 1min, 2h, 3d, 4w, 5m，永久為inf。預設：{}，有給-r參數時為inf'.format(self.DEFAULT_DURATION)
        )
        parser.add_argument(
            '-r', type=str, metavar='原因',
            help='預設：{}'.format(self.DEFAULT_REASON)
        )
        parser.add_argument('--delete', action='store_true', default=False, help='要刪除訊息，無提供原因預設此項')
        parser.add_argument('--no-del', action='store_true', default=False, help='不刪除訊息，有提供原因預設此項')
        parser.add_argument('--no-ban', action='store_true', default=False, help='不進行封鎖')
        parser.add_argument('--dry-run', action='store_true', default=False, help='在日誌記錄但不執行任何操作')
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
        duration = args.d
        is_del = True
        if reason is None:
            reason = self.DEFAULT_REASON
        else:
            if duration is None:
                duration = 'inf'
            is_del = False
        if duration is None:
            duration = self.DEFAULT_DURATION
        if args.delete:
            is_del = True
        elif args.no_del:
            is_del = False

        duration = self.parse_duration(duration)
        if duration is None:
            self.EC.sendmessage('指定的時長無效', reply=self.message_id)
            return
        if duration > 0 and (duration < 30 or duration > 31622400):
            self.EC.sendmessage('時長不可小於30秒或大於366天，否則請指定為永久', reply=self.message_id)
            return

        if ban_user_id == self.EC.bot.id:
            self.EC.sendmessage('你不能對機器人執行此操作', reply=self.message_id)
            return

        if self.is_reply:
            self.EC.deletemessage(self.chat_id, self.update.message.reply_to_message.message_id)
        self.EC.deletemessage(self.chat_id, self.message_id)
        successed = 0
        failed = 0
        if args.dry_run:
            failed = len(self.global_ban_chat)
            error = ''
            reason += ' (dry run)'
        else:
            if not args.no_ban:
                if single is None:
                    successed, failed, error = self.action_ban_all_chat(ban_user_id, duration)
                else:
                    ok, error = self.action_ban_a_chat(ban_user_id, single, duration)
                    if ok:
                        successed += 1
                    else:
                        failed += 1
            else:
                failed = len(self.global_ban_chat)
                error = ''
            if is_del:
                self.action_del_all_msg(ban_user_id)
        self.action_log_admin(
            '#封', self.user_id,
            self.first_name,
            'banned', ban_user_id, reason,
            self.duration_text(duration),
            successed,
            failed,
            self.GROUP_SET if not single else str(single),
            error,
        )

    def cmd_globalunban(self, action, cmd):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GLOBALBAN, 0):
            self.EC.log(
                '[spam_ban] {} /globalunban no premission'.format(self.user_id))
            self.EC.sendmessage('你沒有權限進行全域解除封鎖的動作',
                                reply=self.message_id)
            return

        parser = argparse.ArgumentParser(prog='/{0}'.format(action))
        parser.add_argument(
            'user', type=str, default=None, nargs='?', help='欲解除封鎖用戶ID，不指定時需回覆訊息')
        parser.add_argument(
            '-r', type=str, metavar='原因', default='無原因', help='預設：%(default)s')
        parser.add_argument('--dry-run', action='store_true', default=False, help='在日誌記錄但不執行解除封鎖')
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

        self.EC.deletemessage(self.chat_id, self.message_id)
        if args.dry_run:
            failed = len(self.global_ban_chat)
            reason += ' (dry run)'
        else:
            successed, failed = self.action_unban_all_chat(ban_user_id)
        self.action_log_admin(
            '#解', self.user_id,
            self.first_name,
            'unbanned', ban_user_id, reason,
            self.duration_text(0),
            successed,
            failed,
            self.GROUP_SET,
        )

    def cmd_globalrestrict(self, action, cmd):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GLOBALBAN, 0):
            self.EC.log(
                '[spam_ban] {} /globalban no premission'.format(self.user_id))
            self.EC.sendmessage('你沒有權限進行全域禁言的動作', reply=self.message_id)
            return

        parser = argparse.ArgumentParser(prog='/{0}'.format(action))
        parser.add_argument(
            'user', type=str, default=None, nargs='?', help='欲禁言用戶ID，不指定時需回覆訊息')
        parser.add_argument('-d', type=str, metavar='時長', default='1w',
                            help='接受單位為秒的整數，或是<整數><單位>的格式，例如：60s, 1min, 2h, 3d, 4w, 5m，永久為inf。預設：%(default)s')
        parser.add_argument(
            '-r', type=str, metavar='原因', default='未提供理由', help='預設：%(default)s')
        parser.add_argument('-s', type=str, metavar='群組集合', default=self.GROUP_SET,
                            help='執行禁言的群組集合，預設：%(default)s')
        parser.add_argument('--dry-run', action='store_true', default=False, help='在日誌記錄但不執行禁言')
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
        if duration > 0 and (duration < 30 or duration > 31622400):
            self.EC.sendmessage('時長不可小於30秒或大於366天，否則請指定為永久', reply=self.message_id)
            return

        if ban_user_id == self.EC.bot.id:
            self.EC.sendmessage('你不能對機器人執行此操作', reply=self.message_id)
            return

        group_set = args.s
        if group_set == self.GROUP_SET:
            run_chats = self.global_ban_chat
        else:
            run_chats = []
            self.EC.cur.execute("""SELECT `chat_id` FROM `group_setting` WHERE `key` = 'group_set' AND `value` = %s""",
                                (group_set))
            rows = self.EC.cur.fetchall()
            for row in rows:
                run_chats.append(int(row[0]))

        if len(run_chats) == 0:
            self.EC.sendmessage('找不到執行的群組集合 {}'.format(group_set), reply=self.message_id)
            return

        self.EC.deletemessage(self.chat_id, self.message_id)
        if args.dry_run:
            failed = len(run_chats)
            reason += ' (dry run)'
        else:
            successed, failed = self.action_restrict_all_chat(ban_user_id, duration, run_chats)
        self.action_log_admin(
            '#禁言', self.user_id,
            self.first_name,
            'restricted', ban_user_id, reason,
            self.duration_text(duration),
            successed,
            failed,
            group_set,
        )

    def cmd_globalunrestrict(self, action, cmd):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_GLOBALBAN, 0):
            self.EC.log(
                '[spam_ban] {} /globalunban no premission'.format(self.user_id))
            self.EC.sendmessage('你沒有權限進行全域解除禁言的動作',
                                reply=self.message_id)
            return

        parser = argparse.ArgumentParser(prog='/{0}'.format(action))
        parser.add_argument(
            'user', type=str, default=None, nargs='?', help='欲解除禁言用戶ID，不指定時需回覆訊息')
        parser.add_argument(
            '-r', type=str, metavar='原因', default='無原因', help='預設：%(default)s')
        parser.add_argument('-s', type=str, metavar='群組集合', default=self.GROUP_SET,
                            help='執行禁言的群組集合，預設：%(default)s')
        parser.add_argument('--dry-run', action='store_true', default=False, help='在日誌記錄但不執行解除禁言')
        ok, args = self.EC.parse_command(parser, cmd)

        if not ok:
            self.EC.sendmessage(args, reply=self.message_id, parse_mode='')
            return

        ban_user_id = args.user
        if ban_user_id is None and self.is_reply:
            ban_user_id = self.reply_to_user_id
        if ban_user_id is None:
            self.EC.sendmessage('需要回覆訊息或用參數指定解除禁言目標', reply=self.message_id)
            return

        ban_user_id = int(ban_user_id)
        reason = args.r

        if ban_user_id == self.EC.bot.id:
            self.EC.sendmessage('你不能對機器人執行此操作', reply=self.message_id)
            return

        group_set = args.s
        if group_set == self.GROUP_SET:
            run_chats = self.global_ban_chat
        else:
            run_chats = []
            self.EC.cur.execute("""SELECT `chat_id` FROM `group_setting` WHERE `key` = 'group_set' AND `value` = %s""",
                                (group_set))
            rows = self.EC.cur.fetchall()
            for row in rows:
                run_chats.append(int(row[0]))

        self.EC.deletemessage(self.chat_id, self.message_id)
        if args.dry_run:
            failed = len(group_set)
            reason += ' (dry run)'
        else:
            successed, failed = self.action_unrestrict_all_chat(ban_user_id, run_chats)
        self.action_log_admin(
            '#解', self.user_id,
            self.first_name,
            'unrestricted', ban_user_id, reason,
            self.duration_text(0),
            successed,
            failed,
            group_set,
        )

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
            self._load_setting_from_database()
        else:
            self.EC.add_group_setting(self.chat_id, setting, 'enable')
            self.EC.sendmessage('本群已啟用 {}'.format(setting),
                                reply=self.message_id,
                                parse_mode='')

    def cmd_setting_disable(self, setting):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_SETTING, 0):
            self.EC.sendmessage('你沒有權限變更自動封鎖設定', reply=self.message_id)
            return

        rows = self.EC.list_setting_in_group(self.chat_id, setting)
        if rows:
            self.EC.remove_group_setting(self.chat_id, setting)
            self.EC.sendmessage('本群已停用 {}'.format(setting),
                                reply=self.message_id,
                                parse_mode='')
            self._load_setting_from_database()
        else:
            self.EC.sendmessage('本群並未啟用 {}'.format(setting),
                                reply=self.message_id,
                                parse_mode='')

    def cmd_add_rule(self, action, cmd, rule_type):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_RULE, 0):
            self.EC.log(
                '[spam_ban] {} /{} no premission'.format(self.user_id, action))
            self.EC.sendmessage('你沒有權限進行變更廣告規則的動作',
                                reply=self.message_id)
            return

        parser = argparse.ArgumentParser(prog='/{0}'.format(action))
        parser.add_argument('rule', type=str, help='規則的正規表達式')
        parser.add_argument('-f', action='store_true', dest='force', help='無視警告強制加入此規則')
        parser.set_defaults(force=False)
        ok, args = self.EC.parse_command(parser, cmd)

        if not ok:
            self.EC.sendmessage(args, reply=self.message_id, parse_mode='')
            return

        rule = args.rule
        force = args.force

        self.EC.cur.execute(
            """SELECT COUNT(*) FROM (SELECT * FROM `message` ORDER BY `date` DESC LIMIT %s) temp WHERE `text` REGEXP %s""",
            (self.TEST_LIMIT, rule))
        count = int(self.EC.cur.fetchone()[0])
        rate = count / self.TEST_LIMIT

        if rate > self.RATE_LIMIT_DISALLOW:
            self.EC.sendmessage(
                '該規則在最近的{}則訊息中觸發了{}次（{}%），超過了{}%的限制，因此禁止加入該規則'.format(
                    self.TEST_LIMIT, count, rate * 100, self.RATE_LIMIT_DISALLOW * 100),
                reply=self.message_id, parse_mode='')
            return

        message_append = ''
        if rate > self.RATE_LIMIT_WARN:
            if force:
                message_append = '\n警告：該規則在最近的{0}則訊息中觸發了{1:.1f}次（{2:.1f}%）'.format(
                    self.TEST_LIMIT, count, rate * 100)
            else:
                self.EC.sendmessage(
                    '該規則在最近的{0}則訊息中觸發了{1}次（{2:.1f}%），超過了{3:.1f}%的限制，若確定要加入該規則，請加入 -f 參數再試一次'.format(
                        self.TEST_LIMIT, count, rate * 100, self.RATE_LIMIT_WARN * 100),
                    reply=self.message_id, parse_mode='')
                return

        is_dup = self.EC.list_setting_in_group(0, rule_type, rule)
        if is_dup:
            self.EC.sendmessage('{}規則 {} 已存在{}'
                                .format(rule_type.replace('spam_ban_regex_', ''), rule, message_append),
                                reply=self.message_id,
                                parse_mode='')
            return

        ok = self.EC.add_group_setting(0, rule_type, rule, check_dup=True)
        if ok:
            self.EC.sendmessage('成功加入{}規則 {}{}'
                                .format(rule_type.replace('spam_ban_regex_', ''), rule, message_append),
                                reply=self.message_id,
                                parse_mode='')
            self._load_setting_from_database()
        else:
            self.EC.sendmessage('加入{}規則 {} 失敗{}'
                                .format(rule_type.replace('spam_ban_regex_', ''), rule, message_append),
                                reply=self.message_id,
                                parse_mode='')

    def cmd_remove_rule(self, action, cmd, rule_type):
        if not self.EC.check_permission(self.user_id, self.PERMISSION_RULE, 0):
            self.EC.log(
                '[spam_ban] {} /{} no premission'.format(self.user_id, action))
            self.EC.sendmessage('你沒有權限進行變更廣告規則的動作',
                                reply=self.message_id)
            return

        parser = argparse.ArgumentParser(prog='/{0}'.format(action))
        parser.add_argument(
            'rule', type=str, help='規則的正規表達式')
        ok, args = self.EC.parse_command(parser, cmd)

        if not ok:
            self.EC.sendmessage(args, reply=self.message_id, parse_mode='')
            return

        rule = args.rule

        ok = self.EC.remove_group_setting(0, rule_type, rule)
        if ok:
            self.EC.sendmessage('成功移除{}規則 {}'
                                .format(rule_type.replace('spam_ban_regex_', ''), rule),
                                reply=self.message_id,
                                parse_mode='')
            self._load_setting_from_database()
        else:
            self.EC.sendmessage('移除{}規則 {} 失敗，可能是因為無此規則'
                                .format(rule_type.replace('spam_ban_regex_', ''), rule),
                                reply=self.message_id,
                                parse_mode='')

    # action list start
    def action_ban_a_chat(self, user_id, ban_chat_id, duration=604800):
        until_date = int(time.time() + duration)
        try:
            self.EC.bot_by_chat(ban_chat_id).ban_chat_member(
                chat_id=ban_chat_id, user_id=user_id, until_date=until_date)
        except Exception as e:
            self.EC.log('[spam_ban] ban {} in {} failed: {}'.format(
                user_id, ban_chat_id, e))
            return False, str(e)
        return True, None

    def action_ban_all_chat(self, user_id, duration=604800):
        self.EC.log("[spam_ban] ban {} in {}".format(
            user_id, ", ".join(map(str, self.global_ban_chat))))
        successed = 0
        failed = 0
        error = set()
        for ban_chat_id in self.global_ban_chat:
            ok, msg = self.action_ban_a_chat(user_id, ban_chat_id, duration=duration)
            if ok:
                successed += 1
            else:
                failed += 1
                error.add(msg)
        return successed, failed, '、'.join(error)

    def action_unban_all_chat(self, user_id):
        self.EC.log("[spam_ban] unban {} in {}".format(
            user_id, ", ".join(map(str, self.global_ban_chat))))
        successed = 0
        failed = 0
        for ban_chat_id in self.global_ban_chat:
            try:
                self.EC.bot_by_chat(ban_chat_id).unban_chat_member(
                    chat_id=ban_chat_id, user_id=user_id)
                successed += 1
            except Exception as e:
                self.EC.log('[spam_ban] unban {} in {} failed: {}'.format(
                    user_id, ban_chat_id, e))
                failed += 1
        return successed, failed

    def action_restrict_all_chat(self, user_id, duration, run_chats):
        self.EC.log("[spam_ban] ban {} in {}".format(
            user_id, ", ".join(map(str, run_chats))))
        until_date = int(time.time() + duration)
        successed = 0
        failed = 0
        for ban_chat_id in run_chats:
            try:
                self.EC.bot_by_chat(ban_chat_id).restrict_chat_member(
                    chat_id=ban_chat_id, user_id=user_id, until_date=until_date)
                successed += 1
            except telegram.error.BadRequest as e:
                self.EC.log('[spam_ban] restrict {} in {} failed: {}'.format(
                    user_id, ban_chat_id, e.message))
                failed += 1
        return successed, failed

    def action_unrestrict_all_chat(self, user_id, run_chats):
        self.EC.log("[spam_ban] unrestrict {} in {}".format(
            user_id, ", ".join(map(str, run_chats))))
        successed = 0
        failed = 0
        for ban_chat_id in run_chats:
            try:
                self.EC.bot_by_chat(ban_chat_id).restrict_chat_member(
                    chat_id=ban_chat_id, user_id=user_id,
                    can_send_messages=True, can_send_media_messages=True,
                    can_send_other_messages=True, can_add_web_page_previews=True)
                successed += 1
            except telegram.error.BadRequest as e:
                self.EC.log('[spam_ban] unrestrict {} in {} failed: {}'.format(
                    user_id, ban_chat_id, e.message))
                failed += 1
        return successed, failed

    def action_del_all_msg(self, user_id):
        self.message_deleted = True

        date_limit = int(time.time() - self.delete_limit)
        self.EC.cur.execute(
            """SELECT `chat_id`, `message_id`, `type` FROM `message` WHERE `user_id` = %s AND `date` > %s""",
            (user_id, date_limit)
        )
        rows = self.EC.cur.fetchall()
        self.EC.log('[spam_ban] find {} messages from {} after {} to delete'.format(len(rows), user_id, date_limit))
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

    def action_log_admin(self, hashtag, admin_user_id, admin_name, action, ban_user_id, reason, duration, successed, failed, group_set, error=''):
        message = '{0} <a href="tg://user?id={1}">{2}</a>{9} {3} <a href="tg://user?id={4}">{4}</a> 期限為{6}，於{10} {7}成功，{8}失敗\n理由：{5}{11}'.format(
            hashtag,
            admin_user_id,
            admin_name,
            action,
            ban_user_id,
            reason,
            duration,
            successed,
            failed,
            self._log_format_chat_title(),
            group_set,
            '\n錯誤：{}'.format(error) if error else '',
        )
        self.EC.log("[spam_ban] message {}".format(message))
        self.EC.sendmessage(chat_id=self.log_chat_id,
                            message=message, parse_mode="HTML")

    def action_log_bot(self, ban_user_id, reason, duration, successed, failed, error):
        message = '#封 #自動 ECbot{0} banned <a href="tg://user?id={1}">{1}</a> 期限為{3}，{4}成功，{5}失敗\n理由：{2}{6}'.format(
            self._log_format_chat_title(),
            ban_user_id,
            reason,
            duration,
            successed,
            failed,
            '\n錯誤：{}'.format(error) if error else '',
        )
        self.EC.log("[spam_ban] message {}".format(message))
        self.EC.sendmessage(chat_id=self.log_chat_id,
                            message=message, parse_mode="HTML")

    def action_all_in_one(self, chat_id, user_id, message_id, reason):
        duration = self.parse_duration(self.AUTO_DURATION)

        self.EC.deletemessage(chat_id, message_id)
        single_ban_ok = None
        if chat_id not in self.global_ban_chat:
            single_ban_ok = self.action_ban_a_chat(user_id, chat_id, duration)
        successed, failed, error = self.action_ban_all_chat(user_id, duration)
        if single_ban_ok is not None:
            if single_ban_ok:
                successed += 1
            else:
                failed += 1
        self.action_del_all_msg(user_id)
        self.action_log_bot(user_id, reason, self.duration_text(duration), successed, failed, error)

    def _log_format_chat_title(self):
        if self.chat_id in self.global_ban_chat:
            if self.EC.update.effective_chat.link:
                return '(from <a href="{0}">{1}</a>)'.format(
                    self.EC.update.effective_chat.link, self.EC.get_group_name(self.chat_id))
            else:
                return '(from {})'.format(
                    self.EC.get_group_name(self.chat_id))
        return ''
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

    def check_regex(self, regex, texts):
        for text in texts:
            if text.strip() != '' and re.search(regex, text, flags=re.I | re.S):
                return True
        return False
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
            <td>ban_youtube_link</td>
            <td>ban_photo</td>
            <td>warn_forward</td>
            <td>global_ban</td>
            <td>global_ban_cmd</td>
            </tr>
            """

        chat_ids = list(set(self.ban_username_chat + self.warn_username_chat + self.ban_text_chat
                            + self.warn_text_chat + self.ban_youtube_link_chat + self.ban_photo_chat
                            + self.warn_forward_chat + self.global_ban_chat + self.global_ban_cmd_chat))
        chats = [(
            chat_id,
            (self.group_name[chat_id] or '') if chat_id in self.group_name else '',
            (self.group_username[chat_id] or '') if chat_id in self.group_username else '',
        ) for chat_id in chat_ids]
        chats.sort(key=lambda v: v[1])

        hidden_chats = [row[0] for row in EC.list_group_with_setting('group_set', 'hidden')]
        for chat in chats:
            if chat[0] in hidden_chats:
                continue
            title = chat[1] if chat[0] < 0 else str(chat[0])
            temp += '<tr>'
            temp += '<td><span title="{}">{}</span></td>'.format(chat[0], title)
            for chat_setting in [self.ban_text_chat, self.ban_username_chat,
                                 self.warn_text_chat, self.warn_username_chat,
                                 self.ban_youtube_link_chat, self.ban_photo_chat,
                                 self.warn_forward_chat, self.global_ban_chat,
                                 self.global_ban_cmd_chat]:
                temp += '<td>'
                if chat[0] in chat_setting:
                    temp += '&#10003;'
                temp += '</td>'
            temp += '</tr>'
        temp += '</table>'

        html += '<tr><td>chats</td><td>{}</td></td>'.format(temp)

        html += '<tr><td>ban_text_regex</td><td style="white-space: pre-wrap;">{}</td></td>'.format(
            self.ban_text_regex)

        html += '<tr><td>ban_username_regex</td><td style="white-space: pre-wrap;">{}</td></td>'.format(
            self.ban_username_regex)

        html += '<tr><td>warn_text_regex</td><td style="white-space: pre-wrap;">{}</td></td>'.format(
            self.warn_text_regex)

        html += '<tr><td>warn_username_regex</td><td style="white-space: pre-wrap;">{}</td></td>'.format(
            self.warn_username_regex)

        html += "<tr><td>warn_text</td><td>{}</td></td>".format(self.warn_text)

        html += "<tr><td>ban_youtube_link_regex</td><td>{}</td></td>".format(
            self.ban_youtube_link_regex)

        html += '<tr><td>admin</td><td>'

        users = EC.list_users_with_permission(self.PERMISSION_GLOBALBAN)
        html += 'Ban users<ul>'
        for user in users:
            html += '<li>{}</li>'.format(EC.get_user_fullname(user))
        html += '</ul>'

        users = EC.list_users_with_permission(self.PERMISSION_GRANT)
        html += 'Grant "Ban" permission<ul>'
        for user in users:
            html += '<li>{}</li>'.format(EC.get_user_fullname(user))
        html += '</ul>'

        users = EC.list_users_with_permission(self.PERMISSION_SETTING)
        html += 'Adjust group settings<ul>'
        for user in users:
            html += '<li>{}</li>'.format(EC.get_user_fullname(user))
        html += '</ul>'

        users = EC.list_users_with_permission(self.PERMISSION_RULE)
        html += 'Adjust spam rules<ul>'
        for user in users:
            html += '<li>{}</li>'.format(EC.get_user_fullname(user))
        html += '</ul>'

        html += '</td></td>'

        html += "<tr><td>log_chat_id</td><td>{}</td></td>".format(
            self.log_chat_id)
        html += "<tr><td>delete_limit</td><td>{}</td></td>".format(
            self.delete_limit)

        return html

    def _Equivset(self, string):
        path = os.path.dirname(os.path.realpath(__file__))
        ps = subprocess.Popen(['php', '{}/Equivset.php'.format(path)],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        res = ps.communicate(string.encode())[0].decode()
        return res


def __mainclass__():
    return Spam_ban
