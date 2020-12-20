#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from utilMath import *
from frustum import Frustum
from OpenGL.GL import *

class BBox:
    MODE_FACE = 1
    MODE_WIRE = 2
    MODE_FACE_WIRE = 3
    
    def __init__(self, minpos=(-0.5, -0.5, -0.5), maxpos=(0.5, 0.5, 0.5)):
        self._p0 = Vec3(minpos)
        self._p1 = Vec3(maxpos)
        self._T = Mat4()
        self._S = Mat4()
        self._mode = BBox.MODE_FACE_WIRE

    def draw(self):
        # apply local matrices
        glPushMatrix()
        glMultMatrixf(self._T.m_v)
        glMultMatrixf(self._S.m_v)

        # set drawing mode
        if self._mode & BBox.MODE_WIRE:
            self.draw_wire()
        if self._mode & BBox.MODE_FACE:
            self.draw_face()
            
        # done
        glPopMatrix()
        return

    def draw_wire(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        glColor3f(1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])

        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])

        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])

        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])

        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])

        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glEnd()

    def draw_face(self):
        red_light   = [1.0, 0.5, 0.5]
        red_dark    = [0.6, 0.2, 0.2]
        green_light = [0.5, 1.0, 0.5]
        green_dark  = [0.2, 0.6, 0.2]
        blue_light  = [0.5, 0.5, 1.0]
        blue_dark   = [0.2, 0.2, 0.6]

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_LIGHTING)
        '''
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 100.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 0.4, 0.3, 1.0]);
        glLightfv(GL_LIGHT1, GL_POSITION, [0.0, 50.0, -100.0, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.2, 0.4, 1.0, 1.0]);
        '''

        glBegin(GL_QUADS)
        glNormal3f( 0.0, 0.0, 1.0)
        glColor3fv(blue_light)
        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])

        glNormal3f( 0.0, 0.0,-1.0)
        glColor3fv(blue_dark)
        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])

        glNormal3f( 0.0, 1.0, 0.0)
        glColor3fv(green_light)
        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])

        glNormal3f( 0.0,-1.0, 0.0)
        glColor3fv(green_dark)
        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])

        glNormal3f( 1.0, 0.0, 0.0)
        glColor3fv(red_light)
        glVertex3f(self._p1[0], self._p1[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p1[2])
        glVertex3f(self._p1[0], self._p0[1], self._p0[2])
        glVertex3f(self._p1[0], self._p1[1], self._p0[2])

        glNormal3f(-1.0, 0.0, 0.0)
        glColor3fv(red_dark)
        glVertex3f(self._p0[0], self._p0[1], self._p0[2])
        glVertex3f(self._p0[0], self._p0[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p1[2])
        glVertex3f(self._p0[0], self._p1[1], self._p0[2])
        glEnd()


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
    
