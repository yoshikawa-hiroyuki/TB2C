#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPH_isosurf
"""

import sys, os
import numpy as np
from pySPH import SPH
import TSData
from skimage import measure


class Sph_isosurf:
    VECLEN = -1
    
    def __init__(self, d) -> None:
        self._d = None
        self._ready = False
        if d._dtype != 'SPH':
            return
        if not d._ready:
            return
        self._d = d
        self._ready = True
        return

    def isosurfOBJ(self, stepIdx, dataIdx, value, path):
        if not self._ready:
            return False
        if dataIdx >= self._d._veclen or dataIdx < VECLEN:
            return False
        if dataIdx == VECLEN and self._d._veclen != 3:
            return False
        
        if not self._d.setCurStepIdx(stepIdx):
            return False

        dimSz = self._d._dims[0] * self._d._dims[1] * self._d._dims[2]
        if dataIdx == 0 and self._d._veclen == 0:
            wd = self._d._curData._data
        else:
            wd = np.array(0, dtype=np.float32)
            wd.resize(dimSz)
            if dataIdx == VECLEN:
                for i in range(dimSz):
                    wd[i] = np.linalg.norm(self._d._curData._data[i*3:i*3+3],
                                           ord=2)
            else:
                for i in range(dimSz):
                    wd[i] = self._d._curData._data[i*self._d._veclen+dataIdx]
        vol = wd.reshape([self._d._dims[2], self._d._dims[1], self._d._dims[0]])

        verts, faces, normals, values = measure.marching_cubes(vol, value)

        with open(path, 'w') as f:
            f.write('o isosurf_data\n')
            for v in verts:
                f.write('v {} {} {}\n'.format((v[0], v[1], v[2])))
            for vn in normnals:
                f.write('vn {} {} {}\n'.format((vn[0], vn[1], vn[2])))
            for tri in faces:
                f.write('f {}//{} {}//{} {}//{}\n'.format(
                    (tri[0],tri[0], tri[1],tri[1], tri[2],tri[2])))

        return True
    
