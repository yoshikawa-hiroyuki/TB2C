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
    ''' TB
    Temporal Bufferのプロトタイプ実装クラスです。
    JSONまたはファイルリストで指定された時系列SPHデータを読み込み、保持します。
    また、要求されたタイムスライスのデータをエンコードして送信します。
    '''
    def __init__(self) -> None:
        self._tsdata = TSDataSPH()
        self._lastErr = None
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


def usage(prog:str ='TB'):
    print('usage: {} [-j input.json | -l file0.sph file1.sph ...]'\
          .format(prog))
    return

    
if __name__ == '__main__':
    import threading
    import time

    tbApp = TB()
    ret = False
    if len(sys.argv) > 1:
        tbt = threading.Thread(target=tbApp.loadFromJSON, args=([sys.argv[1]]))
        tbt.setDaemon(True)
        tbt.start()

        while True:
            print('loading: {} steps done'.format(tbApp._tsdata.numSteps))
            time.sleep(0.5)
            if not tbApp._tsdata.is_working:
                break
        tbt.join()

        if tbApp._tsdata.is_ready:
            ret = True

    print('loaded {} steps.'.format(tbApp._tsdata.numSteps))
    sys.exit(0 if ret == True else 1)
    
