# -*- coding: utf-8 -*-
import json
import os
import sys
import traceback

from flask import Flask, request

from config_extension import extensions, webs  # pylint: disable=E0401
from Kamisu66 import EthicsCommittee

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

app = Flask(__name__)


@app.route("/web")
def web():
    if "q" in request.args:
        if request.args['q'] in webs:
            try:
                return webs[request.args['q']].web()
            except (AttributeError, NotImplementedError):
                EC = EthicsCommittee(0, 0)
                EC.log(traceback.format_exc())
                return "This module doesn't have web."
        else:
            return "No such module."
    else:
        return "Not given module name."


@app.route("/webhook", methods=['POST'])
def telegram():
    try:
        data = json.loads(request.data.decode("utf8"))
        EC = EthicsCommittee(update=data)
        for extension in extensions:
            try:
                extension.main(EC)
            except NotImplementedError:
                EC = EthicsCommittee(0, 0)
                EC.log(traceback.format_exc())
    except Exception:
        EC = EthicsCommittee(0, 0)
        EC.log(traceback.format_exc())
    return "OK"


if __name__ == "__main__":
    app.run()
