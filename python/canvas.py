#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os

import wx
import wx.glcanvas as glcanvas
from OpenGL.GL import *

from utilMath import *
from frustum import *
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
        self._size = None

        self._obj = BBox()
        self._obj.fit(self._frustum)

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

    def GetMatrix(self):
        ''' GetMatrix
        カメラの変換行列を返ます。

        Returns
        -------
        Mat4: カメラ変換行列
        '''
        M = self._frustum.GetChOWDERMatrix()
        return M

    def GetFitMatrix(self):
        ''' GetFitMatrix
        オブジェクトを視界にフィットさせる変換行列を返ます。

        Returns
        -------
        Mat4: 変換行列
        '''
        return self._obj.matrix

    def OnSize(self, event):
        ''' OnSize
        キャンバスサイズの変更に対するイベントハンドラーです。ビューポート変更を行います。

        Parameters
        ----------
        evt: wx.Event
          サイズイベント
        '''
        wx.CallAfter(self.DoSetViewport)
        event.Skip()

    def DoSetViewport(self):
        size = self._size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)

    def OnPaint(self, event):
        ''' OnPaint
        再描画に対するイベントハンドラーです。描画処理を行います。

        Parameters
        ----------
        evt: wx.Event
          再描画イベント
        '''
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        self.Draw()

    def OnDoubleClick(self, evt):
        ''' OnDoubleClick
        ダブルクリックに対するイベントハンドラーです。視界のリセットを行います。

        Parameters
        ----------
        evt: wx.Event
          マウスイベント
        '''
        self._frustum.resetEye()
        self.Refresh(False)
        return

    def OnMouseDown(self, evt):
        ''' OnMouseDown
        マウスボタン押下に対するイベントハンドラーです。

        Parameters
        ----------
        evt: wx.Event
          マウスイベント
        '''
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

    def OnMouseUp(self, evt):
        ''' OnMouseUp
        マウスボタンリリースに対するイベントハンドラーです。

        Parameters
        ----------
        evt: wx.Event
          マウスイベント
        '''
        if self.HasCapture():
            self.ReleaseMouse()
        self._app.updateRequest(self._app.REQ_UPDVIEW)

    def OnMouseMotion(self, evt):
        ''' OnMouseMotion
        マウス移動に対するイベントハンドラーです。

        Parameters
        ----------
        evt: wx.Event
          マウスイベント
        '''
        if evt.Dragging() and evt.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = evt.GetPosition()
            if evt.ShiftDown():
                tx = (self.lastx-self.x)*0.01*self._frustum._dist
                ty = (self.y-self.lasty)*0.01*self._frustum._dist
                self._frustum.trans(tx, ty, 0)
            elif evt.ControlDown():
                tz = (self.lasty-self.y)*0.01*self._frustum._dist
                self._frustum.trans(0, 0, tz)
            else:
                h = (self.x-self.lastx)*0.01*90
                p = (self.y-self.lasty)*0.01*90
                self._frustum.rotHead(h)
                self._frustum.rotPan(p)
            self.Refresh(False)

    def OnMouseWheel(self, evt):
        ''' OnMouseWheel
        マウスホイール回転に対するイベントハンドラーです。

        Parameters
        ----------
        evt: wx.Event
          マウスイベント
        '''
        rot = evt.GetWheelRotation() / evt.GetWheelDelta()
        tz = rot * 0.02*self._frustum._dist
        self._frustum.trans(0, 0, tz)
        self.Refresh(False)
        self._app.updateRequest(self._app.REQ_UPDVIEW)
        return

    def setBoxSize(self, minpos, maxpos):
        ''' setBoxSize
        表示オブジェクトのバウンディングボックスサイズを設定します。

        Parameters
        ----------
        evtminpos: [float]
          最小座標値
        evtmaxpos: [float]
          最大座標値
        '''
        self._obj._p0[:] = minpos[:]
        self._obj._p1[:] = maxpos[:]
        self._obj.fit(self._frustum)
        self.Refresh(False)
        return

    def Draw(self):
        ''' Draw
        描画処理を行います。
        '''
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

        # draw obj
        self._obj.draw()

        # done
        self.SwapBuffers()
        return
