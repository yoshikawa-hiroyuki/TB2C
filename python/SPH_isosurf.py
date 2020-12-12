#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPH_isosurf
"""

import sys, os, typing
import numpy as np
from pySPH import SPH
from skimage import measure


class SPH_isosurf:

    @staticmethod
    def generate(d: SPH.SPH, value: float) -> ([], [], []):
        ''' generate
        スカラーのSPHデータに対して等値面を生成する(static method)

        Parameters
        ----------
        d: SPH.SPH
          スカラーSPHデータ
        value: float
          等値面の閾値

        Returns
        -------
        float[]: 等値面の頂点リスト
        int[]: 等値面の三角形の頂点リスト
        float[]: 等値面の頂点の法線ベクトルリスト
        '''
        dimSz = d._dims[0] * d._dims[1] * d._dims[2]
        if dimSz < 8 or d._veclen != 1:
            return (None, None, None)
        
        vol = d._data.reshape([d._dims[2], d._dims[1], d._dims[0]])
        verts, faces, normals, values = measure.marching_cubes(vol, value)

        return (verts, faces, normals)

    @staticmethod
    def saveOBJ(f: typing.IO, verts, faces, normals) -> bool:
        ''' saveOBJ
        generateで生成された等値面をOBJファイルに出力する(static method)

        Parameters
        ----------
        f: typing.IO
          OBJファイル
        verts: float[]
          等値面の頂点リスト
        faces: int[]
          等値面の三角形の頂点リスト
        normals: float[]
          等値面の頂点の法線ベクトルリスト

        Returns
        -------
        bool: 成功=True、失敗=False
        '''
        try:
            f.write('o SPH_isosurf\n')
            for v in verts:
                f.write('v {} {} {}\n'.format(*v))
            for vn in normals:
                f.write('vn {} {} {}\n'.format(*vn))
            for tri in faces:
                f.write('f {}//{} {}//{} {}//{}\n'.format(
                    tri[0]+1,tri[0]+1,tri[1]+1,tri[1]+1,tri[2]+1,tri[2]+1))
        except Exception as e:
            return False

        return True
    
