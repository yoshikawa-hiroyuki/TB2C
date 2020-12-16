#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import wx

class TB2C_UIPanel(wx.Panel):
    def __init__(self, parent, app, size=wx.Size(250,-1)):
        wx.Panel.__init__(self, parent, size=size)
        self._app = app

        # toplevel sizer
        topSizer = wx.BoxSizer(wx.VERTICAL)
        
        # info textbox
        self._infoTxt = wx.TextCtrl(self, size=wx.Size(-1, 100),
                                    style=wx.TE_MULTILINE|wx.TE_READONLY)
        topSizer.Add(self._infoTxt, border=3, flag=wx.EXPAND|wx.ALL)

        # timestep slider
        topSizer.Add(wx.StaticText(self, label='timestep index'), border=3,
                     flag=wx.ALIGN_LEFT|wx.ALL)
        self._tsSlider = wx.Slider(self, style=wx.SL_AUTOTICKS)
        topSizer.Add(self._tsSlider, border=3, flag=wx.EXPAND|wx.ALL)
        self._tsTxt = wx.TextCtrl(self, size=wx.Size(100,-1),
                                  style=wx.TE_PROCESS_ENTER)
        topSizer.Add(self._tsTxt, border=3,
                     flag=wx.ALIGN_RIGHT|wx.ALL)

        topSizer.Add(wx.StaticLine(self, -1, size=(2,2)), flag=wx.EXPAND|wx.ALL)

        # isosurf value slider
        topSizer.Add(wx.StaticText(self, label='isosurf value'), border=3,
                     flag=wx.ALIGN_LEFT|wx.ALL)
        self._isovalSlider = wx.Slider(self, style=wx.SL_AUTOTICKS)
        topSizer.Add(self._isovalSlider, border=3, flag=wx.EXPAND|wx.ALL)
        self._isovalTxt = wx.TextCtrl(self, size=wx.Size(100,-1),
                                      style=wx.TE_PROCESS_ENTER)
        topSizer.Add(self._isovalTxt, border=3,
                     flag=wx.ALIGN_RIGHT|wx.ALL)

        self.SetSizer(topSizer)

#-------------------------------------
if __name__ == '__main__':
    application = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, 'Test Frame', size=(300, 500))
    panel = TB2C_UIPanel(frame, application)
    frame.Show()
    application.MainLoop()
    
