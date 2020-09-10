#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSDataSPH
"""

import os, sys
import numpy as np
from TSData import TSData
from pySPH import SPH
from typing import Iterable

class TSDataSPH(TSData):
    VECMAG = -1
    
    def __init__(self) -> None:
        super().__init__()
        return

    def reset(self) -> None:
        super().reset()
        self._dtype = 'SPH'
        self._dims = [0, 0, 0]
        return

    @property
    def dims(self):
        return self._dims
    
    def setupFiles(self, fnlist: Iterable, basedir: str ='.') -> bool:
        self.reset()
        self._evt.set()
        
        # read the first data
        try:
            fn = fnlist[0]
        except:
            return False
        if basedir and len(basedir) > 0:
            fn = os.path.join(basedir, fn)
        sph = SPH.SPH()
        if not sph.load(fn):
            sph = None
            return False
        self._dims[:] = sph._dims[:]
        self.datalen = sph._veclen
        for i in range(self.datalen):
            self._minMaxList.append([sph._min[i], sph._max[i]])
        self._bbox[0] = sph._org
        self._bbox[1] = [sph._org[0] * sph._pitch[0] * (sph._dims[0]-1),
                         sph._org[1] * sph._pitch[1] * (sph._dims[1]-1),
                         sph._org[2] * sph._pitch[2] * (sph._dims[2]-1)]
        self._stepList.append(sph._step)
        self._timeList.append(sph._time)
        self._fileList.append(fn)
        self._curData = sph
        self._curIdx = 0
        self._hasMinMax = True
        self._ready = True

        # read following data
        for idx in range(1, len(fnlist)):
            fn = fnlist[idx]
            if basedir and len(basedir) > 0:
                fn = os.path.join(basedir, fn)
            if not sph.load(fn):
                self.reset()
                return False
            if self._dims[0] != sph._dims[0] or \
               self._dims[1] != sph._dims[1] or self._dims[2] != sph._dims[2]:
                self.reset()
                return False
            if self.datalen != sph._veclen:
                self.reset()
                return False
            for i in range(self.datalen):
                if self._minMaxList[i][0] > sph._min[i]:
                    self._minMaxList[i][0] = sph._min[i]
                if self._minMaxList[i][1] < sph._max[i]:
                    self._minMaxList[i][1] = sph._max[i]
            if self._bbox[0][0] > sph._org[0]: self._bbox[0][0] = sph._org[0]
            if self._bbox[0][1] > sph._org[1]: self._bbox[0][1] = sph._org[1]
            if self._bbox[0][2] > sph._org[2]: self._bbox[0][2] = sph._org[2]
            gro = [sph._org[0] * sph._pitch[0] * (sph._dims[0]-1),
                   sph._org[1] * sph._pitch[1] * (sph._dims[1]-1),
                   sph._org[2] * sph._pitch[2] * (sph._dims[2]-1)]
            if self._bbox[1][0] < gro[0]: self._bbox[1][0] = gro[0]
            if self._bbox[1][1] < gro[1]: self._bbox[1][1] = gro[1]
            if self._bbox[1][2] < gro[2]: self._bbox[1][2] = gro[2]
            self._stepList.append(sph._step)
            self._timeList.append(sph._time)
            self._fileList.append(fn)
            self._curData = sph
            self._curIdx = idx
            continue # en of for(idx)

        if not self.setCurStepIdx(0):
            self.reset()
            return False
        self._evt.clear()
        return True
    
    def setCurStepIdx(self, idx: int) -> bool:
        if not self._ready:
            return False
        if idx == self._curIdx:
            return True
        xidx = idx
        if xidx < 0:
            xidx = 0
        elif xidx >= len(self._stepList):
            xidx = self._stepList -1

        sph = SPH.SPH()
        if not sph.load(self._fileList[xidx]):
            self.reset()
            return False
        self._curData = sph
        self._curIdx = xidx
        return True

    def getScalarSPH(self, dataIdx) -> SPH:
        if not self._ready:
            return False
        if dataIdx >= self._datalen or dataIdx < self.VECMAG:
            return False
        if dataIdx == self.VECMAG and self._datalen != 3:
            return False

        sph = SPH.SPH()
        sph._dims[:] = self._dims[:]
        sph._org[:] = self._curData._org[:]
        sph._pitch[:] = self._curData._pitch[:]
        sph._veclen = 1
        sph._step = self._stepList[self._curIdx]
        sph._time = self._timeList[self._curIdx]

        if dataIdx == 0 and self._datalen == 0:
            sph._data = self._curData._data
            sph._min = [self._minMaxList[0][0]]
            sph._max = [self._minMaxList[0][1]]
        else:
            sph._data = np.array(0, dtype=np.float32)
            dimSz = sph._dims[0] * sph._dims[1] * sph._dims[2]
            sph._data.resize(dimSz)
            if dataIdx == self.VECMAG:
                vl = np.linalg.norm(self._curData._data[0:3], ord=2)
                sph._min = [vl]
                sph._max = [vl]
                for i in range(dimSz):
                    vl = np.linalg.norm(self._curData._data[i*3:i*3+3], ord=2)
                    sph._data[i] = vl
                    if vl < sph._min[0]: sph._min[0] = vl
                    if vl > sph._max[0]: sph._max[0] = vl
                    continue # end of for(i)
            else:
                val = self._curData._data[dataIdx]
                sph._min = [val]
                sph._max = [val]
                for i in range(dimSz):
                    val  = self._curData._data[i*self._datalen + dataIdx]
                    sph._data[i] = val
                    if val < sph._min[0]: sph._min[0] = val
                    if val > sph._max[0]: sph._max[0] = val
                    continue # end of for(i)
        return sph
