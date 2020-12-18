#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import wx

import canvas
import uiPanel
import uiDialog

class TB2C_App(wx.App):
    def OnInit(self):
        self.SetVendorName('RIKEN')
        self.SetAppName('TB2C_client')

        self._tb2c_serv_url = None
        self._chowder_host = None

        # toplevel frame
        self._frame = wx.Frame(None, title='TB2C client', size=(800, 600))
        fileMenu = wx.Menu()
        menu_connTB2CSrv = fileMenu.Append(wx.ID_ANY, 'Connect to TB2C server')
        menu_connChOWDER = fileMenu.Append(wx.ID_ANY, 'Connect to ChOWDER')
        fileMenu.AppendSeparator()
        menu_quit = fileMenu.Append(wx.ID_EXIT, 'Quit')
        mbar = wx.MenuBar()
        mbar.Append(fileMenu, 'File')
        self._frame.SetMenuBar(mbar)
        self.Bind(wx.EVT_MENU, self.OnQuit, menu_quit)
        self.Bind(wx.EVT_MENU, self.OnConnectTB2CSrv, menu_connTB2CSrv)
        self.Bind(wx.EVT_MENU, self.OnConnectChOWDER, menu_connChOWDER)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

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

        self.SetTopWindow(self._frame)
        self._frame.Show()
        return True

    def Message(self, msg:str, err:bool=False):
        if err:
            dlg = wx.MessageDialog(self._frame, msg, 'Error',
                                   wx.OK|wx.ICON_EXCLAMATION)
        else:
            dlg = wx.MessageDialog(self._frame, msg, 'Notice',
                                   wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        return

    def OnQuit(self, evt):
        sys.exit(0)

    def OnClose(self, evt):
        sys.exit(0)

    def OnConnectTB2CSrv(self, evt):
        dlg = uiDialog.ConnectTB2CSrvDlg(self._tb2c_serv_url)
        res = dlg.ShowModal()
        if res != wx.ID_OK:
            return
        if not self.connectTB2CSrv(dlg.url):
            self.Message('connection to TB2C server failed.', err=True)
            return
        self.Message('connected to TB2C server: {}'.format(dlg.url))
        self._tb2c_serv_url = dlg.url
        return

    def OnConnectChOWDER(self, evt):
        pass

    
    def connectTB2CSrv(self, url:str) -> bool:
        return True

    def requestTB2CSrv(self):
        pass

    def connectChOWDER(self, hostnm:str, pswd:str) -> bool:
        return True

    def requestChOWDER(self):
        pass
    

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import argparse
    prog = 'TB2C_client'

    # parse argv
    parser = argparse.ArgumentParser(description='TB2C client',
      usage='%(prog)s {-s http://localhost:4000/} {-c localhost}')
    parser.add_argument('-s', help='URL of TB2C_server to connect',
                        type=str, default=None)
    parser.add_argument('-c', help='hostname|IP address of ChOWDER server',
                        type=str, default=None)
    args = parser.parse_args()

    # prepare App
    app = TB2C_App()
    if args.s:
        app.connectTB2CSrv(args.s)
    if args.c:
        app.connectChOWDER(args.c)

    # event loop
    app.MainLoop()

    # done
    sys.exit(0)
    
