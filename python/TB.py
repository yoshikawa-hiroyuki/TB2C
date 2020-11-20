#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Temporal Buffer prototype
"""
__author__ = "Yoshikawa, Hiroyuki <yoh@fujitsu.com>"
__version__ = "0.1.0"

import sys, os
import numpy as np
from pySPH import SPH
from TSDataSPH import TSDataSPH
import json
from collections import OrderedDict

class TB(object):
    ''' TB - Temporal Buffer
    Temporal Bufferのプロトタイプ実装クラスです。
    JSONまたはファイルリストで指定された時系列SPHデータを読み込み、保持します。
    また、要求されたタイムスライスのデータをエンコードして送信します。
    '''
    __seq = 1
    
    def __init__(self) -> None:
        self._tsdata = TSDataSPH()
        self._lastErr = None
        self._id = TB.__seq; TB.__seq += 1
        return

    def loadFromJSON(self, json_path: str) -> bool:
        ''' loadFromJSON
        JSONファイルから時系列SPHデータを読み込みます。
        JSONファイルは、以下の形式であることを想定しています。
        {
          "basedir": "SPHファイルが存在するディレクトリ(省略時は'.')"
          "filelist": [
            {"file": "ファイル名1", "step": "タイムステップ番号", "time": "時刻"},
            ...
          ]
        }
        タイムステップ番号と時刻はオプションで、省略された場合SPHファイルに格納されて
        いるタイムステップ番号、時刻が採用されます。

        Parameters
        ----------
        json_path: str
          JSONファイルのパス
        
        Returns
        -------
        bool: True=成功、false=失敗
        '''
        # open and read JSON file
        try:
            with open(json_path) as f:
                jf = json.load(f, object_pairs_hook=OrderedDict)
        except FileNotFoundError as e:
            self._lastErr = str(e)
            return False

        # check 'basedir' and 'filelist' key
        basedir = '.'
        if 'basedir' in jf.keys():
            basedir = jf['basedir']
        try:
            flist = jf['filelist']
        except KeyError:
            self._lastErr = 'no filelist key in ' + json_path
            return False

        # generate list(s)
        file_lst = []
        step_lst = []
        time_lst = []
        for o in flist:
            okeys = o.keys()
            if not 'file' in okeys:
                continue
            if 'step' in okeys:
                step_lst.append(int(o['step']))
            else:
                step_lst.append(None)
            if 'time' in okeys:
                time_lst.append(int(o['time']))
            else:
                time_lst.append(None)
            file_lst.append(o['file'])
            continue # end of for(o)

        # load SPH files
        if not self._tsdata.setupFiles(file_lst, basedir):
            self._lastErr = 'load SPH file failed'
            return False

        # adjust step and time
        for i in range(len(step_lst)):
            if step_lst[i] != None:
                self._tsdata._stepList[i] = step_lst[i]
            if time_lst[i] != None:
                self._tsdata._timeList[i] = time_lst[i]
            continue # end of for(i)
        for i in range(1,len(self._tsdata._stepList)):
            if self._tsdata._stepList[i] <= self._tsdata._stepList[i-1]:
                self._tsdata._stepList[i] = self._tsdata._stepList[i-1] + 1
            if self._tsdata._timeList[i] <= self._tsdata._timeList[i-1]:
                self._tsdata._timeList[i] = self._tsdata._timeList[i-1] + 1.0
            self._tsdata._dataList[i]._step = self._tsdata._stepList[i]
            self._tsdata._dataList[i]._time = self._tsdata._timeList[i]
            continue # end of for(i)

        return True

    def loadFromFilelist(self, fnlist: [], basedir: str ='.') -> bool:
        ''' loadFromFilelist
        SPHファイルのリストを時系列データとして読み込みます。

        Parameters
        ----------
        fnlist: str[]
          SPHファイルのパスのリスト
        basedir: str
          SPHファイルが存在するディレクトリ(省略時は'.')

        Returns
        -------
        bool: True=成功、false=失敗
        '''
        # load SPH files
        if not self._tsdata.setupFiles(fnlist, basedir):
            self._lastErr = 'load SPH file failed'
            return False
        return True

    
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from SPH_filter import SPH_filter

g_tb = None

class TBReqHandler(SimpleHTTPRequestHandler):
    ''' TBReqHandler
    Temporal Buffer用のHTTPリクエストハンドラー実装クラスです。
    '''    
    def do_GET(self):
        _cwd = os.getcwd()
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            # メタデータ要求 --- メタデータを返す
            metad = {}
            metad['id'] = g_tb._id
            first_path = g_tb._tsdata._fileList[0]
            if first_path.startswith(_cwd):
                first_path = first_path.replace(_cwd, '')
            metad['uri'] = 'file:/' + first_path
            metad['type'] = 'SPH'
            metad['dims'] = g_tb._tsdata._dims
            metad['datalen'] = g_tb._tsdata._datalen
            metad['bbox'] = g_tb._tsdata._bbox
            metad['steps'] = len(g_tb._tsdata._stepList)
            metad['timerange'] = [g_tb._tsdata._timeList[0],
                                  g_tb._tsdata._timeList[-1]]
            
        elif parsed_path.path == '/data':
            # データ要求 --- 指定されたstepのデータを返す
            qs = parse_qs(parsed_path.query)
            try:
                step = int(qs['step'][0])
                did = int(qs['id'][0])
            except:
                msg = 'no id nor step specified.'
                self.send_response(412)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-length', len(msg))
                self.end_headers()
                body = bytes(msg, 'utf-8')
                self.wfile.write(body)
                return
            if did != g_tb._id or \
               step < 0 or step >= len(g_tb._tsdata._stepList):
                if did != g_tb._id:
                    msg = 'invalid id specified: {}.'.format(did)
                else:
                    msg = 'invalid step specified: {}.'.format(step)
                self.send_response(412)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-length', len(msg))
                self.end_headers()
                body = bytes(msg, 'utf-8')
                self.wfile.write(body)
                return
            
            metad = {}
            metad['type'] = 'SPH'
            metad['step'] = step
            sph = g_tb._tsdata.getDataIdx(step)
            if sph == None:
                msg = 'can not get data of step {}.'.format(step)
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-length', len(msg))
                self.end_headers()
                body = bytes(msg, 'utf-8')
                self.wfile.write(body)
                return
            metad['data'] = SPH_filter.toJSON(sph)
            
        meta_str = json.dumps(metad)
        body = bytes(meta_str, 'utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-length', len(body))
        self.end_headers()
        self.wfile.write(body)
        return
    

def usage(prog:str ='TB'):
    print('usage: {} [-p port] [-j input.json | -l file0.sph file1.sph ...]'\
          .format(prog))
    return

    
if __name__ == '__main__':
    import threading
    import time
    import argparse
    prog = 'TB'

    # parse argv
    parser = argparse.ArgumentParser(description='Temporal Buffer prototype')
    parser.add_argument('-p', help='port number', type=int, default='4000')
    parser.add_argument('-j', help='path of input.json')
    parser.add_argument('-l', help='pathes of input sph files', nargs='*')
    args = parser.parse_args()
    if args.j == None and args.l == None:
        print('{}: no input.json nor sph files specified.'.format(prog))
        usage(prog)
        sys.exit(1)

    # prepare Temporal Buffer
    g_tb = TB()
    if args.j != None:
        tbt = threading.Thread(target=g_tb.loadFromJSON, args=([args.j]))
    else:
        tbt = threading.Thread(target=g_tb.loadFromFilelist, args=([args.l]))
    tbt.setDaemon(True)
    tbt.start()

    while True:
        sys.stdout.write('loading: {} steps done\r'.format(g_tb._tsdata.numSteps))
        time.sleep(0.5)
        if not g_tb._tsdata.is_working:
            break
    tbt.join()
    if g_tb._tsdata.is_ready:
        print('\n{}: loaded {} steps.'.format(prog, g_tb._tsdata.numSteps))
    else:
        print('{}: load failed: {}'.format(prog, g_tb._lastErr))
        sys.exit(1)
    
    # prepare HTTP server
    host = '0.0.0.0'
    port = args.p
    httpd = HTTPServer((host, port), TBReqHandler)
    httpd.serve_forever()

    sys.exit(0)
    
