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
        self._infoTxt = wx.TextCtrl(self, size=wx.Size(-1, 200),
                                    style=wx.TE_MULTILINE|wx.TE_READONLY)
        topSizer.Add(self._infoTxt, border=3, flag=wx.EXPAND|wx.ALL)
        self._infoTxt.SetValue('no data loaded.')

        # timestep slider
        topSizer.Add(wx.StaticText(self, label='timestep index'), border=3,
                     flag=wx.ALIGN_LEFT|wx.ALL)
        self._tsSlider = wx.Slider(self, style=wx.SL_AUTOTICKS)
        topSizer.Add(self._tsSlider, border=3, flag=wx.EXPAND|wx.ALL)
        self._tsTxt = wx.TextCtrl(self, size=wx.Size(100,-1),
                                  style=wx.TE_PROCESS_ENTER)
        topSizer.Add(self._tsTxt, border=3,
                     flag=wx.ALIGN_RIGHT|wx.ALL)
        self._tsSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.OnTsSlider)
        self._tsTxt.Bind(wx.EVT_TEXT_ENTER, self.OnTsTxt)

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
        self._isovalSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.OnIsovalSlider)
        self._isovalTxt.Bind(wx.EVT_TEXT_ENTER, self.OnIsovalTxt)

        self.SetSizer(topSizer)
        return

    def OnTsSlider(self, evt):
        val = self._tsSlider.GetValue()
        self._tsTxt.SetValue(str(val))
        self._app.updateRequest(self._app.REQ_UPDDATA)

    def OnTsTxt(self, evt):
        valStr = self._tsTxt.GetValue()
        try:
            val = int(valStr)
        except:
            val = self._tsSlider.GetValue()
            self._tsTxt.SetValue(str(val))
            return
        if val < 0:
            val = 0
            self._tsTxt.SetValue(str(val))
        if val >= self._app.metaDic['steps']-1:
            val = self._app.metaDic['steps']-1
            self._tsTxt.SetValue(str(val))
        self._tsSlider.SetValue(val)
        self._app.updateRequest(self._app.REQ_UPDDATA)

    def OnIsovalSlider(self, evt):
        if not self._app.metaDic: return
        vd = self._app.metaDic['vrange'][1] - self._app.metaDic['vrange'][0]
        ival = self._isovalSlider.GetValue()
        val = self._app.metaDic['vrange'][0] + 0.01*ival*vd
        self._isovalTxt.SetValue('{:.6f}'.format(val))
        self._app.updateRequest(self._app.REQ_UPDDATA)

    def OnIsovalTxt(self, evt):
        if not self._app.metaDic: return
        vd = self._app.metaDic['vrange'][1] - self._app.metaDic['vrange'][0]
        valStr = self._isovalTxt.GetValue()
        try:
            val = float(valStr)
        except:
            ival = self._isovalSlider.GetValue()
            val = self._app.metaDic['vrange'][0] + 0.01*ival*vd
            self._isovalTxt.SetValue('{:.6f}'.format(val))
            return
        if val < self._app.metaDic['vrange'][0]:
            val = self._app.metaDic['vrange'][0]
            self._isovalTxt.SetValue('{:.6f}'.format(val))
        if val > self._app.metaDic['vrange'][1]:
            val = self._app.metaDic['vrange'][1]
            self._isovalTxt.SetValue('{:.6f}'.format(val))
        ival = int((val - self._app.metaDic['vrange'][0])*100/vd)
        self._isovalSlider.SetValue(ival)
        self._app.updateRequest(self._app.REQ_UPDDATA)

    def setInformation(self, info:str):
        self._infoTxt.SetValue(info)

    def setTimeStepRange(self, steps:int) -> bool:
        if steps < 1:
            return False
        self._tsSlider.SetMin(0)
        self._tsSlider.SetMax(steps-1)
        self._tsSlider.SetValue(0)
        self._tsTxt.SetValue(str(0))
        return True

    def setValueRange(self, vrange:[]) -> bool:
        vd = vrange[1] - vrange[0]
        if vd <= 0.0:
            return False
        self._isovalSlider.SetValue(50)
        val = (vrange[0] + vrange[1]) * 0.5
        self._isovalTxt.SetValue('{:.6f}'.format(val))
        return True

    def timeStepChanged(self, val:int):
        print('step={}'.format(val))

    def isovalChanged(self, val:float):
        print('isoval={}'.format(val))

#-------------------------------------
if __name__ == '__main__':
    application = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, 'Test Frame', size=(300, 500))
    panel = TB2C_UIPanel(frame, application)
    frame.Show()
    application.MainLoop()
    
