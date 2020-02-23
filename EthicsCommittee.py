# -*- coding: utf-8 -*-
import json
import os
import sys
import time
import traceback
import logging

from flask import Flask, request
from celery import Celery

from config_extension import extensions, webs  # pylint: disable=E0401
from Kamisu66 import EthicsCommittee

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

app = Flask(__name__)
celery = Celery('EthicsCommittee')
celery.config_from_object('config_variable')


@app.route("/pyversion")
def pyversion():
    return sys.version


@celery.task(bind=True, name='EthicsCommittee.process', queue='EthicsCommittee')
def process(self, text):
    logging.info(text)
    try:
        data = json.loads(text)
        if 'message' in data and int(data['message']['date']) < time.time() - 600:
            logging.warning('\tignore')
            return
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
        text = request.data.decode("utf8")
        process.delay(text)
    except Exception:
        EC = EthicsCommittee(0, 0)
        EC.log(traceback.format_exc())
    return "OK"


if __name__ == "__main__":
    app.run()
