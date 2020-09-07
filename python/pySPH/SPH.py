#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
SPH data representation for Sphere framework
"""
from __future__ import print_function
import sys
import struct
import numpy


class SPH:
    """
    Representation of .sph file data
    """

    """ data type """
    (DT_SINGLE, DT_DOUBLE) = (1, 2)

    def __init__(self):
        """
        class initializer
        """
        self.reset()
        return

    def reset(self):
        """
        class identifier
        """
        self._dims = [0, 0, 0]
        self._org = [0.0, 0.0, 0.0]
        self._pitch = [0.0, 0.0, 0.0]
        self._dtype = SPH.DT_SINGLE
        self._veclen = 1
        self._time = 0.0
        self._step = 0
        self._min = [0.0]
        self._max = [0.0]
        self._data = None
        self._path = None
        return

    def load(self, path):
        """
        load from .sph file
         @param path: file path of the .sph file
         @returns: True for succeed or False for failed.
        """
        self._data = None
        self._path = None

        # open file
        try:
            ifp = open(path, "rb")
        except:
            print("SPH.load: open failed: %s" % path)
            return False

        # type record
        bo = '<'
        header = ifp.read(16)
        buff = struct.unpack(bo+'iiii', header)
        svType = buff[1]
        dType = buff[2]
        if ( svType == 1 ):
            self._veclen = 1
        elif ( svType == 2 ):
            self._veclen = 3
        else:
            bo = '>'
            buff = struct.unpack(bo+'iiii', header)
            svType = buff[1]
            dType = buff[2]
            if ( svType == 1 ):
                self._veclen = 1
            elif ( svType == 2 ):
                self._veclen = 3
            else:
                ifp.close()
                return False

        if ( dType == 1 ):
            self._dtype = SPH.DT_SINGLE
        elif ( dType == 2 ):
            self._dtype = SPH.DT_DOUBLE
        else:
            ifp.close()
            return False

        # size record
        if ( dType == 1 ):
            buff = struct.unpack(bo+'iiiii', ifp.read(20))
            self._dims[:] = (buff[1], buff[2], buff[3])
        elif ( dType == 2 ):
            buff = struct.unpack(bo+'i', ifp.read(4))
            buff = struct.unpack(bo+'qqq', ifp.read(24))
            self._dims[:] = (buff[0], buff[1], buff[2])
            buff = struct.unpack(bo+'i', ifp.read(4))

        # org record
        if ( dType == 1 ):
            buff = struct.unpack(bo+'ifffi', ifp.read(20))
            self._org[:] = (buff[1], buff[2], buff[3])
        elif ( dType == 2 ):
            buff = struct.unpack(bo+'i', ifp.read(4))
            buff = struct.unpack(bo+'ddd', ifp.read(24))
            self._org[:] = (buff[0], buff[1], buff[2])
            buff = struct.unpack(bo+'i', ifp.read(4))

        # pitch record
        if ( dType == 1 ):
            buff = struct.unpack(bo+'ifffi', ifp.read(20))
            self._pitch[:] = (buff[1], buff[2], buff[3])
        elif ( dType == 2 ):
            buff = struct.unpack(bo+'i', ifp.read(4))
            buff = struct.unpack(bo+'ddd', ifp.read(24))
            self._pitch[:] = (buff[0], buff[1], buff[2])
            buff = struct.unpack(bo+'i', ifp.read(4))

        # time record
        if ( dType == 1 ):
            buff = struct.unpack(bo+'iifi', ifp.read(16))
            self._step = buff[1]
            self._time = buff[2]
        elif ( dType == 2 ):
            buff = struct.unpack(bo+'i', ifp.read(4))
            buff = struct.unpack(bo+'qd', ifp.read(16))
            self._step = buff[0]
            self._time = buff[1]
            buff = struct.unpack(bo+'i', ifp.read(4))

        # skip data sz
        ifp.read(4)

        dimSz = self._dims[0] * self._dims[1] * self._dims[2]
        if ( svType == 1 ):
            self._min = [0.0,]
            self._max = [0.0,]
            if ( dType == 1 ):
                packStr = 'f'
                dlen = 4
                self._data = numpy.array(0, dtype=numpy.float32)
            else:
                packStr = 'd'
                dlen = 8
                self._data = numpy.array(0, dtype=numpy.float64)
        else:
            self._min = [0.0, 0.0, 0.0]
            self._max = [0.0, 0.0, 0.0]
            if ( dType == 1 ):
                packStr = 'fff'
                dlen = 12
                self._data = numpy.array(0, dtype=numpy.float32)
            else:
                packStr = 'ddd'
                dlen = 24
                self._data = numpy.array(0, dtype=numpy.float64)
        self._data.resize(dimSz*self._veclen)

        # read the first data
        vals = struct.unpack(bo+packStr, ifp.read(dlen))
        for l in range(0, self._veclen):
            self._data[l] = vals[l]
            self._min[l] = vals[l]
            self._max[l] = vals[l]

        # read datas folowing
        for i in range(1, dimSz):
            vals = struct.unpack(bo+packStr, ifp.read(dlen))
            for l in range(0, self._veclen):
                self._data[i*self._veclen + l] = vals[l]
                if ( self._min[l] > vals[l] ):
                    self._min[l] = vals[l]
                elif ( self._max[l] < vals[l] ):
                    self._max[l] = vals[l]

        # done
        ifp.close()
        self._path = path
        return True

    def save(self, path =None, dtype =None):
        """
        save to .sph file
         @param path: file path of the .sph file. if None, use self._path
         @param dtype: file dtype of the .sph file. if None, use self._dtype
         @returns: True for succeed or False for failed.
        """
        if self._data is None: return False
        xpath = path
        if xpath is None: xpath = self._path
        if xpath is None: return False
        xtype = dtype
        if xtype is None: xtype = self._dtype
        if xtype is None: return False

        # open output file
        try:
            ofp = open(xpath, "wb")
        except:
            print("SPH.save: open failed: %s" % xpath)
            return False
        self._dtype = xtype

        # attr record
        buff = [8, 1, 1, 8]
        if self._veclen == 3: buff[1] = 2
        if self._dtype == SPH.DT_DOUBLE: buff[2] = 2
        ofp.write(struct.pack('4i', buff[0], buff[1], buff[2], buff[3]))

        # size record
        if self._dtype == SPH.DT_DOUBLE:
            ofp.write(struct.pack('i', 24))
            ofp.write(struct.pack('3q',
                                  self._dims[0], self._dims[1], self._dims[2]))
            ofp.write(struct.pack('i', 24))
        else:
            ofp.write(struct.pack('5i', 12, self._dims[0], self._dims[1],
                                  self._dims[2], 12))

        # org record
        if self._dtype == SPH.DT_DOUBLE:
            ofp.write(struct.pack('i', 24))
            ofp.write(struct.pack('3d',
                                  self._org[0], self._org[1], self._org[2]))
            ofp.write(struct.pack('i', 24))
        else:
            ofp.write(struct.pack('i3fi', 12, self._org[0], self._org[1],
                                  self._org[2], 12))

        # pitch record
        if self._dtype == SPH.DT_DOUBLE:
            ofp.write(struct.pack('i', 24))
            ofp.write(struct.pack('3d', self._pitch[0],
                                  self._pitch[1], self._pitch[2]))
            ofp.write(struct.pack('i', 24))
        else:
            ofp.write(struct.pack('i3fi', 12, self._pitch[0], self._pitch[1],
                                  self._pitch[2], 12))

        # time record
        if self._dtype == SPH.DT_DOUBLE:
            ofp.write(struct.pack('i', 16))
            ofp.write(struct.pack('qd', self._step, self._time))
            ofp.write(struct.pack('i', 16))
        else:
            ofp.write(struct.pack('iifi', 8, self._step, self._time, 8))

        # data record
        dimSz = self._dims[0] * self._dims[1] * self._dims[2]
        dimVX = self._veclen * self._dims[0]
        k = 0
        if self._dtype == SPH.DT_DOUBLE:
            dfmt = '%dd' % dimVX
            ofp.write(struct.pack('i', dimSz*self._veclen*8))
            for i in range(self._dims[2]):
                for j in range(self._dims[1]):
                    ofp.write(struct.pack(dfmt, *self._data[k:k+dimVX]))
                    k = k + dimVX
                    continue # end of for(j)
                continue # end of for(i)
            ofp.write(struct.pack('i', dimSz*self._veclen*8))
        else:
            dfmt = '%df' % dimVX
            ofp.write(struct.pack('i', dimSz*self._veclen*4))
            for i in range(self._dims[2]):
                for j in range(self._dims[1]):
                    ofp.write(struct.pack(dfmt, *self._data[k:k+dimVX]))
                    k = k + dimVX
                    continue # end of for(j)
                continue # end of for(i)
            ofp.write(struct.pack('i', dimSz*self._veclen*4))

        ofp.close()
        self._path = xpath
        return True

    def loadFromFort(self, path, dims, veclen=1, dtype=DT_SINGLE,
                     org=(0.0,0.0,0.0), pitch=(1.0,1.0,1.0),
                     tm=0.0, step=0, xcut=(0,0), ycut=(0,0), zcut=(0,0)):
        """
        load from FORTRAN Unformatted file
         @param path: file path to read
         @param dims: data array size (X, Y, Z)
         @param veclen: vector length of each data(defalt=1)
         @param dtype: data type(default=single precision)
         @param org: corrdinate of the origin of the data(default=[0,0,0])
         @param pitch: voxel pitch of each direction(default=[1,1,1])
         @param tm: time of the data(default=0.0)
         @param step: time step number of the data(default=0)
         @param xcut: size of sleeve data to cut-off at the edge(left, right)
         @param ycut:  default=(0, 0)
         @param zcut:  param 'dims' must include sleeve size, and self._dims
                       will be set to the size exclude sleeve.
         @returns: True for succeed or False for failed.
        """
        self._data = None
        self._path = None

        # check dims, dtype
        dimSz = 0
        try:
            dimSz = dims[0] * dims[1] * dims[2] * veclen
        except:
            print("SPH.loadFromFort: invalid dims or veclen specified.")
            return False
        if dtype == SPH.DT_SINGLE:
            dsz = dimSz * 4
            dds = "f"
        elif dtype == SPH.DT_DOUBLE:
            dsz = dimSz * 8
            dds = "d"
        else:
            print("SPH.loadFromFort: invalid dtype specified.")
            return False

        # open file
        try:
            ifp = open(path, "rb")
        except:
            print("SPH.loadFromFort: open failed: %s" % path)
            return False

        # header
        bo = '<'
        header = ifp.read(4)
        buff = struct.unpack(bo+'i', header)
        if buff[0] != dsz:
            bo = '>'
            buff = struct.unpack(bo+'i', header)
            if buff[0] != dsz:
                print("SPH.loadFromFort: can not figure out byte-order"
                      + " or specified invalid dims.")
                return False

        # read
        ndt = numpy.dtype([("arr", bo + "%d"%dimSz + dds)])
        try:
            chunk = numpy.fromfile(ifp, dtype=ndt, count=1)
        except:
            print("SPH.loadFromFort: data read failed: %s" % path)
            ifp.close()
            return False
        ifp.close()

        arr = chunk[0]["arr"].reshape((dims[2], dims[1], dims[0], veclen),
                                      order='C')

        # setup myself
        self._dims[:] = [dims[0]-xcut[0]-xcut[1],
                         dims[1]-ycut[0]-ycut[1], dims[2]-zcut[0]-zcut[1]]
        vdimSz = self._dims[0]*self._dims[1]*self._dims[2]
        vdsz = vdimSz * veclen
        self._data = arr[zcut[0]:dims[2]-zcut[1], ycut[0]:dims[1]-ycut[1],
                         xcut[0]:dims[0]-xcut[1], :].reshape((vdsz))
        self._veclen = veclen
        self._org[:] = org[:]
        self._pitch[:] = pitch[:]
        self._dtype = dtype
        self._time = tm
        self._step = step

        # check min/max
        self._min = [0.0]*veclen
        self._max = [0.0]*veclen
        for l in range(0, self._veclen):
            self._min[l] = self._data[l]
            self._max[l] = self._data[l]
        for i in range(1, vdimSz):
            for l in range(0, self._veclen):
                val = self._data[i*self._veclen + l]
                if self._min[l] > val:
                    self._min[l] = val
                elif self._max[l] < val:
                    self._max[l] = val
        # done
        return True

    def saveToFort(self, path, dtype =None, endian='@'):
        """
        save to FORTRAN Unformatted file
         @param path: file path to write
         @param dtype: file dtype of the .sph file. if None, use self._dtype
         @param endian: BOM character according to 'struct' module
         @returns: True for succeed or False for failed.
        """
        xtype = dtype
        if xtype is None: xtype = self._dtype
        if xtype is None: return False

        # open output file
        try:
            ofp = open(path, "wb")
        except:
            print("SPH.saveToFort: open failed: %s" % path)
            return False
        
        # data record
        dimSz = self._dims[0] * self._dims[1] * self._dims[2]
        dimVX = self._veclen * self._dims[0]
        k = 0
        if xtype == SPH.DT_DOUBLE:
            dfmt = endian + '%dd' % dimVX
            ofp.write(struct.pack(endian+'i', dimSz*self._veclen*8))
            for i in range(self._dims[2]):
                for j in range(self._dims[1]):
                    ofp.write(struct.pack(dfmt, *self._data[k:k+dimVX]))
                    k = k + dimVX
                    continue # end of for(j)
                continue # end of for(i)
            ofp.write(struct.pack(endian+'i', dimSz*self._veclen*8))
        else:
            dfmt = '%df' % dimVX
            ofp.write(struct.pack(endian+'i', dimSz*self._veclen*4))
            for i in range(self._dims[2]):
                for j in range(self._dims[1]):
                    ofp.write(struct.pack(dfmt, *self._data[k:k+dimVX]))
                    k = k + dimVX
                    continue # end of for(j)
                continue # end of for(i)
            ofp.write(struct.pack(endian+'i', dimSz*self._veclen*4))

        ofp.close()
        return True

    def setNdarray(self, arr):
        """
        setup from numpy.ndarray
         @param arr: numpy.ndarray
         @returns: True for succeed or False for failed.
        """
        shp = arr.shape
        if len(shp) < 1 or len(shp) > 3:
            return False
        shpSz = numpy.array(shp).prod()
        if shpSz < 1:
            return False
        self.reset()

        self._dims = [1, 1, 1]
        for i in range(len(shp)):
            self._dims[len(shp)-1-i] = shp[i]

        self._pitch = [1.0, 1.0, 1.0]
        self._data = arr.reshape((-1))
        self._min[0] = self._data.min()
        self._max[0] = self._data.max()
        return True
    
