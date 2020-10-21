#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSData represents time-series data
"""

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
        self._bbox = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        self._dataList = []
        self._datalen = 0
        self._minMaxList = []
        self._hasMinMax = False
        self._evt.clear()
        return

    @property
    def is_ready(self):
        return self._ready

    @property
    def dtype(self):
        return self._dtype

    @property
    def stepList(self):
        return self._stepList

    @property
    def timeList(self):
        return self._timeList

    @property
    def fileList(self):
        return self._fileList

    @property
    def bbox(self):
        return self._bbox

    @property
    def datalen(self):
        return self._datalen
    @datalen.setter
    def datalen(self, val):
        self._datalen = val
    
    @property
    def minMax(self):
        if self._hasMinMax:
            return self._minMaxList
        else:
            return None
    
    @property
    def is_working(self):
        return self._evt.is_set()

    @property
    def numSteps(self):
        if self.is_ready:
            return len(self._stepList)
        return 0

    def convStepToIdx(self, stp):
        if not self.is_ready:
            return -1
        if stp < self._stepList[0]:
            return -1
        if stp >= self._stepList[-1]:
            return self.numSteps - 1
        for i in range(self.numSteps):
            if self._stepList[i] > stp:
                break
        return i - 1
    
    def getDataIdx(self, stpIdx):
        if not self.is_ready:
            return None
        if stpIdx < 0 or stpIdx >= self.numSteps:
            return None
        return self._dataList[stpIdx]

    def getDataStp(self, stp):
        stpIdx = self.convStepToIdx(stp)
        return self.getDataIdx(stpIdx)
    
