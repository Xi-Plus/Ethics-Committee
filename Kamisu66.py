# -*- coding: utf-8 -*-
import contextlib
import io
import json
import shlex
import time
import traceback
import urllib.parse
import urllib.request

import pymysql
import telegram


class EthicsCommittee:
    def __init__(self, chat_id=None, user_id=None, update=None):
        from config_variable import cfg  # pylint: disable=E0401
        self.token = cfg['telegram']['token']
        # self.bot = EthicsCommitteeTelegramBot(self.token)
        self.bot = telegram.Bot(self.token)
        self.botid = self.bot.id
        self.url = cfg['telegram']['url']
        self.max_connections = cfg['telegram']['max_connections']
        self.db = pymysql.connect(host=cfg['database']['host'],
                                  user=cfg['database']['user'],
                                  passwd=cfg['database']['passwd'],
                                  db=cfg['database']['db'],
                                  charset=cfg['database']['charset'])
        self.cur = self.db.cursor()
        if update is None:
            self.update = None
            self.chat_id = chat_id
            self.user_id = user_id
        else:
            self.data = update
            self.update = telegram.Update.de_json(update, self.bot)
            self.chat_id = self.update.effective_chat.id
            if self.update.effective_user is not None:
                self.user_id = self.update.effective_user.id

    def sendmessage(self, message, parse_mode="Markdown", reply=False, reply_markup=None, chat_id=None):
        try:
            query = {}
            query["chat_id"] = self.chat_id
            if chat_id is not None:
                query["chat_id"] = chat_id
            if parse_mode != "":
                query["parse_mode"] = parse_mode
            if isinstance(reply, (str, int)):
                query["reply_to_message_id"] = reply
            if reply_markup is not None:
                query["reply_markup"] = reply_markup
            query["disable_web_page_preview"] = 1
            query["text"] = message

            query = urllib.parse.urlencode(query)
            url = "https://api.telegram.org/bot" + self.token + "/sendMessage?" + query
            res = urllib.request.urlopen(url).read().decode("utf8")
            res = json.loads(res)
            if res["ok"]:
                from_first_name = ""
                if "from" in res["result"]:
                    from_first_name = res["result"]["from"]["first_name"]
                reply_to_message_id = 0
                reply_to_user_id = 0
                if "reply_to_message" in res["result"]:
                    reply_to_message_id = res["result"]["reply_to_message"]["message_id"]
                    reply_to_user_id = res["result"]["reply_to_message"]["from"]["id"]
                self.addmessage(self.botid, res["result"]["message_id"], from_first_name, "text",
                                res["result"]["text"], res["result"]["date"], reply_to_message_id, reply_to_user_id)
            return res
        except urllib.error.HTTPError as e:
            res = e.read().decode("utf8")
            self.log("send msg error: code={} res={}".format(e.code, res))
            self.log(traceback.format_exc())
            return json.loads(res)
        except Exception as e:
            self.log(traceback.format_exc())
            return None

    def sendSticker(self, sticker, reply=False, chat_id=None):
        try:
            query = {}
            query["chat_id"] = self.chat_id
            if chat_id is not None:
                query["chat_id"] = chat_id
            if isinstance(reply, (str, int)):
                query["reply_to_message_id"] = reply
            query["sticker"] = sticker

            query = urllib.parse.urlencode(query)
            url = "https://api.telegram.org/bot" + self.token + "/sendSticker?" + query
            res = urllib.request.urlopen(url).read().decode("utf8")
            res = json.loads(res)
            if res["ok"]:
                from_first_name = ""
                if "from" in res["result"]:
                    from_first_name = res["result"]["from"]["first_name"]
                reply_to_message_id = 0
                reply_to_user_id = 0
                if "reply_to_message" in res["result"]:
                    reply_to_message_id = res["result"]["reply_to_message"]["message_id"]
                    reply_to_user_id = res["result"]["reply_to_message"]["from"]["id"]
                self.addmessage(self.botid, res["result"]["message_id"], from_first_name, "sticker", res["result"]
                                ["sticker"]["file_id"], res["result"]["date"], reply_to_message_id, reply_to_user_id)
        except urllib.error.HTTPError as e:
            self.log("send msg error: code={} res={}".format(
                e.code, e.read().decode("utf8")))
            self.log(traceback.format_exc())
        except Exception as e:
            self.log(traceback.format_exc())

    def sendChatAction(self, action='typing', chat_id=None):
        try:
            query = {}
            query["chat_id"] = self.chat_id
            if chat_id is not None:
                query["chat_id"] = chat_id
            query["action"] = action

            query = urllib.parse.urlencode(query)
            url = "https://api.telegram.org/bot" + self.token + "/sendChatAction?" + query
            urllib.request.urlopen(url).read().decode("utf8")
        except urllib.error.HTTPError as e:
            self.log("send msg error: code={} res={}".format(
                e.code, e.read().decode("utf8")))
            self.log(traceback.format_exc())
        except Exception as e:
            self.log(traceback.format_exc())

    def editmessage(self, message_id, message, parse_mode="Markdown", reply_markup=None, chat_id=None):
        try:
            query = {}
            query["chat_id"] = self.chat_id
            if chat_id is not None:
                query["chat_id"] = chat_id
            if parse_mode != "":
                query["parse_mode"] = parse_mode
            if reply_markup is not None:
                query["reply_markup"] = reply_markup
            query["disable_web_page_preview"] = 1
            query["message_id"] = message_id
            query["text"] = message

            query = urllib.parse.urlencode(query)
            url = "https://api.telegram.org/bot" + self.token + "/editMessageText?" + query
            res = urllib.request.urlopen(url).read().decode("utf8")
            res = json.loads(res)
            return res
        except urllib.error.HTTPError as e:
            res = e.read().decode("utf8")
            self.log("edit msg error: code={} res={}".format(e.code, res))
            self.log(traceback.format_exc())
            return json.loads(res)
        except Exception as e:
            self.log(traceback.format_exc())
            return None

    def deletemessage(self, chat_id, message_id):
        try:
            self.cur.execute("""UPDATE `message` SET `deleted` = 1 WHERE `chat_id` = %s AND `message_id` = %s""",
                             (chat_id, message_id))
            self.db.commit()
            if message_id > 0:
                url = "https://api.telegram.org/bot{}/deleteMessage?chat_id={}&message_id={}".format(
                    self.token, chat_id, message_id)
                urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            datastr = e.read().decode("utf8")
            data = json.loads(datastr)
            if data["description"] == "Bad Request: message to delete not found":
                self.cur.execute(
                    """UPDATE `message` SET `deleted` = 1 WHERE `chat_id` = %s AND `message_id` = %s""", (chat_id, message_id))
                self.db.commit()
            else:
                self.log("del msg error: chat_id={} message_id={} code={} msg={} datastr={}".format(
                    chat_id, message_id, e.code, e.msg, datastr))
                self.log(traceback.format_exc())

    def addmessage(self, user_id, message_id, full_name, msg_type, text, date, reply_to_message_id, reply_to_user_id):
        self.cur.execute("""INSERT INTO `message` (`chat_id`, `user_id`, `message_id`, `full_name`, `type`, `text`, `date`, `reply_to_message_id`, `reply_to_user_id`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                         (str(self.chat_id), str(user_id), str(message_id), full_name, msg_type, text, str(date), reply_to_message_id, reply_to_user_id))
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
        self.addmessage(self.botid, 0, '', 'log', text, date, '', '')

    def log(self, message):
        self.cur.execute("""INSERT INTO `log` (`chat_id`, `message`) VALUES (%s, %s)""",
                         (self.chat_id, str(message)))
        self.db.commit()

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()


class EthicsCommitteeExtension():
    def main(self, EC):
        raise NotImplementedError

    def web(self):
        raise NotImplementedError


def load_extensions(name):
    import importlib
    import extensions  # pylint: disable=E0401,W0611
    return importlib.import_module('.' + name, 'extensions').__mainclass__()
