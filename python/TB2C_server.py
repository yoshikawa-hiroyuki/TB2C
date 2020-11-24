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

g_meta_dic = None

class TB2C_server_ReqHandler(SimpleHTTPRequestHandler):
    ''' TB2C_server_ReqHandler
    TB2C server用のHTTPリクエストハンドラー実装クラスです。
    '''    
    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/':
            # メタデータ要求 --- 図種('vistype')を追加したメタデータを返す
            if not g_meta_dic:
                msg = 'no meta-data has hold.'
                self.send_response(412)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-length', len(msg))
                self.end_headers()
                self.wfile.write(bytes(msg, 'utf-8'))
                return
            meta_str = json.dumps(g_meta_dic)
            body = bytes(meta_str, 'utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-length', len(body))
            self.end_headers()
            self.wfile.write(body)
            return

        elif parsed_path.path == '/quit':
            # 停止要求
            msg = 'ok'
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
            if vistype != 'isosurf':
                msg = 'vistype not supported: {}'.format(vistype)
                self.send_response(412)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-length', len(msg))
                self.end_headers()
                self.wfile.write(bytes(msg, 'utf-8'))
                return

            # get data of step, and visualize
            
            
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

    
def getMetadata(uri:str) -> {}:
    with urllib.request.urlopen(uri) as response:
        res_bin = response.read()
       
    res_str = res_bin.decode()
    res_dic = json.loads(res_str)
    res_dic['vistype'] = ['isosurf']
    return res_dic


def getSPHdata(uri:str, id:int, stp:int) -> SPH.SPH:
    xuri = uri
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

    # get metadata from TB
    try:
        g_meta_dic = getMetadata(args.t)
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
    