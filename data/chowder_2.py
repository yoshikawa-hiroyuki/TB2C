
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


def updateCamera(ch, id):
    # idと、更新したいパラメータを入れる
    # 指定されていないパラメータは無視される（更新されない
    content_req = JSONRPC('UpdateMetaData')
    meta_data = {}
    meta_data['id'] = id
    meta_data['cameraWorldMatrix'] = json.dumps([\
        0.9904480059361608,\
        0.13788671994460838,\
        1.3877787807814457e-17,\
        0,\
        -0.06547901568723759,\
        0.4703394245953484,\
        0.8800530235025317,\
        0,\
        0.12134762478809945,\
        -0.8716467622461717,\
        0.4748754319019388,\
        0,\
        1882322.7995019327,\
        -9977694.58814505 + 1000000,\
        6849391.7570487335,\
        1\
    ])
    content_req['params'] = [meta_data] # UpdateMetaDataはリスト形式でmetadataを入れる必要があります（複数同時更新に対応）
    def updatemeta_callback(ch):
        def func(err, result):
            print(result)
        return func
    ch.send_json(content_req, updatemeta_callback(ch))
    return content_req


def add3DTilesContent(ch, image_data, update_id='000'):
    content_req = JSONRPC('AddContent')
    meta_data = {}
    meta_data['id'] = 'my3dtilecontent'
    meta_data['posx'] = 0
    meta_data['posy'] = 0
    meta_data['width'] = 640
    meta_data['height'] = 480
    meta_data['type'] = 'webgl'
    meta_data['visible'] = "true" # 登録直後から表示する場合
    meta_data['url'] =  urllib.parse.unquote('itowns/Preset/cartesian/cartesian.html')
    #meta_data['cameraWorldMatrix'] = json.dumps([ \
    #    0.0, 0.0, 1.0, 0.0, \
    #    1.0, 0.0, 0.0, 0.0, \
    #    0.0, 1.0, 0.0, 0.0, \
    #    0.0, 0.0, -6378237.0, 1.0 \
    #])

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

    tileLayer0 = {}
    tileLayer0['id'] = 'isosurf_0' # 他と被らないIDが必須
    tileLayer0['type'] = '3dtile' # 必須
    tileLayer0['visible'] = 'true' # 必須
    tileLayer0['url'] = 'http://localhost/data/b3dm/Batchedisosurf_0/tileset.json'
    tileLayer0['sseThreshold'] = 0
    tileLayer0['update_id'] = update_id

    tileLayer1 = {}
    tileLayer1['id'] = 'isosurf_1' # 他と被らないIDが必須
    tileLayer1['type'] = '3dtile' # 必須
    tileLayer1['visible'] = 'true' # 必須
    tileLayer1['url'] = 'http://localhost/data/b3dm/Batchedisosurf_1/tileset.json'
    tileLayer1['sseThreshold'] = 0
    tileLayer1['update_id'] = update_id

    # chowder itowns appでの編集用パラメータ
    meta_data['layerList'] = json.dumps([tileLayer0, tileLayer1])
    
    content_req['params'] = meta_data
    
    def addwebgl_callback(ch):
        def func(err, result):
            print(result)
        return func
    ch.send_binary(content_req, image_data, addwebgl_callback(ch)) # webglコンテンツの場合, image_dataはサムネイルとして使わます
    # サムネイルの推奨サイズ：横200px、縦140px

    return content_req

def update3DTilesContent(ch, id, update_id):
    content_req = JSONRPC('UpdateMetaData')
    meta_data = {}
    meta_data['id'] = id
    meta_data['type'] = 'webgl'
    tileLayer2 = {}
    tileLayer2['id'] = 'isosurf_2' # 他と被らないIDが必須
    tileLayer2['type'] = '3dtile' # 必須
    tileLayer2['visible'] = 'true' # 必須
    tileLayer2['url'] = 'http://localhost/data/b3dm/Batchedisosurf_2/tileset.json'
    tileLayer2['sseThreshold'] = 0
    tileLayer2['update_id'] = update_id

    tileLayer3 = {}
    tileLayer3['id'] = 'isosurf_3' # 他と被らないIDが必須
    tileLayer3['type'] = '3dtile' # 必須
    tileLayer3['visible'] = 'true' # 必須
    tileLayer3['url'] = 'http://localhost/data/b3dm/Batchedisosurf_3/tileset.json'
    tileLayer3['sseThreshold'] = 0
    tileLayer3['update_id'] = update_id

    meta_data['layerList'] = json.dumps([tileLayer2, tileLayer3]) # chowder itowns appでの編集用パラメータ

    content_req['params'] = [meta_data] # UpdateMetaDataはリスト形式でmetadataを入れる必要があります（複数同時更新に対応）
    def updatemeta_callback(ch):
        def func(err, result):
            print(result)
        return func
    ch.send_json(content_req, updatemeta_callback(ch))
    return content_req

def update3DTilesContent2(ch, id, update_id):
    content_req = JSONRPC('UpdateMetaData')
    meta_data = {}
    meta_data['id'] = id
    meta_data['type'] = 'webgl'

    tileLayer0 = {}
    tileLayer0['id'] = 'isosurf_0' # 他と被らないIDが必須
    tileLayer0['type'] = '3dtile' # 必須
    tileLayer0['visible'] = 'true' # 必須
    tileLayer0['url'] = 'http://localhost/data/b3dm/Batchedisosurf_0/tileset.json'
    tileLayer0['sseThreshold'] = 0
    tileLayer0['update_id'] = update_id

    tileLayer1 = {}
    tileLayer1['id'] = 'isosurf_1' # 他と被らないIDが必須
    tileLayer1['type'] = '3dtile' # 必須
    tileLayer1['visible'] = 'true' # 必須
    tileLayer1['url'] = 'http://localhost/data/b3dm/Batchedisosurf_1/tileset.json'
    tileLayer1['sseThreshold'] = 0
    tileLayer1['update_id'] = update_id

    tileLayer2 = {}
    tileLayer2['id'] = 'isosurf_2' # 他と被らないIDが必須
    tileLayer2['type'] = '3dtile' # 必須
    tileLayer2['visible'] = 'true' # 必須
    tileLayer2['url'] = 'http://localhost/data/b3dm/Batchedisosurf_2/tileset.json'
    tileLayer2['sseThreshold'] = 0
    tileLayer2['update_id'] = update_id

    tileLayer3 = {}
    tileLayer3['id'] = 'isosurf_3' # 他と被らないIDが必須
    tileLayer3['type'] = '3dtile' # 必須
    tileLayer3['visible'] = 'true' # 必須
    tileLayer3['url'] = 'http://localhost/data/b3dm/Batchedisosurf_3/tileset.json'
    tileLayer3['sseThreshold'] = 0
    tileLayer3['update_id'] = update_id

    meta_data['layerList'] = json.dumps([tileLayer0, tileLayer1, tileLayer2, tileLayer3]) # chowder itowns appでの編集用パラメータ
    
    content_req['params'] = [meta_data] # UpdateMetaDataはリスト形式でmetadataを入れる必要があります（複数同時更新に対応）
    def updatemeta_callback(ch):
        def func(err, result):
            print(result)
        return func
    ch.send_json(content_req, updatemeta_callback(ch))
    return content_req

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

    # 画像データの読み込み
    image_path = os.path.abspath('thumb.png')
    image_data = open(image_path, "rb").read(os.path.getsize(image_path))

    ### webglコンテンツ登録
    print("\n add3DTilesContent")
    content_req = add3DTilesContent(ch, image_data)

    # コンテンツ追加完了待ち
    while not ch.is_done(content_req):
        time.sleep(0.01)

    sys.exit(0)
    ### 5秒待つ
    time.sleep(5)

    update_target_id = content_req['params']['id']

    # 同じURLのデータを再読み込み(update_idの変更による更新)
    print("\n update3DTilesContent")
    content_req = update3DTilesContent(ch, update_target_id, 'aaa')

    # メタデータ更新完了待ち
    while not ch.is_done(content_req):
        time.sleep(0.01)
        
    time.sleep(5)

    # カメラ更新
    print("\n updateCamera")
    content_req = updateCamera(ch, update_target_id)

    # メタデータ更新完了待ち
    while not ch.is_done(content_req):
        time.sleep(0.01)

    time.sleep(5)

    # 同じURLのデータを再読み込み(update_idの変更による更新)
    print("\n update3DTilesContent2")
    content_req = update3DTilesContent2(ch, update_target_id, 'bbb')

    # メタデータ更新完了待ち
    while not ch.is_done(content_req):
        time.sleep(0.01)

        
    ch.disconnect()
    ch.wait_until_close()
    
hello()
