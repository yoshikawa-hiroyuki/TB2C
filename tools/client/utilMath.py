#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 * CES Utilities
 *
 * Copyright(c) FUJITSU LIMITED
 *      CES Project, 2008-2019, All Right Reserved.

 utilMath : vector/matrix/quaternions utilities
   Vec3 : represents (x, y, z)
   Mat4 : represents 4x4 matrix
   Quat4 : represents (x, y, z, w) quaternions
   
"""
import sys
import math
import numpy as N

_dt = N.dtype('f4')


def Sqr(x):
    return (x * x)

def Deg2Rad(x):
    return (x * math.pi / 180.0)

def Rad2Deg(x):
    return (x / math.pi * 180.0)


class Vec3(object):
    """
    Vec3 : (x, y, z)=(m_v[0], m_v[1], m_v[2])
    """
    __slots__=['m_v']
    
    def __init__(self, org =None):
        if org and isinstance(org, Vec3):
            self.m_v = N.array([x for x in org.m_v], _dt)
        else:
            try:
                self.m_v = N.array([x for x in org], _dt)
            except:
                self.m_v = N.array([0.0, 0.0, 0.0], _dt)

    def __str__(self):
        return 'Vec3' + str(self.m_v)

    def __getitem__(self, key):
        return self.m_v.__getitem__(key)

    def __setitem__(self, key, value):
        return self.m_v.__setitem__(key, value)
    
    def __neg__(self):
        return self * (-1.0)

    def __pos__(self):
        return self * 1.0

    def __add__(self, a):
        b = Vec3()
        if isinstance(a, Vec3):
            b.m_v = N.array([x + y  for x, y in zip(self.m_v, a.m_v)], _dt)
        else:
            b.m_v = N.array([x + a for x in self.m_v], _dt)
        return b

    __iadd__ = __add__

    def __sub__(self, a):
        return self.__add__(-a)

    __isub__ = __sub__
    
    def __mul__(self, a):
        if isinstance(a, Vec3):
            return sum([x * y for x, y in zip(self.m_v, a.m_v)])
        else:
            b = Vec3()
            b.m_v = N.array([x * a for x in self.m_v], _dt)
            return b

    __rmul__ = __mul__

    def cross(self, a):
        cv = Vec3()
        if not isinstance(a, Vec3): return cv
        cv[0] = self.m_v[1]*a.m_v[2] - self.m_v[2]*a.m_v[1]
        cv[1] = self.m_v[2]*a.m_v[0] - self.m_v[0]*a.m_v[2]
        cv[2] = self.m_v[0]*a.m_v[1] - self.m_v[1]*a.m_v[0]
        return cv

    def __abs__(self):
        return math.sqrt(sum([x * x for x in self.m_v]))

    def unit(self):
        a = self.__abs__()
        b = Vec3((0,0,1))
        if a < 1e-8: return b
        b.m_v = N.array([x/a for x in self.m_v], _dt)
        return b


class Mat4(object):
    """
    Mat4 : 4x4 matrix
            m_v[ 0] m_v[ 4] m_v[ 8] m_v[12]
            m_v[ 1] m_v[ 5] m_v[ 9] m_v[13]
            m_v[ 2] m_v[ 6] m_v[10] m_v[14]
            m_v[ 3] m_v[ 7] m_v[11] m_v[15]
    """
    __slots__=['m_v']

    def __init__(self, org =None):
        if org and isinstance(org, Mat4):
            self.m_v = N.array([x for x in org.m_v], _dt)
        else:
            try:
                self.m_v = N.array([x for x in org], _dt)
            except:
                self.m_v = N.array([0.0 for i in range(16)], _dt)
                self.Identity()


    def __str__(self):
        return 'Mat4' + str(self.m_v)

    def __getitem__(self, key):
        return self.m_v.__getitem__(key)

    def __setitem__(self, key, value):
        return self.m_v.__setitem__(key, value)
    
    def Identity(self):
        self.m_v[0:] = 0.0
        self.m_v[0] = self.m_v[5] = self.m_v[10] = self.m_v[15] = 1.0
    
    def __mul__(self, m):
        if isinstance(m, Mat4):
            w = Mat4()
            for i in range(4):
                for j in range(4):
                    w.m_v[i*4 +j] = 0.0
                    for k in range(4):
                        l = i * 4
                        w.m_v[l + j] += (self.m_v[j + k*4] * m.m_v[l + k])
            return w
        elif isinstance(m, Vec3):
            w = Vec3()
            for i in range(0,3):
                w.m_v[i] = 0.0
                for k in range(0,3):
                    w.m_v[i] += (self.m_v[i + k*4] * m.m_v[k])
                w.m_v[i] += self.m_v[i + 12]
            return w
        else:
            w = Mat4([x*m for x in self.m_v])
            return w
        

    def Scale(self, s):
        w = Mat4()
        if isinstance(s, Vec3):
            w.m_v[0] = s.m_v[0]; w.m_v[5] = s.m_v[1]; w.m_v[10] = s.m_v[2]
        else:
            try:
                w.m_v[0] = s[0]; w.m_v[5] = s[1]; w.m_v[10] = s[2]
            except:
                w.m_v[0] = w.m_v[5] = w.m_v[10] = s
        x = self * w
        self.m_v[0:] = x.m_v[0:]


    def Translate(self, t):
        w = Mat4()
        if isinstance(t, Vec3):
            w.m_v[12] = t.m_v[0]; w.m_v[13] = t.m_v[1]; w.m_v[14] = t.m_v[2]
        else:
            try:
                w.m_v[12] = t[0]; w.m_v[13] = t[1]; w.m_v[14] = t[2]
            except:
                w.m_v[12] = w.m_v[13] = w.m_v[14] = t
        x = self * w
        self.m_v[0:] = x.m_v[0:]
    

    def RotX(self, rx):
        w = Mat4()
        w.m_v[ 5] = math.cos(rx)
        w.m_v[ 6] = math.sin(rx)
        w.m_v[ 9] =-w.m_v[ 6]
        w.m_v[10] = w.m_v[ 5]
        x = self * w
        self.m_v[0:] = x.m_v[0:]

    def RotY(self, ry):
        w = Mat4()
        w.m_v[ 0] = math.cos(ry)
        w.m_v[ 8] = math.sin(ry)
        w.m_v[ 2] =-w.m_v[ 8]
        w.m_v[10] = w.m_v[ 0]
        x = self * w
        self.m_v[0:] = x.m_v[0:]
        

    def RotZ(self, rz):
        w = Mat4()
        w.m_v[ 0] = math.cos(rz)
        w.m_v[ 1] = math.sin(rz)
        w.m_v[ 4] =-w.m_v[ 1]
        w.m_v[ 5] = w.m_v[ 0]
        x = self * w
        self.m_v[0:] = x.m_v[0:]

    def Rotation(self, a, v):
        m = Mat4(); uut = Mat4(); ciu = Mat4(); s = Mat4()
        sa = math.sin(a)
        ca = math.cos(a)
        u = Vec3(v).unit()
    
        uut.m_v[0 ] = u.m_v[0]*u.m_v[0]
        uut.m_v[5 ] = u.m_v[1]*u.m_v[1]
        uut.m_v[10] = u.m_v[2]*u.m_v[2]
        uut.m_v[1 ] = uut.m_v[4] = u.m_v[0] * u.m_v[1]
        uut.m_v[2 ] = uut.m_v[8] = u.m_v[0] * u.m_v[2]
        uut.m_v[6 ] = uut.m_v[9] = u.m_v[1] * u.m_v[2]
        for i in range(0, 3):
            for j in range(0, 3):
                k = j*4 + i
                ciu.m_v[k] -= uut.m_v[k]
                ciu.m_v[k] *= ca

        s.m_v[0] =  s.m_v[5] = s.m_v[10] = 0.0
        s.m_v[1] =  u.m_v[2] * sa
        s.m_v[2] = -u.m_v[1] * sa
        s.m_v[4] = -u.m_v[2] * sa
        s.m_v[6] =  u.m_v[0] * sa
        s.m_v[8] =  u.m_v[1] * sa
        s.m_v[9] = -u.m_v[0] * sa
        for i in range(0, 3):
            for j in range(0, 3):
                k = j*4 + i
                m.m_v[k] = uut.m_v[k] + ciu.m_v[k] + s.m_v[k]
        x = self * m
        self.m_v[0:] = x.m_v[0:]


    def transpose(self):
        x = Mat4(self)
        x.m_v[ 4] = self.m_v[ 1]; x.m_v[ 1] = self.m_v[ 4]
        x.m_v[ 8] = self.m_v[ 2]; x.m_v[ 2] = self.m_v[ 8]
        x.m_v[12] = self.m_v[ 3]; x.m_v[ 3] = self.m_v[12]
        x.m_v[ 9] = self.m_v[ 6]; x.m_v[ 6] = self.m_v[ 9]
        x.m_v[13] = self.m_v[ 7]; x.m_v[ 7] = self.m_v[13]
        x.m_v[14] = self.m_v[11]; x.m_v[11] = self.m_v[14]
        return x


    def inverse(self):
        RET = Mat4()
        ip = 4;
        l = [0,0,0,0]
        m = [0,0,0,0]
        r = [[self.m_v[ 0], self.m_v[ 4], self.m_v[ 8], self.m_v[12]],
             [self.m_v[ 1], self.m_v[ 5], self.m_v[ 9], self.m_v[13]],
             [self.m_v[ 2], self.m_v[ 6], self.m_v[10], self.m_v[14]],
             [self.m_v[ 3], self.m_v[ 7], self.m_v[11], self.m_v[15]]]

        for k in range(0, ip):
            m[k] = l[k] = k
            b = r[k][k]
            for j in range(k, ip):
                for i in range(k, ip):
                    if abs(r[j][i]) > abs(b):
                        b = r[j][i]; l[k] = i; m[k] = j
            if abs(b) < 1e-12:
                RET.m_v = [0.0 for i in self.m_v]
                return RET # Failed: returns Zero.
            j = l[k]
            if j > k:
                for i in range(0, ip):
                    t = -r[i][k]
                    r[i][k] = r[i][j]
                    r[i][j] = t
            i = m[k]
            if i > k:
                for j in range(0, ip):
                    t = -r[k][j]
                    r[k][j] = r[i][j]
                    r[i][j] = t
            for i in range(0, ip):
                if i != k: r[k][i] /= -b
            for i in range(0, ip):
                for j in range(0, ip):
                    if i != k and j != k: r[j][i] += r[k][i] * r[j][k]
            for j in range(0, ip):
                if j != k: r[j][k] /= b
            r[k][k] = 1.0 / b
            
        for k in range(ip - 2, -1, -1):
            i = l[k]
            if i > k:
                for j in range(0, ip):
                    t = r[k][j]
                    r[k][j] = -r[i][j]
                    r[i][j] = t
            j = m[k]
            if j > k:
                for i in range(0, ip):
                    t = r[i][k]
                    r[i][k] = -r[i][j]
                    r[i][j] = t
      
        RET.m_v[ 0] = r[0][0]; RET.m_v[ 1] = r[1][0]
        RET.m_v[ 2] = r[2][0]; RET.m_v[ 3] = r[3][0]
        RET.m_v[ 4] = r[0][1]; RET.m_v[ 5] = r[1][1]
        RET.m_v[ 6] = r[2][1]; RET.m_v[ 7] = r[3][1]
        RET.m_v[ 8] = r[0][2]; RET.m_v[ 9] = r[1][2]
        RET.m_v[10] = r[2][2]; RET.m_v[11] = r[3][2]
        RET.m_v[12] = r[0][3]; RET.m_v[13] = r[1][3]
        RET.m_v[14] = r[2][3]; RET.m_v[15] = r[3][3]
        return RET


class Quat4(object):
    """
    Quat4 : Quaternions
        (xi, yj, zk, w) = (m_i[0], m_i[1], m_i[2], m_w)
    """
    __slots__=['m_i', 'm_w']

    def __init__(self, org =None):
        if org and isinstance(org, Quat4):
            self.m_i = Vec3(org=org.m_i)
            self.m_w = org.m_w
        else:
            try:
                self.m_i = Vec3(org[0:3])
                self.m_w = org[3:4][0]
            except:
                self.m_i = Vec3()
                self.m_w = 1.0

    def __str__(self):
        return 'Quat4[' + self.m_i.__str__() +', ' + str(self.m_w) +']'

    def Identity(self):
        self.m_i = Vec3()
        self.m_w = 1.0


    def conjugate(self):
        x = Quat4(self)
        x.m_i = -x.m_i
        return x;

    def norm(self):
        return (self.m_w * self.m_w) + (self.m_i * self.m_i)

    def __abs__(self):
        return math.sqrt(self.norm())

    def inverse(self):
        return self.conjugate() / self.norm()

    def unit(self):
        a = self.__abs__()
        b = Quat4()
        if a < 1e-8: return b
        b.m_i = self.m_i *(1.0/a)
        b.m_w = self.m_w / a
        return b

    def __neg__(self):
        return self * (-1.0)

    def __pos__(self):
        return self * 1.0

    def __add__(self, a):
        b = Quat4()
        if isinstance(a, Quat4):
            b.m_i = self.m_i + a.m_i
            b.m_w = self.m_w + a.m_w
        else:
            b.m_w = self.m_w + a
        return b

    __iadd__ = __add__

    def __sub__(self, a):
        return self.__add__(-a)

    __isub__ = __sub__


    def dotImagenary(self, a):
        return sum([x * y for x, y in zip(self.m_i.m_v, a.m_i.m_v)])

    def crossImagenary(self, a):
        x = Vec3(self.m_i)
        if isinstance(a, Quat4):
            y = Vec3(a.m_i)
        else:
            y = a
        return x.cross(a)

    def __mul__(self, a):
        x = Quat4()
        if isinstance(a, Quat4):
            # returns (v x v' + w v' + w'v, w w' - (v,v'))
            x.m_i = self.crossImagenary(a) + a.m_i*self.m_w + self.m_i*a.m_w
            x.m_w = self.m_w * a.m_w - self.dotImagenary(a)
        else:
            x.m_i = self.m_i * a
            x.m_w = self.m_w * a
        return x
            

    def Rotation(self, a, v):
        u = Vec3(v).unit()
        self.m_i = u * math.sin(a/2.0)
        self.m_w = math.cos(a/2.0)

    def rotMat(self):
        M = Mat4()
        N = self.norm()
        if N < 1e-8: return M
        N = 2.0 / N
        xx=self.m_i[0]*self.m_i[0]; xy=self.m_i[0]*self.m_i[1]
        xz=self.m_i[0]*self.m_i[2]; xw=self.m_i[0]*self.m_w
        yy=self.m_i[1]*self.m_i[1]; yz=self.m_i[1]*self.m_i[2]
        yw=self.m_i[1]*self.m_w
        zz=self.m_i[2]*self.m_i[2]; zw=self.m_i[2]*self.m_w
        M.m_v[0] = 1-N*(yy+zz); M.m_v[4] =   N*(xy-zw); M.m_v[8] =   N*(xz+yw)
        M.m_v[1] =   N*(xy+zw); M.m_v[5] = 1-N*(xx+zz); M.m_v[9] =   N*(yz-xw)
        M.m_v[2] =   N*(xz-yw); M.m_v[6] =   N*(yz+xw); M.m_v[10]= 1-N*(xx+yy)
        M.m_v[ 3] = M.m_v[ 7] = M.m_v[11] = 0.0
        M.m_v[12] = M.m_v[13] = M.m_v[14] = 0.0
        M.m_v[15] = 1.0
        return M


def QuatSlerp(q1, q2, t):
    """Slerp of Quaternions
    """
    if not isinstance(q1, Quat4) or not isinstance(q2, Quat4):
        return None
    cosX = q1.dotImagenary(q2) + q1.m_w*q2.m_w
    if cosX > 1.0: cosX = 1.0
    elif cosX < -1.0: cosX = -1.0
    X  = math.acos(abs(cosX))
    sinX = math.sin(X);

    if abs(sinX) > 1e-8:
        s0 = math.sin((1.0-t)* X) / sinX
        s1 = math.sin(   t * X) / sinX
    else:
        s0 = 1.0 - t
        s1 = t
    if cosX < 0.0: s1 = -s1
    return (q1 * s0) + (q2 * s1)

