#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os

import wx
import wx.glcanvas as glcanvas
from OpenGL.GL import *

from utilMath import *
from frustum import *
from trackball import Trackball
from bbox import BBox

#----------------------------------------------------------------------

class TB2C_Canvas(glcanvas.GLCanvas):
    ''' TB2C_Canvas
    TB2C clientのOpenGL表示用キャンバスクラスです。
    wxPythonのGLCanvasクラスを継承しており、マウスイベント用のハンドラが実装されています。
    '''
    def __init__(self, parent, app):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.context = glcanvas.GLContext(self)
        self._app = app

        self._frustum = Frustum()
        self._trackball = Trackball()
        self._size = None

        self._obj = BBox()
        self._obj.fit(self._frustum)

        self._T = Mat4()
        self._R = Mat4()
        self._S = Mat4()

        self.lastx = self.x = 0
        self.lasty = self.y = 0

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def Getmatrix(self):
        M = Mat4()
        M = M * self._T
        M = M * self._R
        M = M * self._S
        return M

    def GetFitMatrix(self):
        return self._obj.matrix

    def OnSize(self, event):
        wx.CallAfter(self.DoSetViewport)
        event.Skip()

    def DoSetViewport(self):
        size = self._size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        self.Draw()

    def OnDoubleClick(self, evt):
        self._T.Identity()
        self._R.Identity()
        self._S.Identity()
        self._trackball._rotation = [0,0,0,1]
        self.Refresh(False)
        return

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

    def OnMouseUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        self._app.updateRequest(self._app.REQ_UPDVIEW)

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = evt.GetPosition()
            if evt.ShiftDown():
                self._T.Translate([(self.x-self.lastx)*0.1/self._frustum._dist,
                                   (self.lasty-self.y)*0.1/self._frustum._dist,
                                   0.0])
            elif evt.ControlDown():
                self._T.Translate([0.0, 0.0,
                                   (self.lasty-self.y)*0.1/self._frustum._dist])
            else:
                self._trackball.drag_to(self.lastx, self.lasty,
                                        self.x-self.lastx, self.lasty-self.y)
                self._R.m_v[:] = self._trackball.matrix[:]
            self.Refresh(False)

    def OnMouseWheel(self, evt):
        rot = evt.GetWheelRotation() / evt.GetWheelDelta()
        self._S.Scale(1.0 + 0.1*rot)
        self.Refresh(False)

    def setBoxSize(self, minpos, maxpos):
        self._obj._p0[:] = minpos[:]
        self._obj._p1[:] = maxpos[:]
        self._obj.fit(self._frustum)
        self.Refresh(False)
        return

    def Draw(self):
        if not self._size:
            self._size = self.GetClientSize()
        w, h = self._size

        # Projection Matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self._frustum.ApplyProjection(asp=float(w)/float(h))

        # Modelview Matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self._frustum.ApplyModelview()

        # set OpenGL mode
        glEnable(GL_NORMALIZE)
        glEnable(GL_DEPTH_TEST)

        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # apply matrices
        #glMultMatrixf(self._trackball.matrix)
        glMultMatrixf(self._T.m_v)
        glMultMatrixf(self._R.m_v)
        glMultMatrixf(self._S.m_v)
        
        # draw obj
        self._obj.draw()

        # done
        self.SwapBuffers()
        return
