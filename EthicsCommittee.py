# -*- coding: utf-8 -*-
import json
from flask import Flask, request, abort
import configparser
from Kamisu66 import EthicsCommittee
import os
import sys
import importlib
import traceback
from action.main import main_action


sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

config = configparser.ConfigParser()
configpath = os.path.dirname(os.path.realpath(__file__))+'/config.ini'
config.read(configpath)

app = Flask(__name__)

@app.route("/web")
def web():
	if "q" in request.args:
		try:
			module = importlib.import_module("."+request.args["q"], "action")
		except ImportError as e:
			return "No such module."
		try:
			return module.web()
		except AttributeError as e:
			return "This module doesn't have web."
	else:
		return "Not given module name."
	

@app.route("/webhook", methods=['POST'])
def telegram():
	try:
		data = json.loads(request.data.decode("utf8"))
		main_action(data)
	except Exception as e:
		EC = EthicsCommittee("error", "error")
		EC.log(traceback.format_exc())
	return "OK"

if __name__ == "__main__":
	app.run()
