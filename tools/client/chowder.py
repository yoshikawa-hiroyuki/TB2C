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


def add3DTilesContent(ch, image_data):
    content_req = JSONRPC('AddContent')

    meta_data = {}
    meta_data['id'] = 'tb2c_content'
    meta_data['posx'] = 0
    meta_data['posy'] = 0
    meta_data['width'] = 640
    meta_data['height'] = 480
    meta_data['type'] = 'webgl'
    meta_data['visible'] = "true" # 登録直後から表示する場合
    meta_data['url'] = urllib.parse.unquote('data/tb2c_vis.html')
    tileLayer = {}
    tileLayer['id'] = '3dtiles_tb2c' # 他と被らないIDが必須
    tileLayer['type'] = '3dtile' # 必須
    tileLayer['visible'] = 'true' # 必須
    ###tileLayer['url'] = 'http://localhost/data/tileset.json'
    # chowder itowns appでの編集用パラメータ
    meta_data['layerList'] = json.dumps([tileLayer])
    #meta_data['cameraWorldMatrix'] = json.dumps([\
    #    1.0, 0.0, 0.0, 0,\
    #    0.0, 1.0, 0.0, 0,\
    #    0.0, 0.0, 1.0, 0,\
    #    0.0, 0.0, 50.0,\
    #    1\
    #])
    # カメラパラメータ
    cparam = {}
    cparam['fovy'] = 45
    cparam['zoom'] = 1
    cparam['near'] = 1
    #cparam['far'] = 63781370
    cparam['filmOffset'] = 0
    cparam['filmGauge'] = 35
    cparam['aspect'] = 640.0 / 480.0
    meta_data['cameraParams'] = json.dumps(cparam)
    content_req['params'] = meta_data
    
    def addwebgl_callback(ch):
        def func(err, result):
            #print(result)
            pass
        return func
    
    ch.send_binary(content_req, image_data, addwebgl_callback(ch))
    # webglコンテンツの場合, image_dataはサムネイルとして使われます
    # サムネイルの推奨サイズ：横200px、縦140px

    return content_req

def update3DTilesContent(ch, id, update_id):
    content_req = JSONRPC('UpdateMetaData')
    meta_data = {}
    meta_data['id'] = id
    meta_data['type'] = 'webgl'
    tileLayer = {}
    tileLayer['id'] = '3dtiles_tb2c' # 他と被らないIDが必須
    tileLayer['type'] = '3dtile' # 必須
    tileLayer['visible'] = 'true' # 必須
    tileLayer['url'] = 'http://localhost/itowns/Preset/tb2c/tileset.json'

    # 前回と違うupdate_id（任意の文字列）を入れると、全く同じURLでも再読み込みされる
    if update_id != None:
        tileLayer['update_id'] = update_id

    # chowder itowns appでの編集用パラメータ
    meta_data['layerList'] = json.dumps([tileLayer])
    # UpdateMetaDataはリスト形式でmetadataを入れる必要があります（複数同時更新に対応）
    content_req['params'] = [meta_data]
    def updatemeta_callback(ch):
        def func(err, result):
            #print(result)
            pass
        return func
    ch.send_json(content_req, updatemeta_callback(ch))
    return content_req


#-----------------------------------------------------------------------------
# 試し
def main():
    ch = ChOWDER()

    ### ChOWDERサーバに接続
    ch.connect()

    ### loginリクエスト
    login_req = JSONRPC('Login')
    login_req['params']['id'] = 'APIUser'
    login_req['params']['password'] = 'password'
    def login_callback(err, result):
        # 次回同じセッションにログインし直すためのキーが返ってくる 
        # id, passwordの代わりに key : loginKeyを入れると再ログイン可能
        print('loginkey=' + result['loginkey'])
    ch.send_json(login_req, login_callback)

    # 画像データの読み込み
    image_path = os.path.abspath('thumb.png')
    image_data = open(image_path, "rb").read(os.path.getsize(image_path))

    ### webglコンテンツ登録
    print("\nCall add3DTilesContent")
    content_req = add3DTilesContent(ch, image_data)

    # コンテンツ追加完了待ち
    while not ch.is_done(content_req):
        time.sleep(0.05)
    ch.disconnect()
    ch.wait_until_close()
    
if __name__ == '__main__':
    main()
