#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import wx

#-----------------------------------------------------------------------------
class ConnectTB2CSrvDlg(wx.Dialog):
    def __init__(self, url:str=None):
        wx.Dialog.__init__(self, None, -1, 'Connect to TB2C server',
                           size=(300,-1))
        self._urlTxt = wx.TextCtrl(self, size=wx.Size(350,-1))
        if url: self._urlTxt.SetValue(url)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(wx.StaticText(self, label='URL of TB2C server'), border=5,
                   flag=wx.EXPAND|wx.ALL)
        layout.Add(self._urlTxt, 0, border=5, flag=wx.EXPAND|wx.ALL)

        layout.Add(wx.StaticLine(self, -1, size=(2,2)), border=5,
                   flag=wx.EXPAND|wx.ALL)

        btns = wx.StdDialogButtonSizer()
        btnOk = wx.Button(self, wx.ID_OK)
        btnOk.SetDefault()
        btnCancel = wx.Button(self, wx.ID_CANCEL)
        btns.AddButton(btnOk)
        btns.AddButton(btnCancel)
        btns.Realize()
        layout.Add(btns, 0, wx.EXPAND|wx.ALL, 3)

        self.SetSizer(layout)
        self.Fit()
        return

    @property
    def url(self):
        return self._urlTxt.GetValue()

#-----------------------------------------------------------------------------
class ConnectChOWDERDlg(wx.Dialog):
    def __init__(self, hostname:str=None):
        wx.Dialog.__init__(self, None, -1, 'Connect to ChOWDER server',
                           size=(300,-1))
        self._hostTxt = wx.TextCtrl(self, size=wx.Size(350,-1))
        if hostname: self._hostTxt.SetValue(hostname)
        self._pswdTxt = wx.TextCtrl(self, style=wx.TE_PASSWORD)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(wx.StaticText(self, label='hostname/IP-addr of ChOWDER'),
                   border=5, flag=wx.ALIGN_LEFT|wx.ALL)
        layout.Add(self._hostTxt, border=5, flag=wx.ALL|wx.EXPAND)
        layout.Add(wx.StaticText(self, label='password of ChOWDER APIUser'),
                   border=5, flag=wx.ALIGN_LEFT|wx.ALL)
        layout.Add(self._pswdTxt, border=5, flag=wx.ALL|wx.EXPAND)

        layout.Add(wx.StaticLine(self, -1, size=(2,2)), flag=wx.EXPAND|wx.ALL)

        btns = wx.StdDialogButtonSizer()
        btnOk = wx.Button(self, wx.ID_OK)
        btnOk.SetDefault()
        btnCancel = wx.Button(self, wx.ID_CANCEL)
        btns.AddButton(btnOk)
        btns.AddButton(btnCancel)
        btns.Realize()
        layout.Add(btns, 0, wx.EXPAND|wx.ALL, 3)

        self.SetSizer(layout)
        self.Fit()
        return

    @property
    def host(self):
        return self._hostTxt.GetValue()

    @property
    def password(self):
        return self._pswdTxt.GetValue()


#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app = wx.App()

    dlg = ConnectTB2CSrvDlg('http://localhost:80/')
    res = dlg.ShowModal()
    if res == wx.ID_OK:
        print('url={}'.format(dlg.url))
    dlg.Destroy()

    dlg = ConnectChOWDERDlg('localhost')
    res = dlg.ShowModal()
    if res == wx.ID_OK:
        print('hostname={}'.format(dlg.host))
        print('password={}'.format(dlg.password))
    dlg.Destroy()

    sys.exit(0)
