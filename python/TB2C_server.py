#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TB2C_server
"""
import sys, os
import numpy as np
import json
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import TB2C_visualize
from pySPH import SPH
from SPH_filter import SPH_filter

#-----------------------------------------------------------------------------
g_app = None # global instance of TB2C_server

class TB2C_server:
    ''' TB2C_server
    TB2C serverのプロトタイプ実装クラスです。
    '''
    def __init__(self):
        self._meta_dic = None
        self._tb_uri = None
        self._div = [1, 1, 1]
        self._out_dir = '.'
        self._last_step = -1
        self._last_sph_list = []
        self._obj23dt_ver = None
        return
    
    @property
    def meta_dic(self):
        return self._meta_dic

    @property
    def tb_uri(self):
        return self._tb_uri

    @property
    def div(self):
        return self._div

    @property
    def out_dir(self):
        return self._out_dir

    def connectTB(self, uri:str):
        ''' connectTB
        URIで指定されたデータソースに接続し、メタデータを読み込み、
        'vistype'を付加して保持する。

        Parameters
        ----------
        uri: str
          データソースのURI
        '''
        with urllib.request.urlopen(uri) as response:
            res_bin = response.read()

        res_str = res_bin.decode()
        res_dic = json.loads(res_str)
        res_dic['vistype'] = ['isosurf']
        self._meta_dic = res_dic
        self._tb_uri = uri
        self._last_step = -1
        self._last_sph_list = []
        return

    def getSPHdata(self, id:int, stp:int) -> [SPH.SPH]:
        ''' getSPHdata
        TBより、idとstepを指定してSPHデータを取得する。
        実際にアクセスするURLは'{uri}/data?id={id}&step={stp}'

        Parameters
        ----------
        id: int
          取得するSPHデータのID
        step: int
          取得するSPHデータのタイムステップインデックス番号

        Returns
        -------
        [SPH.SPH]: 取得したデータ(を分割したリスト)
        '''
        if not self._tb_uri:
            return None
        if stp == self._last_step:
            return self._last_sph_list
        
        xuri = self._tb_uri
        if xuri.endswith('/'):
            xuri += 'data'
        else:
            xuri += '/data'
        xuri += '?id={}'.format(id)
        xuri += '&step={}'.format(stp)
        with urllib.request.urlopen(xuri) as response:
            res_bin = response.read()
        res_str = res_bin.decode()
        res_dic = json.loads(res_str)
        sph = SPH_filter.fromJSON(res_dic['data'])
        if not sph:
            return []
        if self.div[0]*self.div[1]*self.div[2] > 1:
            self._last_sph_list = SPH_filter.divideShareEdge(sph, self.div)
        else:
            self._last_sph_list = [sph]
        self._last_step = stp
        return self._last_sph_list

    def generateIsosurf(self, value:float) -> bool:
        ''' generateIsosurf
        現在保持しているSPHデータに対し、valueで指定された値で等値面を生成し、
        3D-Tiles形式のファイルに出力します。

        Parameters
        ----------
        value: float
          等値面を生成する値

        Returns
        -------
        bool: True=成功、False=失敗
        '''
        if self._last_step < 0:
            return False
        vis = TB2C_visualize.TB2C_visualize(self._out_dir)
        if not vis.isosurf(self._last_sph_list, value):
            return False
        return True

#-----------------------------------------------------------------------------
class TB2C_server_ReqHandler(SimpleHTTPRequestHandler):
    ''' TB2C_server_ReqHandler
    TB2C server用のHTTPリクエストハンドラー実装クラスです。
    '''
    def sendMsgRes(self, code:int, msg:str):
        ''' sendMsgRes
        HTTPアクセスに対するtext/plain形式のレスポンスを返す。

        Parameters
        ----------
        code: int
          レスポンスコード
        msg: str
          レスポンスメッセージ
        '''
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-length', len(msg))
        self.end_headers()
        self.wfile.write(bytes(msg, 'utf-8'))
        return
    
    def do_GET(self):
        ''' do_GET
        GETメソッド用のリクエストハンドラー
        要求されたパスが'/'の場合はメタデータを返し、'/quit'の場合は終了します。
        '''
        global g_app
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/':
            # メタデータ要求 --- 図種('vistype')を追加したメタデータを返す
            if not g_app:
                msg = 'no meta-data has hold.'
                self.sendMsgRes(412, msg)
                return
            qs = parse_qs(parsed_path.query)
            if 'update' in qs:
                try:
                    g_app.connectTB(g_app._tb_uri)
                except Exception as e:
                    msg = 'update meta-data failed.'
                    self.sendMsgRes(412, msg)
                    return
            meta_str = json.dumps(g_app.meta_dic)
            body = bytes(meta_str, 'utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-length', len(body))
            self.end_headers()
            self.wfile.write(body)
            return

        elif parsed_path.path == '/favicon.ico':
            # ignore
            return
            
        elif parsed_path.path == '/quit':
            # 停止要求 --- 終了する。pathが'/quit?with_tb=y'ならTBも停止させる。
            msg = 'ok'
            qs = parse_qs(parsed_path.query)
            if 'with_tb' in qs and qs['with_tb'][0] == 'y' and \
               g_app and g_app.tb_uri:
                xuri = g_app.tb_uri
                if xuri.endswith('/'):
                    xuri += 'quit'
                else:
                    xuri += '/quit'
                with urllib.request.urlopen(xuri) as response:
                    res_bin = response.read()
                if res_bin.decode() != 'ok':
                    msg += ' (TB not stopped)'
            self.sendMsgRes(200, msg)
            sys.exit(0)

        msg = 'invalid URL specified.'
        self.sendMsgRes(404, msg)
        return

    def do_POST(self):
        ''' do_POST
        POSTメソッド用のリクエストハンドラー
        要求されたパスが'/visualize'の場合はパラメータに従い可視化を行います。
        '''
        content_length = int(self.headers['content-length'])
        parsed_path = urlparse(self.path)

        if parsed_path.path in ('/visualize', '/visualize/'):
            # 図種生成要求 --- 指定されたstepの可視化図種を生成する
            req_body = self.rfile.read(content_length).decode('utf-8')
            req_dic = json.loads(req_body)
            try:
                step = int(req_dic['step'])
                vistype = req_dic['vistype']
                visparam = req_dic['visparam']
            except:
                msg = 'lack of required param.'
                self.sendMsgRes(412, msg)
                return
            if not vistype in {'isosurf'}:
                msg = 'vistype not supported: {}'.format(vistype)
                self.sendMsgRes(412, msg)
                return
            try:
                isoval = float(visparam['value'])
            except:
                msg = 'visparam[value] access failed.'
                self.sendMsgRes(412, msg)
                return

            # get data of step, and do visualize
            sph_lst = g_app.getSPHdata(g_app.meta_dic['id'], step)
            if len(sph_lst) < 1:
                msg = 'can not get SPH data.'
                self.sendMsgRes(412, msg)
                return
            if not g_app.generateIsosurf(isoval):
                msg = 'generate isosurface(s) failed.'
                self.sendMsgRes(412, msg)
                return
            
        else:
            msg = 'invalid URL specified.'
            self.sendMsgRes(404, msg)
            return

        self.sendMsgRes(200, 'ok')
        return


#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse
    prog = 'TB2C_server'

    # parse argv
    parser = argparse.ArgumentParser(description='TB2C server',
      usage='%(prog)s [--port 4000] [--tb http://localhost:4001/]'\
        + '\n        [--odir ./] [--dx divX] [--dy divY] [--dz divZ]')
    parser.add_argument('--port', help='port number', type=int, default='4000')
    parser.add_argument('--tb', help='URL of TB to connect', type=str,
                        default='http://localhost:4001/')
    parser.add_argument('--odir', type=str, default='.',
                        help='output directory for tileset.json')
    parser.add_argument('--dx', type=int, default=1,
                        help='Number of divisions in the X-axis direction')
    parser.add_argument('--dy', type=int, default=1,
                        help='Number of divisions in the Y-axis direction')
    parser.add_argument('--dz', type=int, default=1,
                        help='Number of divisions in the Z-axis direction')
    args = parser.parse_args()

    # create TB2C_server and get metadata
    g_app = TB2C_server()
    g_app._div[:] = [args.dx, args.dy, args.dz]
    g_app._out_dir = args.odir
    try:
        g_app.connectTB(args.tb)
    except Exception as e:
        print('{}: get metadata failed: {}'.format(prog, str(e)))
        sys.exit(1)

    # invoke HTTP server
    host = '0.0.0.0'
    port = args.port
    try:
        httpd = HTTPServer((host, port), TB2C_server_ReqHandler)
    except Exception as e:
        print('{}: invoke httpd failed: {}'.format(prog, str(e)))
        sys.exit(1)
    print('{}: started at port#{}'.format(prog, port))
    httpd.serve_forever()

    sys.exit(0)
    
