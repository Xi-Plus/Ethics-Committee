# -*- coding: utf-8 -*-
import configparser
import json
import os
import time
import traceback
import urllib.parse
import urllib.request

import pymysql


class EthicsCommittee:
    def __init__(self, chat_id, user_id):
        self.chat_id = chat_id
        self.user_id = user_id
        config = configparser.ConfigParser()
        configpath = os.path.dirname(
            os.path.realpath(__file__)) + '/config.ini'
        config.read(configpath)
        self.token = config.get('telegram', 'token')
        self.botid = config.getint('telegram', 'botid')
        self.url = config.get('telegram', 'url')
        self.max_connections = config.get('telegram', 'max_connections')
        self.db = pymysql.connect(host=config.get('database', 'host'),
                                  user=config.get('database', 'user'),
                                  passwd=config.get('database', 'passwd'),
                                  db=config.get('database', 'db'),
                                  charset=config.get('database', 'charset'))
        self.cur = self.db.cursor()

    def sendmessage(self, message, parse_mode="Markdown", reply=False, reply_markup=None, chat_id=None):
        try:
            query = {}
            query["chat_id"] = self.chat_id
            if chat_id is not None:
                query["chat_id"] = chat_id
            if parse_mode != "":
                query["parse_mode"] = parse_mode
            if type(reply) == str or type(reply) == int:
                query["reply_to_message_id"] = reply
            if reply_markup != None:
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
                reply_to_message_id = ""
                reply_to_user_id = ""
                if "reply_to_message" in res["result"]:
                    reply_to_message_id = res["result"]["reply_to_message"]["message_id"]
                    reply_to_user_id = res["result"]["reply_to_message"]["from"]["id"]
                self.addmessage(self.botid, res["result"]["message_id"], from_first_name, "text",
                                res["result"]["text"], res["result"]["date"], reply_to_message_id, reply_to_user_id)
        except urllib.error.HTTPError as e:
            self.log("send msg error: code={} res={}".format(
                e.code, e.read().decode("utf8")))
            self.log(traceback.format_exc())
        except Exception as e:
            self.log(traceback.format_exc())

    def sendSticker(self, sticker, reply=False, chat_id=None):
        try:
            query = {}
            query["chat_id"] = self.chat_id
            if chat_id is not None:
                query["chat_id"] = chat_id
            if type(reply) == str or type(reply) == int:
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
                reply_to_message_id = ""
                reply_to_user_id = ""
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

    def editmessage(self, message_id, message, parse_mode="Markdown", reply_markup=None, chat_id=None):
        try:
            query = {}
            query["chat_id"] = self.chat_id
            if chat_id is not None:
                query["chat_id"] = chat_id
            if parse_mode != "":
                query["parse_mode"] = parse_mode
            if reply_markup != None:
                query["reply_markup"] = reply_markup
            query["disable_web_page_preview"] = 1
            query["message_id"] = message_id
            query["text"] = message

            query = urllib.parse.urlencode(query)
            url = "https://api.telegram.org/bot" + self.token + "/editMessageText?" + query
            res = urllib.request.urlopen(url).read().decode("utf8")
            res = json.loads(res)
            if res["ok"]:
                pass
        except urllib.error.HTTPError as e:
            self.log("edit msg error: code={} res={}".format(
                e.code, e.read().decode("utf8")))
            self.log(traceback.format_exc())
        except Exception as e:
            self.log(traceback.format_exc())

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
