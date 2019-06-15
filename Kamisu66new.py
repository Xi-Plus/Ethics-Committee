# -*- coding: utf-8 -*-
import contextlib
import io
import shlex
import time

import pymysql
from telethon import TelegramClient


class EthicsCommittee(TelegramClient):
    def __init__(self):
        from config_variable import cfg  # pylint: disable=E0401
        TelegramClient.__init__(self, 'bot', cfg['telegram']['api_id'], cfg['telegram']['api_hash'])
        self.token = cfg['telegram']['token']
        self.url = cfg['telegram']['url']
        self.max_connections = cfg['telegram']['max_connections']
        self.db = pymysql.connect(host=cfg['database']['host'],
                                  user=cfg['database']['user'],
                                  passwd=cfg['database']['passwd'],
                                  db=cfg['database']['db'],
                                  charset=cfg['database']['charset'])
        self.cur = self.db.cursor()

    # override
    def start(self):
        return super().start(bot_token=self.token)

    # override
    async def send_message(self, *args, **kwargs):
        message = await super().send_message(*args, **kwargs)
        print(message)
        self.addmessage(
            user_id=message.sender_id,
            message_id=message.id,
            full_name=message.sender.first_name,
            msg_type='text',
            text=message.message,
            date=message.date.timestamp(),
            reply_to_message_id=message.reply_to_msg_id,
            reply_to_user_id=0,
            chat_id=message.chat_id,
        )

    # override end

    def addmessage(self, user_id, message_id, full_name, msg_type, text, date, reply_to_message_id, reply_to_user_id, chat_id=None):
        if chat_id is None:
            chat_id = self.chat_id
        self.cur.execute("""INSERT INTO `message` (`chat_id`, `user_id`, `message_id`, `full_name`, `type`, `text`, `date`, `reply_to_message_id`, `reply_to_user_id`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                         (str(chat_id), str(user_id), str(message_id), full_name, msg_type, text, str(date), reply_to_message_id, reply_to_user_id))
        self.db.commit()

    def parse_command(self, parser, cmd, ignore_first=False):
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        elif isinstance(cmd, list):
            pass
        else:
            raise TypeError('cmd not a str or list')

        if ignore_first:
            cmd = cmd[1:]

        with io.StringIO() as buf, contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                args = parser.parse_args(cmd)
            except SystemExit:
                output = buf.getvalue()
                return False, output
            else:
                return True, args

    def add_permission(self, user_id, user_right, chat_id=None):
        if chat_id is None:
            chat_id = self.chat_id

        res = self.cur.execute("""INSERT IGNORE INTO `permissions` (`chat_id`, `user_id`, `user_right`)
                                  VALUES (%s, %s, %s)""",
                               (chat_id, user_id, user_right))
        self.db.commit()
        if res == 0:
            return False
        return True

    def remove_permission(self, user_id, user_right, chat_id=None):
        if chat_id is None:
            chat_id = self.chat_id

        res = self.cur.execute("""DELETE FROM `permissions` WHERE `chat_id` = %s
                                  AND `user_id` = %s AND `user_right` = %s""",
                               (chat_id, user_id, user_right))
        self.db.commit()
        if res == 0:
            return False
        return True

    def check_permission(self, user_id, user_right, chat_id=None):
        if chat_id is None:
            chat_id = 0
        self.cur.execute("""SELECT 'true' FROM `permissions` WHERE `user_id` = %s AND `user_right` = %s AND `chat_id` = %s""",
                         (user_id, user_right, chat_id))
        rows = self.cur.fetchall()
        return len(rows) > 0

    def list_users_with_permission(self, user_right, chat_id=None):
        if chat_id is None:
            self.cur.execute("""SELECT `user_id` FROM `permissions` WHERE `user_right` = %s""",
                             (user_right))
        else:
            self.cur.execute("""SELECT 'user_id' FROM `permissions` WHERE `user_right` = %s AND `chat_id` = %s""",
                             (user_right, chat_id))
        rows = self.cur.fetchall()
        return [row[0] for row in rows]

    def add_group_setting(self, chat_id, key, value='', check_dup=False):
        if check_dup:
            rows = self.list_setting_in_group(chat_id, key, value)
            if rows:
                return True

        res = self.cur.execute("""INSERT INTO `group_setting` (`chat_id`, `key`, `value`)
                                  VALUES (%s, %s, %s)""",
                               (chat_id, key, value))
        self.db.commit()
        if res == 0:
            return False
        return True

    def remove_group_setting(self, chat_id, key, value=None):
        if value is None:
            res = self.cur.execute("""DELETE FROM `group_setting` WHERE `chat_id` = %s
                                    AND `key` = %s""",
                                   (chat_id, key))
        else:
            res = self.cur.execute("""DELETE FROM `group_setting` WHERE `chat_id` = %s
                                    AND `key` = %s AND `value` = %s""",
                                   (chat_id, key, value))
        self.db.commit()
        if res == 0:
            return False
        return True

    def list_setting_in_group(self, chat_id, key, value=None):
        if value is None:
            self.cur.execute(
                """SELECT `value` FROM `group_setting` WHERE `chat_id` = %s AND `key` = %s""",
                (chat_id, key))
        else:
            self.cur.execute(
                """SELECT `value` FROM `group_setting` WHERE `chat_id` = %s AND `key` = %s AND `value` = %s""",
                (chat_id, key, value))
        rows = self.cur.fetchall()
        return rows

    def list_group_with_setting(self, key, value=None):
        if value is None:
            self.cur.execute("""SELECT `chat_id`, `value` FROM `group_setting` WHERE `key` = %s""",
                             (key))
        else:
            self.cur.execute("""SELECT `chat_id`, `value` FROM `group_setting` WHERE `key` = %s AND `value` = %s""",
                             (key, value))
        rows = self.cur.fetchall()
        return rows

    def get_group_name(self, chat_id=None):
        if chat_id is None:
            chat_id = self.chat_id
        self.cur.execute("""SELECT `title` FROM `group_name` WHERE `chat_id` = %s""",
                         (chat_id))
        row = self.cur.fetchone()
        if row is None:
            return str(chat_id)
        return row[0]

    def addBotMessage(self, text, date=None):
        if date is None:
            date = int(time.time())
        self.addmessage(0, 0, '', 'log', text, date, '', '')

    def log(self, message):
        self.cur.execute("""INSERT INTO `log` (`chat_id`, `message`) VALUES (%s, %s)""",
                         (self.chat_id, str(message)))
        self.db.commit()

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()


class EthicsCommitteeExtension():
    EC = None

    def prepare(self, EC):
        self.EC = EC

    def main(self, EC=None):  # Compatible with the old version
        raise NotImplementedError

    def web(self):
        raise NotImplementedError


def load_extensions(name):
    import importlib
    import extensions  # pylint: disable=E0401,W0611
    return importlib.import_module('.' + name, 'extensions').__mainclass__()
