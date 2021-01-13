#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import websocket # pip install websocket-client
import os
import sys
import json
import metabinary
import threading
import time
import urllib

CHOWDER_SERVER = 'ws://{}/v2'
HTML_PATH = 'itowns/Preset/cartesian/cartesian.html'

# JSONPRC用のdictを返す
def JSONRPC(method, forBinary = False):
    JSONRPC.id_counter += 1
    req = {}
    req['jsonrpc'] = '2.0'
    req['id'] = JSONRPC.id_counter
    req['method'] = method
    req['params'] = {}
    req['type'] = 'utf8'
    if forBinary:
        req['type'] = 'binary'
    return req
# 非同期メッセージ用カウンタを初期化
JSONRPC.id_counter = 1

# ChOWDERと通信するクラス
class ChOWDER:
    def __init__(self):
        # websocket connection
        self.connection = None
        self.is_open = False
        self.callback_dict = {}

    def _on_message(self):
        def func(ws, message):
            res = json.loads(message)
            if res != None:
                if 'id' in res and res['id'] in self.callback_dict:
                    err = None
                    result = None
                    if 'error' in res:
                        err = res['error']
                    if 'result' in res:
                        result = res['result']
                    self.callback_dict[res['id']](err, result)
                    del self.callback_dict[res['id']]
        return func

    def _on_error(self):
        def func(ws, error):
            raise Exception(error)
        return func

    def _on_close(self):
        def func(ws):
            self.is_open = False
        return func

    def _on_open(self):
        def func(ws):
            self.is_open = True
        return func

    # ChOWDERサーバに接続
    def connect(self, host):
        #websocket.enableTrace(True)
        url = CHOWDER_SERVER.format(host)
        self.connection =  websocket.WebSocketApp(url,\
                                    on_message=self._on_message(),\
                                    on_error=self._on_error(),\
                                    on_close=self._on_close(),
                                    on_open=self._on_open())
        wst = threading.Thread(target=self.connection.run_forever)
        wst.daemon = True
        wst.start()
        while not self.is_open:
            time.sleep(1)

    # 切断
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.is_open = False

    # JSONRPC2形式でリクエストを送る
    # @param req リクエストを含んだdict. 
    # 　　　　　　reqはJSONRPC()によって作成可能.
    def send_json(self, req, callback = lambda : None):
        self.callback_dict[req['id']] = callback
        self.connection.send(json.dumps(req))

    # JSONRPC2形式でリクエストを送る
    # @param req リクエストを含んだdict. 
    # @param binary 画像などのコンテンツデータ（バイナリデータ）. 
    def send_binary(self, req, binary, callback = lambda : None):
        # metabinaryにまとめる
        mb = metabinary.MetaBinary().createMetaBinary(req, binary)
        self.callback_dict[req['id']] = callback
        self.connection.send(mb, opcode=websocket.ABNF.OPCODE_BINARY)

    # 切断されるまで待機
    def wait_until_close(self):
        while self.is_open:
            time.sleep(1)

    # send_json, send_binaryしたリクエストが終了したかどうか
    def is_done(self, req):
        return not(req['id'] in self.callback_dict)


def add3DTilesContent(ch, layerList:[], image_data):
    content_req = JSONRPC('AddContent')
    meta_data = {}
    meta_data['id'] = 'tb2c_3dtile'
    meta_data['posx'] = 0
    meta_data['posy'] = 0
    meta_data['width'] = 640
    meta_data['height'] = 480
    meta_data['type'] = 'webgl'
    meta_data['visible'] = "true"
    meta_data['url'] =  urllib.parse.unquote(HTML_PATH)
    meta_data['layerList'] = json.dumps(layerList)

    # カメラパラメータ
    cparam = {}
    cparam['fovy'] = 45
    cparam['zoom'] = 1
    cparam['near'] = 15
    cparam['far'] = 63781370
    cparam['filmOffset'] = 0
    cparam['filmGauge'] = 35
    cparam['aspect'] = 640.0 / 480.0
    meta_data['cameraParams'] = json.dumps(cparam)
    content_req['params'] = meta_data

    def addwebgl_callback(ch):
        def func(err, result):
            pass
            #print(result)
        return func
    ch.send_binary(content_req, image_data, addwebgl_callback(ch))
    return content_req

def update3DTilesContent(ch, id, layerList:[]):
    content_req = JSONRPC('UpdateMetaData')
    meta_data = {}
    meta_data['id'] = id
    meta_data['type'] = 'webgl'
    # 前回と違うupdate_id（任意の文字列）を入れると、全く同じURLでも再読み込みされる
    update_id = time.asctime(time.localtime())
    for tileLayer in layerList:
        tileLayer['update_id'] = update_id
        continue
    meta_data['layerList'] = json.dumps(layerList)

    # UpdateMetaDataはリスト形式でmetadataを入れる
    content_req['params'] = [meta_data]

    def updatemeta_callback(ch):
        def func(err, result):
            pass
            #print(result)
        return func
    ch.send_json(content_req, updatemeta_callback(ch))
    return content_req

def updateCamera(ch, id, cmat):
    content_req = JSONRPC('UpdateMetaData')
    meta_data = {}
    meta_data['id'] = id
    meta_data['cameraWorldMatrix'] = json.dumps(cmat)

    content_req['params'] = [meta_data]

    def updatemeta_callback(ch):
        def func(err, result):
            pass
            #print(result)
        return func
    ch.send_json(content_req, updatemeta_callback(ch))
    return content_req
