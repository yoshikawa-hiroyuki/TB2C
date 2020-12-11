#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from utilMath import *
from frustum import Frustum
from OpenGL.GL import *

class BBox:
    MODE_FACE = 0
    MODE_WIRE = 1
    
    def __init__(self, minpos=(-0.5, -0.5, -0.5), maxpos=(0.5, 0.5, 0.5)):
        self._p0 = Vec3(minpos)
        self._p1 = Vec3(maxpos)
        self._T = Mat4()
        self._S = Mat4()
        self._mode = BBox.MODE_WIRE

    def draw(self):
        # apply local matrices
        glPushMatrix()
        glMultMatrixf(self._T.m_v)
        glMultMatrixf(self._S.m_v)

        # set drawing mode
        if self._mode == BBox.MODE_WIRE:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # draw six faces of a box
        glBegin(GL_QUADS)
        glNormal3f( 0.0, 0.0, 1.0)
        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])

        glNormal3f( 0.0, 0.0,-1.0)
        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])

        glNormal3f( 0.0, 1.0, 0.0)
        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])

        glNormal3f( 0.0,-1.0, 0.0)
        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])

        glNormal3f( 1.0, 0.0, 0.0)
        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glEnd()

        # done
        glPopMatrix()
        return

    def identity(self):
        self._T.Identity()
        self._S.Identity()

    def fit(self, frustum: Frustum):
        self.identity()
        
        # scale
        s0 = frustum._halfW * 2
        bblen = (self._p1 - self._p0).__abs__()
        s1 = s0 / bblen / 1.732 if bblen > 1e-8 else 1.0
        self._S.Scale(s1)

        # translate
        center = (self._p0 + self._p1) * 0.5
        self._T.Translate(center*(-s1))

        return
    
