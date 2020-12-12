#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TB2C_visualize
"""
import os, sys
from pySPH import SPH
from SPH_isosurf import SPH_isosurf

class TB2C_visualize:
    def __init__(self):
        self._outDir = '.'
        return

    def checkB3dmDir(self) -> bool:
        b3dmDir = os.path.join(self._outDir, 'b3dm')
        if os.makedirs(b3dmDir):
            return True
        if os.path.exists(b3dmDir):
            if os.path.isdir(b3dmDir):
                return True
        return False
        
    def isosurf(self, sph_lst:[SPH.SPH], value:float, fnbase:str='isosurf') \
        -> bool:
        if len(sph_lst) < 1:
            return False
        if not self.checkB3dmDir():
            return False

        whole_bbox = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        sph = sph_lst[0]
        whole_bbox[0][:] = sph._org[:]
        for i in range(3):
            whole_bbox[1][i] = sph._org[i] + sph._pitch[i]*(sph._dims[i]-1)

        b3dmDir = os.path.join(self._outDir, 'b3dm')
        for sph in sph_lst:
            v, f, n = SPH_isosurf.generate(sph, value)
            ### save objfile, update whole_bbox

        ### create tileset.json
        return True
    
