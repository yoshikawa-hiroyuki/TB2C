#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TB2C_server
"""
import sys, os
import numpy as np
from pySPH import SPH
from SPH_filter import SPH_filter
import json
import urllib.request

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

#-----------------------------------------------------------------------------
class TB2C_server:
    def __init__(self):
        self._meta_dic = None
        self._tb_uri = None
        return
    
    @property
    def meta_dic(self):
        return self._meta_dic

    @property
    def tb_uri(self):
        return self._tb_uri

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
        return

    def getSPHdata(self, id:int, stp:int) -> SPH.SPH:
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
        SPH.SPH: 取得したデータ
        '''
        if not self._tb_uri:
            return None
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
        return sph

g_app = None

#-----------------------------------------------------------------------------
class TB2C_server_ReqHandler(SimpleHTTPRequestHandler):
    ''' TB2C_server_ReqHandler
    TB2C server用のHTTPリクエストハンドラー実装クラスです。
    '''
    def do_GET(self):
        ''' do_GET
        GETメソッド用のリクエストハンドラー
        要求されたパスが'/'の場合はメタデータを返し、'/quit'の場合は終了する。
        '''
        global g_app
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/':
            # メタデータ要求 --- 図種('vistype')を追加したメタデータを返す
            if not g_app:
                msg = 'no meta-data has hold.'
                self.send_response(412)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-length', len(msg))
                self.end_headers()
                self.wfile.write(bytes(msg, 'utf-8'))
                return
            meta_str = json.dumps(g_app.meta_dic)
            body = bytes(meta_str, 'utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-length', len(body))
            self.end_headers()
            self.wfile.write(body)
            return

        elif parsed_path.path == '/quit':
            # 停止要求 --- TBを停止させ、自分も終了する
            msg = 'ok'
            if g_app and g_app.tb_uri:
                xuri = g_app.tb_uri
                if xuri.endswith('/'):
                    xuri += 'quit'
                else:
                    xuri += '/quit'
                with urllib.request.urlopen(xuri) as response:
                    res_bin = response.read()
                if res_bin.decode() != 'ok':
                    msg += ' (TB not stopped)'
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-length', len(msg))
            self.end_headers()
            self.wfile.write(bytes(msg, 'utf-8'))
            sys.exit(0)

        msg = 'invalid URL specified.'
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-length', len(msg))
        self.end_headers()
        self.wfile.write(bytes(msg, 'utf-8'))
        return

    def do_POST(self):
        ''' do_POST
        POSTメソッド用のリクエストハンドラー
        要求されたパスが'/visualize'の場合はパラメータに従い可視化を行う。
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
                self.send_response(412)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-length', len(msg))
                self.end_headers()
                self.wfile.write(bytes(msg, 'utf-8'))
                return
            if not vistype in {'isosurf'}:
                msg = 'vistype not supported: {}'.format(vistype)
                self.send_response(412)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-length', len(msg))
                self.end_headers()
                self.wfile.write(bytes(msg, 'utf-8'))
                return

            # get data of step, and visualize
            #sph = getSPHdata(args.t, g_meta_dic['id'], step)
            
            
        else:
            msg = 'invalid URL specified.'
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-length', len(msg))
            self.end_headers()
            self.wfile.write(bytes(msg, 'utf-8'))
            return

        msg = 'ok'
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-length', len(msg))
        self.end_headers()
        self.wfile.write(bytes(msg, 'utf-8'))
        return


def usage(prog:str ='TB2C_server'):
    print('usage: {} [-p port] [-t url_TB] [-d out_dir]'.format(prog))
    return


if __name__ == '__main__':
    import argparse
    prog = 'TB2C_server'

    # parse argv
    parser = argparse.ArgumentParser(description='TB2C server')
    parser.add_argument('-p', help='port number', type=int, default='4000')
    parser.add_argument('-t', help='URL of TB to connect', type=str,
                        default='http://localhost:4001/')
    parser.add_argument('-d', help='output dir for tileset.json', type=str,
                        default='.')
    args = parser.parse_args()

    # create TB2C_server and get metadata
    g_app = TB2C_server()
    try:
        g_app.connectTB(args.t)
    except Exception as e:
        print('{}: get metadata failed: {}'.format(prog, str(e)))
        sys.exit(1)

    # invoke HTTP server
    host = '0.0.0.0'
    port = args.p
    try:
        httpd = HTTPServer((host, port), TB2C_server_ReqHandler)
    except Exception as e:
        print('{}: invoke httpd failed: {}'.format(prog, str(e)))
        sys.exit(1)
    print('{}: serving started at port#{}'.format(prog, port))
    httpd.serve_forever()

    sys.exit(0)
    #sph = getSPHdata(args.t, g_meta_dic['id'], 30)
    #print(sph)
    
