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
        #self._S = Mat4()

        self.lastx = self.x = 0
        self.lasty = self.y = 0

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

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

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

    def OnMouseUp(self, evt):
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



class TB2C_Canvas(OGL_CanvasBase):
    def __init__(self, parent):
        OGL_CanvasBase.__init__(self, parent)

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
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # apply matrices
        #glMultMatrixf(self._trackball.matrix)
        glMultMatrixf(self._T.m_v)
        glMultMatrixf(self._R.m_v)
        #glMultMatrixf(self._S.m_v)
        
        # draw six faces of a cube
        glBegin(GL_QUADS)
        glNormal3f( 0.0, 0.0, 1.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5, 0.5)

        glNormal3f( 0.0, 0.0,-1.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5)
        glVertex3f( 0.5,-0.5,-0.5)

        glNormal3f( 0.0, 1.0, 0.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5, 0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glVertex3f(-0.5, 0.5, 0.5)

        glNormal3f( 0.0,-1.0, 0.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f(-0.5,-0.5, 0.5)

        glNormal3f( 1.0, 0.0, 0.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5)

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glEnd()

        self.SwapBuffers()


#----------------------------------------------------------------------

if __name__ == '__main__':
    if not haveWx:
        print('not installed wxPython, exit.')
        sys.exit(1)
    app = wx.App(False)
    if not haveOpenGL:
        wx.MessageBox('This program requires the PyOpenGL package.', 'Error')
        sys.exit(1)

    frame = wx.Frame(None, title='TB2C client')
    canvas = TB2C_Canvas(frame)
    frame.Show()
    app.MainLoop()

    sys.exit(0)
    
