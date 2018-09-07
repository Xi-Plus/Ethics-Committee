# -*- coding: utf-8 -*-
import pymysql
import configparser
import random
import re
import os
import json
import traceback
import urllib.parse
import urllib.request

class EthicsCommittee:
	def __init__(self, chat_id, user_id):
		self.chat_id = chat_id
		self.user_id = user_id
		config = configparser.ConfigParser()
		configpath = os.path.dirname(os.path.realpath(__file__))+'/config.ini'
		config.read(configpath)
		self.token = config.get('telegram', 'token')
		self.botid = config.getint('telegram', 'botid')
		self.db = pymysql.connect(host=config.get('database', 'host'),
								  user=config.get('database', 'user'),
								  passwd=config.get('database', 'passwd'),
								  db=config.get('database', 'db'),
								  charset=config.get('database', 'charset'))
		self.cur = self.db.cursor()
		self.tableprefix = config.get('database', 'tableprefix')

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
			url = "https://api.telegram.org/bot"+self.token+"/sendMessage?"+query
			res = urllib.request.urlopen(url).read().decode("utf8")
			res = json.loads(res)
			if res["ok"]:
				from_first_name = ""
				if "from" in res["result"]:
					from_first_name =  res["result"]["from"]["first_name"]
				reply_to_message_id = ""
				reply_to_user_id = ""
				if "reply_to_message" in res["result"]:
					reply_to_message_id = res["result"]["reply_to_message"]["message_id"]
					reply_to_user_id = res["result"]["reply_to_message"]["from"]["id"]
				self.addmessage(self.botid, res["result"]["message_id"], from_first_name, "text", res["result"]["text"], res["result"]["date"], reply_to_message_id, reply_to_user_id)
		except urllib.error.HTTPError as e:
			self.log("send msg error: "+str(e.code)+" "+str(e.read().decode("utf8")))
			self.log(traceback.format_exc())
		except Exception as e:
			self.log(traceback.format_exc())

	def deletemessage(self, chat_id, message_id):
		try:
			url = "https://api.telegram.org/bot"+self.token+"/deleteMessage?chat_id="+str(chat_id)+"&message_id="+str(message_id)
			urllib.request.urlopen(url)
			self.cur.execute("""UPDATE `EC_message` SET `deleted` = 1 WHERE `chat_id` = %s AND `message_id` = %s""", (chat_id, message_id))
			self.db.commit()
		except urllib.error.HTTPError as e:
			datastr = e.read().decode("utf8")
			data = json.loads(datastr)
			if data["description"] == "Bad Request: message to delete not found":
				self.cur.execute("""UPDATE `EC_message` SET `deleted` = 1 WHERE `chat_id` = %s AND `message_id` = %s""", (chat_id, message_id))
				self.db.commit()
			else :
				self.log("del msg error: "+str(chat_id)+" "+str(message_id)+" "+str(e.code)+" "+str(e.msg)+" "+str(e.hdrs)+" "+str(datastr))
				self.log(traceback.format_exc())

	def addmessage(self, user_id, message_id, first_name, type, text, date, reply_to_message_id, reply_to_user_id):
		self.cur.execute("""INSERT INTO `EC_message` (`chat_id`, `user_id`, `message_id`, `first_name`, `type`, `text`, `date`, `reply_to_message_id`, `reply_to_user_id`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
			(str(self.chat_id), str(user_id), str(message_id), first_name, type, text, str(date), reply_to_message_id, reply_to_user_id) )
		self.db.commit()

	def log(self, message):
		self.cur.execute("""INSERT INTO `EC_log` (`chat_id`, `message`) VALUES (%s, %s)""",
			(self.chat_id, str(message)) )
		self.db.commit()

	def __exit__(self):
		self.db.close()
