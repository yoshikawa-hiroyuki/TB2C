#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from utilMath import *

"""視点タイプ"""
(CYCLOP, LEFT_EYE, RIGHT_EYE) = range(3)

EPSF = 1e-6
DIST = 6378137.0

#----------------------------------------------------------------------
class Frustum(object):
    """
    視垂台クラス
    視垂台はモデル空間の中の視界を表わす垂台の領域です。
     eye: 視点座標
     view: 視線方向ベクトル
     up: 上方向ベクトル
     dist: 視点から注視点までの距離
     halfW/halfH: 注視点における視界の幅および高さの半分の値
     near/far: 視点から前後のクリップ面までの距離
    """

    def __init__(self):
        self._dist = DIST * 2
        self._halfW = DIST
        self._halfH = DIST
        self._near = DIST / 10
        self._far = DIST * 5
        self.resetEye()

    def resetEye(self):
        self._eye = Vec3((self._dist, 0.0, 0.0))
        self._view = Vec3((-1, 0, 0))
        self._up = Vec3((0, 0, 1))

    def rotHead(self, a):
        ''' up周りにviewをa(deg)回転させる
        '''
        RM = Mat4()
        RM.Rotation(Deg2Rad(a), self._up)
        self._view = RM * self._view

    def rotPan(self, a):
        ''' Right(=up x (-view))周りにview, upをa(deg)回転させる
        '''
        Cv = self._view * (-1)
        Uv = self._up
        Rv = Uv.cross(Cv)
        RM = Mat4()
        RM.Rotation(Deg2Rad(a), Rv)
        self._view = RM * self._view
        self._up = RM * self._up

    def trans(self, x, y, z):
        ''' eyeをRight(=up x (-view))方向にx, up方向にy, view方向にz移動させる
        '''
        Cv = self._view * (-1)
        Rv = self._up.cross(Cv)
        self._eye = self._eye + (Rv * x)
        self._eye = self._eye + (self._up * y)
        self._eye = self._eye + (self._view * z)

    def ApplyProjection(self, ortho =False, asp =1.0):
        """
        プロジェクション行列のOpenGL適用
        - ortho: 平行投影モード
        - asp: 視界のアスペクト比率(横/縦)
        """
        try:
            from OpenGL.GL import glFrustum, glOrtho
        except:
            return False

        if self._far - self._near < EPSF: return False
        if not ortho and self._near < EPSF: return False
        if self._halfW < EPSF or self._halfH < EPSF: return False

        aspect = asp
        if aspect < EPSF: aspect = 1.0
        wBias = aspect * self._halfH / self._halfW

        (left, right, top, bottom) = (0,0,0,0)
        try:
            if not ortho:
                d = self._near / self._dist
                top    =  self._halfH * d
                bottom = -self._halfH * d
                right  =  (self._halfW * wBias) * d
                left   = -(self._halfW * wBias) * d
                glFrustum(left, right, bottom, top, self._near, self._far)
            else:
                top    =  self._halfH
                bottom = -self._halfH
                right  =  self._halfW * wBias
                left   = -(self._halfW * wBias)
                glOrtho(left, right, bottom, top, self._near, self._far)
        except:
            return False # no valid OpenGL context
        return True

    def ApplyModelview(self):
        """
        モデルビュー行列のOpenGL適用
          以下の変換を行う行列を生成し、モデルビュー行列とする
          - ステレオ表示の場合、視点位置をオフセットする
          - 視線方向の回転
          - 視点位置への平行移動
        """
        try:
            from OpenGL.GL import glMultMatrixf
        except:
            return False
        M = self.GetMVM()
        try:
            glMultMatrixf(M.m_v.tolist())
        except:
            return False # no valid OpenGL context
        return True

    def GetPM(self, ortho =False, asp =1.0):
        """
        プロジェクション行列を返す
        - ortho: 平行投影モード
        - asp: 視界のアスペクト比率(横/縦)
        """
        PM = Mat4()
        if self._far - self._near < EPSF: return PM
        if not ortho and self._near < EPSF: return PM
        if self._halfW < EPSF or self._halfH < EPSF: return PM

        aspect = asp
        if aspect < EPSF: aspect = 1.0
        wBias = aspect * self._halfH / self._halfW

        (left, right, top, bottom) = (0,0,0,0)
        if not ortho:
            d = self._near / self._dist
            top    =  self._halfH * d
            bottom = -self._halfH * d
            right  =  self._halfW * wBias * d
            left   = -self._halfW * wBias * d
            PM.m_v[ 0] = 2.0*self._near/(right-left)
            PM.m_v[ 5] = 2.0*self._near/(top-bottom)
            PM.m_v[ 8] = (right+left)/(right-left)
            PM.m_v[ 9] = (top+bottom)/(top-bottom)
            PM.m_v[10] = -(self._far+self._near)/(self._far-self._near)
            PM.m_v[11] = -1.0
            PM.m_v[14] = -2.0*self._far*self._near/(self._far-self._near)
            PM.m_v[15] = 0.0
        else:
            top    =  self._halfH
            bottom = -self._halfH
            right  =  self._halfW * wBias
            left   = -self._halfW * wBias
            PM.m_v[ 0] = 2.0/(right-left)
            PM.m_v[ 5] = 2.0/(top-bottom)
            PM.m_v[10] = -2.0/(self._far-self._near)
            PM.m_v[12] = -(right+left)/(right-left)
            PM.m_v[13] = -(top+bottom)/(top-bottom)
            PM.m_v[14] = -(self._far+self._near)/(self._far-self._near)
        return PM

    def GetMVM(self):
        """
        モデルビュー行列を返す
        """
        Cv = self._view * (-1)
        Uv = self._up
        Rv = Uv.cross(Cv)
        MM = Mat4((Rv[0], Uv[0], Cv[0], 0,
                   Rv[1], Uv[1], Cv[1], 0,
                   Rv[2], Uv[2], Cv[2], 0,
                   0, 0, 0, 1))
        MM[12] = - self._eye * Rv
        MM[13] = - self._eye * Uv
        MM[14] = - self._eye * Cv
        return MM

    def GetChOWDERMatrix(self):
        """
        ChOWDER用のカメラ変換行列を返す
        """
        Zv = self._view * (-1)
        Xv = self._up.cross(Zv)
        Yv = Zv.cross(Xv)
        Tv = self._eye
        MM = Mat4((Xv[0], Xv[1], Xv[2], 0,
                   Yv[0], Yv[1], Yv[2], 0,
                   Zv[0], Zv[1], Zv[2], 0,
                   Tv[0], Tv[1], Tv[2], 1))
        return MM
    
                   
