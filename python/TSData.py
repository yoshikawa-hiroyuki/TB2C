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
        self._curData = None
        self._curIdx = 0
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
    def curData(self):
        return self._curData

    @property
    def curStepIdx(self):
        return self._curIdx

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

    def setCurStepIdx(self, idx: int) -> bool:
        pass
    
