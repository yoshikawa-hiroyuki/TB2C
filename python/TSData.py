#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSData represents time-series data
"""

import sys, os
from pySPH import SPH
import threading

class TSData:
    def __init__(self) -> None:
        self._evt = threading.Event()
        self.reset()
        return

    def reset(self) -> None:
        self._ready = False
        self._dtype = None
        self._stepList = []
        self._timeList = []
        self._fileList = []
        self._curData = None
        self._curIdx = 0
        self._evt.clear()
        return

class TSDataSph(TSData):
    def __init__(self) -> None:
        super().__init__()
        return

    def reset(self) -> None:
        super().reset()
        self._dtype = 'SPH'
        self._dims = [0, 0, 0]
        self._veclen = 0
        self._minMaxList = []
        self._bbox = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        return
    
    def loadCheck(self, fnlist, basedir='.'):
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
        self._veclen = sph._veclen
        for i in range(self._veclen):
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
            if self._veclen != sph._veclen:
                self.reset()
                return False
            for i in range(self._veclen):
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
    
    def setCurStepIdx(self, idx):
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
    
