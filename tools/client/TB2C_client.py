#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import wx

import canvas
import uiPanel

class TB2C_App(wx.App):
    def OnInit(self):
        self.SetVendorName('RIKEN')
        self.SetAppName('TB2C_client')

        # toplevel frame
        self._frame = wx.Frame(None, title='TB2C client', size=(800, 600))

        # gfx canvas
        self._canvas = canvas.TB2C_Canvas(self._frame, self)
        self._canvas.setBoxSize([0.0, 0.0, 0.0], [100.0, 50.0, 20.0])

        # UI panel
        self._uiPanel = uiPanel.TB2C_UIPanel(self._frame, self)

        # layout in the frame
        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(self._canvas, 1, wx.EXPAND)
        layout.Add(self._uiPanel, 0, wx.EXPAND)
        self._frame.SetSizer(layout)
        layout.Layout()

        return True
    
if __name__ == '__main__':
    app = TB2C_App()
    app._frame.Show()
    app.MainLoop()
    sys.exit(0)
    
        
