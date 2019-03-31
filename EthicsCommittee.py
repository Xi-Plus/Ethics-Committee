# -*- coding: utf-8 -*-
import json
from flask import Flask, request, abort
import configparser
from Kamisu66 import EthicsCommittee, EthicsCommitteeExtension
import os
import sys
import importlib
import traceback
try:
    from config_local import extensions
except ImportError:
    from config_default import extensions


sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

config = configparser.ConfigParser()
configpath = os.path.dirname(os.path.realpath(__file__)) + '/config.ini'
config.read(configpath)

app = Flask(__name__)


@app.route("/web")
def web():
    if "q" in request.args:
        try:
            module = importlib.import_module(
                "." + request.args["q"], "extensions")
        except ImportError as e:
            return "No such module."

        try:
            return module.__mainclass__()().web()
        except (AttributeError, NotImplementedError) as e:
            EC = EthicsCommittee(0, 0)
            EC.log(traceback.format_exc())
            return "This module doesn't have web."
    else:
        return "Not given module name."


@app.route("/webhook", methods=['POST'])
def telegram():
    try:
        data = json.loads(request.data.decode("utf8"))
        for extension in extensions:
            try:
                extension.main(data)
            except NotImplementedError:
                EC = EthicsCommittee(0, 0)
                EC.log(traceback.format_exc())
    except Exception as e:
        EC = EthicsCommittee(0, 0)
        EC.log(traceback.format_exc())
    return "OK"


if __name__ == "__main__":
    app.run()
