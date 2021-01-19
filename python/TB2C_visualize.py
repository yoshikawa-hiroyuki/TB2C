#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TB2C_visualize
"""
import os, sys
import shutil
import json
import subprocess
from math import log10
from collections import OrderedDict as OD

from utilMath import *
from pySPH import SPH
from SPH_isosurf import SPH_isosurf
from SPH_filter import SPH_filter

LONG = 6378137.0


class TB2C_visualize:
    ''' TB2C_visualize:
    TB2Cサーバ用の、可視化機能実装クラスです。
    SPHデータに対する可視化(等値面生成)結果をジオメトリ(OBJ)ファイルに出力し、
    obj23dtilesコマンドを使用して3D-Tilesに変換します。
    '''
    def __init__(self, outdir:str ='.', bbox =[[0,0,0],[1,1,1]]):
        self._outDir = outdir
        self._obj23dt_ver = None
        self._layerList = []
        self._bbox = [Vec3(bbox[0]), Vec3(bbox[1])]
        return

    def checkObj23dtiles(self) -> bool:
        ''' checkObj23dtiles
        "obj23dtiles --version"を実行し、正常に動作するか確認します。

        Returns
        -------
        bool: True=成功、False=失敗
        '''
        if not self._obj23dt_ver:
            try:
                self._obj23dt_ver \
                    = subprocess.check_output(['obj23dtiles', '--version'])
            except:
                self._obj23dt_ver = None
                return False
        return True

    def checkB3dmDir(self) -> bool:
        ''' checkB3dmDir
        出力先ディレクトリ(self._outDir)配下に"b3dm"ディレクトリを
        (存在すれば削除してから)作成します。

        Returns
        -------
        bool: True=成功、False=失敗
        '''
        b3dmDir = os.path.join(self._outDir, 'b3dm')
        try:
            if os.path.isfile(b3dmDir):
                os.remove(b3dmDir)
            elif os.path.isdir(b3dmDir):
                shutil.rmtree(b3dmDir)
            os.makedirs(b3dmDir)
        except:
            return False
        return True

    def bbox2Box(self, bbox:[[float],[float]]) -> [float]:
        ''' bbox2Box
        バウンディングボックスデータを、3D-Tileの"Box"形式に変換します。

        Parameters
        ----------
        bbox: [[float],[float]]
          バウンディングボックスデータ

        Returns
        -------
        [float]: 3D-Tileの"Box"形式データ
        '''
        box = []
        c = [(bbox[0][i]+bbox[1][i])*0.5 for i in range(3)]
        hl = [(bbox[1][i]-bbox[0][i])*0.5 for i in range(3)]
        box.extend(c)
        box.extend([hl[0], 0.0, 0.0])
        box.extend([0.0, hl[1], 0.0])
        box.extend([0.0, 0.0, hl[2]])
        return box

    def isosurf(self, sph_lst:[SPH.SPH], value:float,
                fnbase:str='isosurf') -> bool:
        ''' isosurf
        sph_lstで渡されたSPHデータ群に対し、valueで指定された値で等値面を生成し、
        OBJファイルに出力した後、obj23dtilesコマンドを使用して3D-Tilesに変換します。
        self._out_dir配下に、以下のファイルが作成されます。
          b3dm/Batchedfnbase_nnn/fnbase_nnn.b3dm
          b3dm/Batchedfnbase_nnn/tileset.json

        Parameters
        ----------
        sph_lst: [SPH.SPH]
          等値面を生成するSPHデータのリスト
        value: float
          等値面を生成する値
        fnbase: str
          等値面ファイルのベース名(省略時:"isosurf")

        Returns
        -------
        bool: True=成功、False=失敗
        '''
        if len(sph_lst) < 1:
            return False
        ndigit = int(log10(len(sph_lst)) +1)
        if not self.checkB3dmDir():
            return False
        if not self.checkObj23dtiles():
            return False

        whole_bbox = self._bbox
        bblen = (whole_bbox[1] - whole_bbox[0]).__abs__()
        scale = LONG * 2 / bblen / 1.732 if bblen > 1e-8 else 1.0
        centr = (whole_bbox[1] + whole_bbox[0]) * 0.5
        trans = centr * (-scale)
        
        self._layerList = []
        b3dmDir = os.path.join(self._outDir, 'b3dm')
        cnt = 0
        for sph in sph_lst:
            # pathes
            path_base = fnbase+'_{}'.format(str(cnt).zfill(ndigit))
            obj_path = os.path.join(b3dmDir, path_base + '.obj')
            ts_path = os.path.join(b3dmDir, 'Batched'+path_base, 'tileset.json')
            ts_rpath = os.path.join('b3dm', 'Batched'+path_base, 'tileset.json')
            # generate isosurface
            if sph._veclen == 1:
                xsph = sph
            else:
                xsph = SPH_filter.vectorMag(sph)
            try:
                v, f, n = SPH_isosurf.generate(xsph, value)
            except Exception as e: # maybe empty
                cnt += 1
                continue
            # normalize vertices
            v = v * scale
            v = v + trans.m_v
            # save objfile
            try:
                obj_f = open(obj_path, 'w')
                SPH_isosurf.saveOBJ(obj_f, v, f, n)
                obj_f.close()
            except Exception as e:
                cnt += 1
                continue
            # convert to b3dm
            print('exec: obj23dtiles --tileset -i {} ... '\
                  .format(obj_path), end='')
            sys.stdout.flush()
            try:
                subprocess.call(['obj23dtiles', '--tileset', '-i', obj_path])
            except Exception as e:
                cnt += 1
                continue
            # remove objfile
            os.remove(obj_path)

            # modify tileset.json
            try:
                ts_f = open(ts_path, 'r')
                ts_dict = json.load(ts_f, object_pairs_hook=OD)
                ts_f.close()
            except Exception as e:
                cnt += 1
                continue
            ts_dict['asset']['gltfUpAxis'] = 'Z'
            ts_dict['root']['transform'] = [
                1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1]
            try:
                ts_f = open(ts_path, 'w')
                json.dump(ts_dict, ts_f, indent=4)
                ts_f.close()
            except Exception as e:
                cnt += 1
                continue

            # add tileLayer to layerList
            tileLayer = {}
            tileLayer['id'] = path_base
            tileLayer['type'] = '3dtile'
            tileLayer['visible'] = 'true'
            tileLayer['sseThreshold'] = 0
            tileLayer['url'] = 'http://localhost/data/' + ts_rpath
            self._layerList.append(tileLayer)
            
            cnt += 1
            continue # end of for(sph)

        # done
        return True
