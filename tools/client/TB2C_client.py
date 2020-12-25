#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TB2C_client
"""
import sys, os
import json
import time
import urllib.request
try:
    import wx # need to install via pip3 (wxPython)
except:
    print('TB2C_client: Error: import wx failed, install wxPython.')
    sys.exit(1)
try:
    import chowder
except:
    print('TB2C_client: Error: import chowder failed, install websocket.')
    sys.exit(1)

import canvas
import uiPanel
import uiDialog

class TB2C_App(wx.App):
    ''' TB2C_App
    TB2C clientのプロトタイプAppクラスです。
    wxPythonのAppクラスを継承しています。
    '''
    def OnInit(self):
        ''' OnInit
        App初期化時のイベントハンドラー。
        トップレベルのFrameを作成し、OpenGL canvasとUI panelを横方向に配置します。
        '''
        self.SetVendorName('RIKEN')
        self.SetAppName('TB2C_client')
        self._metaDic = None
        self._lastErr = None

        self._tb2c_serv_url = None

        self._chowder = chowder.ChOWDER()
        self._chowder_host = None
        self._chowder_loginkey = None

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
        self._canvas.setBoxSize([0.0, 0.0, 0.0], [1.0, 1.0, 1.0])

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

    @property
    def metaDic(self):
        return self._metaDic
    
    @property
    def lastError(self):
        ret = self._lastErr
        if self._lastErr:
            self._lastErr = None
        return ret

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
        ''' OnConnectTB2CSrv
        'Connect to TB2C server'メニューのイベントハンドラー。
        URL入力用のダイアログを表示し、TB2C serverに接続します。

        Parameters
        ----------
        evt: wx.Event
          メニューイベント
        '''
        dlg = uiDialog.ConnectTB2CSrvDlg(self._tb2c_serv_url)
        res = dlg.ShowModal()
        if res != wx.ID_OK:
            return
        if not self.connectTB2CSrv(dlg.url):
            self.Message('connect to TB2C server failed.', err=True)
            return
        self.Message('connected to TB2C server: {}'.format(dlg.url))
        self._tb2c_serv_url = dlg.url
        return

    def OnConnectChOWDER(self, evt):
        ''' OnConnectChOWDER
        'Connect to ChOWDDER'メニューのイベントハンドラー。
        URLおよびパスワード入力用のダイアログを表示し、ChOWDERに接続します。

        Parameters
        ----------
        evt: wx.Event
          メニューイベント
        '''
        dlg = uiDialog.ConnectChOWDERDlg(self._chowder_host)
        res = dlg.ShowModal()
        if res != wx.ID_OK:
            return
        host = dlg.host
        pswd = dlg.password
        if not self.connectChOWDER(host, pswd):
            self.Message('connect to ChOWDER server failed.', err=True)
        self.Message('connected to chOWDER server: {}'.format(host))
        return

    def connectTB2CSrv(self, url:str) -> bool:
        ''' connectTB2CSrv
        urlで指定されたTB2C serverへ接続し、メタデータを取得します。
        取得したメタデータのチェック後、AppのUIに反映します。

        Parameters
        ----------
        url: str
          TB2C serverのURL

        Returns
        -------
        bool: True=成功、False=失敗(self._lastErrにエラーメッセージを登録)
        '''
        try:
            with urllib.request.urlopen(url) as res:
                res_bin = res.read()
            res_str = res_bin.decode()
        except Exception as e:
            self._lastErr = str(e)
            return False
        
        # load and check metadata
        try:
            xdic = json.loads(res_str)
            if xdic['type'] != 'SPH' or \
               xdic['dims'][0]*xdic['dims'][1]*xdic['dims'][2] < 8 or \
               xdic['datalen'] < 1 or xdic['steps'] < 1 or \
               not 'isosurf' in xdic['vistype'] or \
               xdic['vrange'][0] > xdic['vrange'][1] or \
               xdic['bbox'][0][0] > xdic['bbox'][1][0] or \
               xdic['bbox'][0][1] > xdic['bbox'][1][1] or \
               xdic['bbox'][0][2] > xdic['bbox'][1][2]:
                self._lastErr = 'invalid metadata responsed.'
                return False
        except Exception as e:
            self._lastErr = str(e)
            return False
        # update bbox
        self._canvas.setBoxSize(xdic['bbox'][0], xdic['bbox'][1])
        # update info
        info = 'url={}\n'.format(url)
        info += 'steps={}'.format(xdic['steps'])
        try:
            info += ' ({},{})'.format(xdic['timerange'][0],xdic['timerange'][1])
        except:
            pass
        info += '\n'
        info += 'datalen={}\n'.format(xdic['datalen'])
        info += 'vrange={}\n'.format(xdic['vrange'])
        info += 'bbox=({}, {})'.format(xdic['bbox'][0], xdic['bbox'][1])
        self._uiPanel.setInformation(info)
        # update timestep range
        self._uiPanel.setTimeStepRange(xdic['steps'])
        # update isovalue range
        self._uiPanel.setValueRange(xdic['vrange'])
        
        self._metaDic = xdic
        self._tb2c_serv_url = url
        return True

    def requestTB2CSrv(self):
        pass

    def connectChOWDER(self, hostnm:str, pswd:str) -> bool:
        ''' connectChOWDER
        hostnmで指定されたホスト上のChOWDER serverに接続します。

        Parameters
        ----------
        hostnm: str
          ChOWDER serverが動作するホスト(ホスト名またはIPアドレス)
          接続先は'ws://{hostnm}/v2'となる。
        pswd: str
          ChOWDER serverに接続する際のAPIUserのパスワード

        Returns
        -------
        bool: True=成功、False=失敗(self._lastErrにエラーメッセージを登録)
        '''
        if self._chowder.is_open:
            self._chowder.disconnect()
            #self._chowder.wait_until_close()
        try:
            self._chowder.connect(hostnm)
        except Exception as e:
            return False
        
        login_req = chowder.JSONRPC('Login')
        login_req['params']['id'] = 'APIUser'
        login_req['params']['password'] = pswd
        def login_callback(err, result):
            self._chowder_loginkey = result['loginkey']
        self._chowder.send_json(login_req, login_callback)

        import thumb_data
        content_req = chowder.add3DTilesContent(self._chowder, thumb_data._data)
        while not self._chowder.is_done(content_req):
            time.sleep(0.05)
        self._chowder_host = hostnm
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
        if not app.connectTB2CSrv(args.s):
            print('TB2C_client: Error: {}'.format(app.lastError))
            sys.exit(1)
    if args.c:
        app.connectChOWDER(args.c)

    # event loop
    app.MainLoop()

    # done
    sys.exit(0)
    
