
import websocket # pip install websocket-client
import os
import sys
import json
import metabinary
import threading
import time
import urllib

CHOWDER_SERVER = 'ws://localhost/v2'
API_USER_PASSWORD = '123456'

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
                if 'method' in res and res['method'] in self.callback_dict:
                    err = None
                    params = None
                    if 'error' in res:
                        err = res['error']
                    if 'params' in res:
                        params = res['params']
                    self.callback_dict[res['method']](err, params)
        return func

    def _on_error(self):
        def func(ws, error):
            print(error)
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
    def connect(self):
        #websocket.enableTrace(True)
        self.connection =  websocket.WebSocketApp(CHOWDER_SERVER,\
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

    # あるmethod名のメッセージを取得したらcallbackを呼ぶ
    def listen(self, methodName, callback):
        self.callback_dict[methodName] = callback

def measureTime(ch, id):
    measure_req = JSONRPC('SendMessage')
    meta_data = {}
    meta_data['id'] = id
    meta_data['command'] = 'measureITownPerformance'
    measure_req['params'] = meta_data
    ch.send_json(measure_req)
    return measure_req

# 試し
def hello():
    ch = ChOWDER()

    ### ChOWDERサーバに接続
    ch.connect()

    ### loginリクエスト
    login_req = JSONRPC('Login')
    login_req['params']['id'] = 'APIUser'
    login_req['params']['password'] = API_USER_PASSWORD
    def login_callback(err, result):
        # 次回同じセッションにログインし直すためのキーが返ってくる 
        # id, passwordの代わりに key : loginKeyを入れると再ログイン可能
        print(result['loginkey'])
    ch.send_json(login_req, login_callback)

    # 計測結果受け取り
    def measure_result_callback(err, params):
        if 'command' in params and params['command'] == 'measureITownPerformanceResult':
            print('Measure Result:', params['result'])
    ch.listen('SendMessage', measure_result_callback)

    # 測定命令送信(第二引数に適切なコンテンツIDを入れてください)
    measure_req = measureTime(ch, 'tb2c_3dtile')
    # 完了待ち(ディスプレイの状況によって変更してください)
    time.sleep(10)

    ch.disconnect()
    ch.wait_until_close()
    
hello()
