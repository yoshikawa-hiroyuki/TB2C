#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPH_filter
"""

import sys, os
import numpy as np
from pySPH import SPH

import json
import base64
import _pickle as pickle

class SPH_filter:

    @staticmethod
    def extractScalar(d: SPH.SPH, dataIdx: int) -> SPH.SPH:
        if d._veclen < 1:
            return None
        if dataIdx < 0 or dataIdx >= d._veclen:
            return None

        sph = SPH.SPH()
        sph._dims[:] = d._dims[:]
        sph._org[:] = d._org[:]
        sph._pitch[:] = d._pitch[:]
        sph._veclen = 1
        sph._step = d._step
        sph._time = d._time
        if d._dtype == SPH.SPH.DT_DOUBLE:
            sph._dtype = SPH.SPH.DT_DOUBLE
            sph._data = np.array(0, dtype=np.float64)
        else:
            sph._dtype = SPH.SPH.DT_SINGLE
            sph._data = np.array(0, dtype=np.float32)
        dimSz = sph._dims[0] * sph._dims[1] * sph._dims[2]
        if dimSz < 1:
            return None
        sph._data.resize(dimSz)

        val = d._data[dataIdx]
        sph._min = [val]
        sph._max = [val]
        for i in range(dimSz):
            val  = d._data[i*self._datalen + dataIdx]
            sph._data[i] = val
            if val < sph._min[0]: sph._min[0] = val
            if val > sph._max[0]: sph._max[0] = val
            continue # end of for(i)
        return sph

    @staticmethod
    def vectorMag(d: SPH.SPH) -> SPH.SPH:
        if d._veclen < 1:
            return None
        if d._veclen == 1:
            return d

        sph = SPH.SPH()
        sph._dims[:] = d._dims[:]
        sph._org[:] = d._org[:]
        sph._pitch[:] = d._pitch[:]
        sph._veclen = 1
        sph._step = d._step
        sph._time = d._time
        if d._dtype == SPH.SPH.DT_DOUBLE:
            sph._dtype = SPH.SPH.DT_DOUBLE
            sph._data = np.array(0, dtype=np.float64)
        else:
            sph._dtype = SPH.SPH.DT_SINGLE
            sph._data = np.array(0, dtype=np.float32)
        dimSz = sph._dims[0] * sph._dims[1] * sph._dims[2]
        if dimSz < 1:
            return None
        sph._data.resize(dimSz)

        vl = np.linalg.norm(d._data[0:d._veclen], ord=2)
        sph._min = [vl]
        sph._max = [vl]
        for i in range(dimSz):
            idx = i * d._veclen
            vl = np.linalg.norm(d._data[idx:idx+d._veclen], ord=2)
            sph._data[i] = vl
            if vl < sph._min[0]: sph._min[0] = vl
            if vl > sph._max[0]: sph._max[0] = vl
            continue # end of for(i)
        return sph
    
    @staticmethod
    def toJSON(d: SPH.SPH) -> str:
        jd = {
            'type': 'sph',
            'data': base64.b64encode(pickle.dumps(d)).decode('utf-8'),
            }
        str_data = json.dumps(jd)
        return str_data

    @staticmethod
    def fromJSON(sd: str) -> SPH.SPH:
        jd = json.loads(sd)
        d = base64.b64decode(jd['data'].encode())
        sph = pickle.loads(d)
        return sph
    
