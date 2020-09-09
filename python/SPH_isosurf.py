#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPH_isosurf
"""

import sys, os
import numpy as np
from pySPH import SPH
from skimage import measure


class SPH_isosurf:

    @staticmethod
    def generate(d: SPH.SPH, value: float):
        dimSz = d._dims[0] * d._dims[1] * d._dims[2]
        if dimSz < 8 or d._veclen != 1:
            return None
        
        vol = d._data.reshape([d._dims[2], d._dims[1], d._dims[0]])
        verts, faces, normals, values = measure.marching_cubes(vol, value)

        return (verts, faces, normals)

    @staticmethod
    def saveOBJ(path, verts, faces, normals):
        try:
            with open(path, 'w') as f:
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
    
