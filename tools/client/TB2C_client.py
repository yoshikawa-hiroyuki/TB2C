#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os

try:
    import wx
    import wx.glcanvas as glcanvas
    haveWx = True
except ImportError:
    haveWx = False

try:
    from OpenGL.GL import *
    haveOpenGL = True
except ImportError:
    haveOpenGL = False

from utilMath import *
from frustum import *
from trackball import Trackball
from bbox import BBox

#----------------------------------------------------------------------

class OGL_CanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.context = glcanvas.GLContext(self)

        self._frustum = Frustum()
        self._trackball = Trackball()
        self._size = None

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
        self.OnDraw()

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


class TB2C_Canvas(OGL_CanvasBase):
    def __init__(self, parent):
        OGL_CanvasBase.__init__(self, parent)
        self._obj = BBox()
        self._obj.fit(self._frustum)

    def setBoxSize(self, minpos, maxpos):
        self._obj._p0[:] = minpos[:]
        self._obj._p1[:] = maxpos[:]
        self._obj.fit(self._frustum)
        self.Refresh(False)
        return

    def OnDraw(self):
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
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_LIGHTING)
        #glEnable(GL_LIGHT0)
        #glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 10.0, 0.0])

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


#----------------------------------------------------------------------

if __name__ == '__main__':
    if not haveWx:
        print('not installed wxPython, exit.')
        sys.exit(1)
    app = wx.App(False)
    if not haveOpenGL:
        wx.MessageBox('This program requires the PyOpenGL package.', 'Error')
        sys.exit(1)

    frame = wx.Frame(None, title='TB2C client', size=(800, 600))
    canvas = TB2C_Canvas(frame)
    canvas.setBoxSize([0.0, 0.0, 0.0], [100.0, 50.0, 20.0])
    frame.Show()
    
    app.MainLoop()

    sys.exit(0)
    
