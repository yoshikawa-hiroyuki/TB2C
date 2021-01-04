#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TB2C_visualize
"""
import os, sys
import json
import subprocess
from math import log10
from collections import OrderedDict as OD

from pySPH import SPH
from SPH_isosurf import SPH_isosurf
from SPH_filter import SPH_filter
import tileset_tmpl


class TB2C_visualize:
    ''' TB2C_visualize:
    TB2Cサーバ用の、可視化機能実装クラスです。
    SPHデータに対する可視化(等値面生成)結果をジオメトリ(OBJ)ファイルに出力し、
    obj23dtilesコマンドを使用して3D-Tilesに変換します。
    '''
    def __init__(self, outdir:str ='.'):
        self._outDir = outdir
        self._obj23dt_ver = None
        self._doc = tileset_tmpl._tmpl
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
        出力先ディレクトリ(self._outDir)配下に"b3dm"ディレクトリを作成します。

        Returns
        -------
        bool: True=成功、False=失敗
        '''
        b3dmDir = os.path.join(self._outDir, 'b3dm')
        try:
            os.makedirs(b3dmDir, exist_ok=True)
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

    def isosurf(self, sph_lst:[SPH.SPH], value:float, fnbase:str='isosurf') \
        -> bool:
        ''' isosurf
        sph_lstで渡されたSPHデータ群に対し、valueで指定された値で等値面を生成し、
        OBJファイルに出力した後、obj23dtilesコマンドを使用して3D-Tilesに変換します。
        self._out_dir配下に、以下のファイルが作成されます。
          tileset.json
          b3dm/fnbase_nnn.b3dm

        Parameters
        ----------
        sph_lst: [SPH.SPH]
          等値面を生成するSPHデータのリスト
        value: float
          等値面を生成する値
        fnbase: str
          等値面ファイルのベース名

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

        whole_bbox = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        sph = sph_lst[0]
        whole_bbox[0][:] = sph._org[:]
        for i in range(3):
            whole_bbox[1][i] = sph._org[i] + sph._pitch[i]*(sph._dims[i]-1)

        root = self._doc['root']
        root['children'] = []
        b3dmDir = os.path.join(self._outDir, 'b3dm')
        cnt = 0
        for sph in sph_lst:
            # pathes
            obj_path = os.path.join(b3dmDir, fnbase+'_{}.obj'. \
                                    format(str(cnt).zfill(ndigit)))
            b3dm_path0 = fnbase+'_{}.b3dm'.format(str(cnt).zfill(ndigit))
            b3dm_path = os.path.join(b3dmDir, b3dm_path0)
            # generate isosurface
            if sph._veclen == 1:
                xsph = sph
            else:
                xsph = SPH_filter.vectorMag(sph)
            try:
                v, f, n = SPH_isosurf.generate(xsph, value)
            except ValueError: # maybe empty
                open(b3dm_path, 'wb').close()
                cnt += 1
                continue
            # save objfile
            try:
                obj_f = open(obj_path, 'w')
                SPH_isosurf.saveOBJ(obj_f, v, f, n)
                obj_f.close()
            except Exception as e:
                cnt += 1
                continue
            # convert to b3dm
            try:
                subprocess.call(['obj23dtiles', '--b3dm',
                                 '-i', obj_path, '-o', b3dm_path])
            except Exception as e:
                cnt += 1
                continue
            # update whole_bbox
            org = sph._org
            gro = [org[i] +sph._pitch[i]*(sph._dims[i]-1) for i in range(3)]
            for i in range(3):
                if org[i] < whole_bbox[0][i]: whole_bbox[0][i] = org[i]
                if gro[i] > whole_bbox[1][i]: whole_bbox[1][i] = gro[i]
            # remove objfile
            os.remove(obj_path)

            # add node to root/children list
            node = tileset_tmpl.get_node()
            node['boundingVolume']['box'] = self.bbox2Box([org, gro])
            node['content']['uri'] = b3dm_path0
            root['children'].append(node)
            
            cnt += 1
            continue # end of for(sph)

        # create tileset.json
        root['boundingVolume']['box'] = self.bbox2Box(whole_bbox)
        json_path = os.path.join(self._outDir, 'tileset.json')
        try:
            with open(json_path, 'w') as f:
                f.write(json.dumps(self._doc, indent=2))
        except Exception as e:
            return False

        # done
        return True
