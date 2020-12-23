#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TB2C_visualize
"""
import os, sys
import json
import subprocess
from pySPH import SPH
from SPH_isosurf import SPH_isosurf
from math import log10

class TB2C_visualize:
    def __init__(self, outdir:str ='.'):
        self._outDir = outdir
        self._obj23dt_ver = None
        self._doc = {
            'asset':{
                'version': '0.0',
                'tilesetVersion': '1.0.0-obj23dtiles',
                'gltfUpAxis': 'Z'
            },
            'geometricError': 500,
            'root': {}
        }
        return

    def checkObj23dtiles(self):
        if not self._obj23dt_ver:
            try:
                self._obj23dt_ver \
                    = subprocess.check_output(['obj23dtiles', '--version'])
            except:
                return False
        return True

    def checkB3dmDir(self) -> bool:
        b3dmDir = os.path.join(self._outDir, 'b3dm')
        try:
            os.makedirs(b3dmDir, exist_ok=True)
        except:
            return False
        return True

    def createTileset(self, node_lst:[]) -> bool:
        pass
        
    def isosurf(self, sph_lst:[SPH.SPH], value:float, fnbase:str='isosurf') \
        -> bool:
        ''' isosurf
        sph_lstで渡されたSPHデータ群に対し、valueで指定された値で等値面を生成し、
        OBJファイルに出力した後、obj23dtilesコマンドを使用して3D-Tilesに変換します。
        self._out_dir配下に、以下のファイルが作成されます。
          tileset.json
          b3dm/fnbase_**.b3dm
        '''
        if len(sph_lst) < 1:
            return False
        ndigit = int(log10(len(sph_lst)) +1)
        if not self.checkB3dmDir():
            return False

        whole_bbox = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        sph = sph_lst[0]
        whole_bbox[0][:] = sph._org[:]
        for i in range(3):
            whole_bbox[1][i] = sph._org[i] + sph._pitch[i]*(sph._dims[i]-1)

        nd_dic = []
        b3dmDir = os.path.join(self._outDir, 'b3dm')
        cnt = 0
        for sph in sph_lst:
            v, f, n = SPH_isosurf.generate(sph, value)
            if len(f) < 1: continue
            # save objfile
            obj_path = os.path.join(b3dmDir, fnbase+'_{}.obj'. \
                                    format(str(cnt).zfill(ndigit)))
            try:
                obj_f = open(obj_path, 'w')
                SPH_isosurf.saveOBJ(obj_f, v, f, n)
                obj_f.close()
            except Exception as e:
                continue
            # convert to b3dm
            b3dm_path = os.path.join(b3dmDir, fnbase+'_{}.b3dm'. \
                                    format(str(cnt).zfill(ndigit)))
            try:
                subprocess.call(['obj23dtiles', '--b3dm',
                                 '-i', obj_path, '-o', b3dm_path])
            except Exception as e:
                continue
            # update whole_bbox
            org = sph._org[i]
            gro = [org[i] +sph._pitch[i]*(sph._dims[i]-1) for i in range(3)]
            for i in range(3):
                if org[i] < whole_bbox[0][i]: whole_bbox[0][i] = org[i]
                if gro[i] > whole_bbox[1][i]: whole_bbox[1][i] = gro[i]
            # remove objfile

            # add node dict
            jd = json.loads("{'path':{}, 'bbox':{'min':{},'max':{}}}"\
                            .format(b3dm_path, str(org), str(gro)))
            nd_dic.append(jd)
            
            cnt += 1
            continue # end of for(sph)

        # create tileset.json

        json_path = os.path.join(self._outDir, 'tileset.json')
        try:
            f = open(json_path, 'w')
        except Exception as e:
            return False
        
        return True
    
