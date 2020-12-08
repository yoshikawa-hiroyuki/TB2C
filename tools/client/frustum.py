#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from utilMath import *

"""視点タイプ"""
(CYCLOP, LEFT_EYE, RIGHT_EYE) = range(3)

EPSF = 1e-6


#----------------------------------------------------------------------
class Frustum(object):
    """
    視垂台クラス
    視垂台はモデル空間の中の視界を表わす垂台の領域です。
     eye: 視点座標
     dist: 視点から注視点までの距離
     halfW/halfH: 注視点における視界の幅および高さの半分の値
     near/far: 視点から前後のクリップ面までの距離
     hpr: 視線方向の回転量。初期の視線方向は(0,0,-1)
          hprは初期視線方向に対するY軸,X軸,Z軸回りの回転量(deg)を表わす
    """

    """ステレオ表示の左右視点の距離"""
    __strOff = 0.05
    
    def __init__(self):
        self._eyeType = CYCLOP
        self._eye = Vec3((0.0, 0.0, 6.0))
        self._eyeOff = Vec3()
        self._dist = 6.0
        self._halfW = 6.0
        self._halfH = 6.0
        self._near = 0.5
        self._far = 500.5
        self._hpr = Vec3()

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

        eoff = Vec3(self._eyeOff)
        if self._eyeType == LEFT_EYE: eoff.m_v[0] -= Frustum.__strOff
        elif self._eyeType == RIGHT_EYE: eoff.m_v[0] += Frustum.__strOff

        aspect = asp
        if aspect < EPSF: aspect = 1.0
        wBias = aspect * self._halfH / self._halfW

        (left, right, top, bottom) = (0,0,0,0)
        try:
            if not ortho:
                d = self._near / (self._dist + eoff.m_v[2])
                top    =  (self._halfH - eoff.m_v[1]) * d
                bottom = -(self._halfH + eoff.m_v[1]) * d
                right  =  (self._halfW * wBias - eoff.m_v[0]) * d
                left   = -(self._halfW * wBias + eoff.m_v[0]) * d
                glFrustum(left, right, bottom, top, self._near, self._far)
            else:
                top    =  self._halfH - eoff.m_v[1]
                bottom = -(self._halfH + eoff.m_v[1])
                right  =  self._halfW * wBias - eoff.m_v[0]
                left   = -(self._halfW * wBias + eoff.m_v[0])
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
            from OpenGL.GL import glTranslatef, glRotatef
        except:
            return False

        eoff = Vec3(self._eyeOff)
        if self._eyeType == LEFT_EYE: eoff.m_v[0] -= Frustum.__strOff
        elif self._eyeType == RIGHT_EYE: eoff.m_v[0] += Frustum.__strOff

        try:
            glTranslatef(-eoff.m_v[0], -eoff.m_v[1], -eoff.m_v[2])
            glRotatef(-self._hpr.m_v[2], 0.0, 0.0, 1.0)
            glRotatef(-self._hpr.m_v[1], 1.0, 0.0, 0.0)
            glRotatef(-self._hpr.m_v[0], 0.0, 1.0, 0.0)
            glTranslatef(-self._eye.m_v[0],-self._eye.m_v[1],-self._eye.m_v[2])
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

        eoff = Vec3(self._eyeOff)
        if self._eyeType == LEFT_EYE: eoff.m_v[0] -= Frustum.__strOff
        elif self._eyeType == RIGHT_EYE: eoff.m_v[0] += Frustum.__strOff

        aspect = asp
        if aspect < EPSF: aspect = 1.0
        wBias = aspect * self._halfH / self._halfW

        (left, right, top, bottom) = (0,0,0,0)
        if not ortho:
            d = self._near / (self._dist + eoff.m_v[2])
            top    =  (self._halfH - eoff.m_v[1]) * d
            bottom = -(self._halfH + eoff.m_v[1]) * d
            right  =  (self._halfW * wBias - eoff.m_v[0]) * d
            left   = -(self._halfW * wBias + eoff.m_v[0]) * d
            PM.m_v[ 0] = 2.0*self._near/(right-left)
            PM.m_v[ 5] = 2.0*self._near/(top-bottom)
            PM.m_v[ 8] = (right+left)/(right-left)
            PM.m_v[ 9] = (top+bottom)/(top-bottom)
            PM.m_v[10] = -(self._far+self._near)/(self._far-self._near)
            PM.m_v[11] = -1.0
            PM.m_v[14] = -2.0*self._far*self._near/(self._far-self._near)
            PM.m_v[15] = 0.0
        else:
            top    =  self._halfH - eoff.m_v[1]
            bottom = -(self._halfH + eoff.m_v[1])
            right  =  self._halfW * wBias - eoff.m_v[0]
            left   = -(self._halfW * wBias + eoff.m_v[0])
            PM.m_v[ 0] = 2.0/(right-left)
            PM.m_v[ 5] = 2.0/(top-bottom)
            PM.m_v[10] = -2.0/(self._far-self._near)
            PM.m_v[12] = -(right+left)/(right-left)
            PM.m_v[13] = -(top+bottom)/(top-bottom)
            PM.m_v[14] = -(self._far+self._near)/(self._far-self._near)
        return PM

    def GetMVRM(self):
        """
        モデルビュー行列の回転成分を返す
        """
        MM = Mat4()
        MM.RotZ(-Deg2Rad(self._hpr.m_v[2]))
        MM.RotX(-Deg2Rad(self._hpr.m_v[1]))
        MM.RotY(-Deg2Rad(self._hpr.m_v[0]))
        return MM

    def GetMVM(self):
        """
        モデルビュー行列を返す
        """
        eoff = Vec3(self._eyeOff)
        if self._eyeType == LEFT_EYE: eoff.m_v[0] -= Frustum.__strOff
        elif self._eyeType == RIGHT_EYE: eoff.m_v[0] += Frustum.__strOff
        MM = Mat4()
        MM.Translate(eoff * (-1))
        MM.RotZ(-Deg2Rad(self._hpr.m_v[2]))
        MM.RotX(-Deg2Rad(self._hpr.m_v[1]))
        MM.RotY(-Deg2Rad(self._hpr.m_v[0]))
        MM.Translate(self._eye * (-1))
        return MM

    def GetEye(self):
        """
        視点位置を返す
        """
        return self._eye + self._eyeOff

    def GetViewDirMVM(self):
        """
        視線方向ベクトルを返す
        """
        MM = GetMVM()
        eye = MM * Vec3((0, 0, 0))
        vdir = MM * Vec3((0, 0, -1)) - eye
        return vdir
