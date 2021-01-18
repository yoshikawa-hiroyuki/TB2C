#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
divideSph - SPHファイルを指定された個数にエッジを共有して分割する
"""
import sys, os
import numpy as np
from pySPH import SPH
from SPH_filter import SPH_filter

def divide(sph: SPH.SPH, div: [], outbase: str) -> bool:
    if div[0]*div[1]*div[2] < 1:
        return False
    
    sph_lst = SPH_filter.divideShareEdge(sph, div)

    path_tmpl = outbase.replace('%I','{I:0=3}') \
                       .replace('%J','{J:0=3}') \
                       .replace('%K','{K:0=3}')
    if not path_tmpl.endswith('.sph') or not path_tmpl.endswith('.SPH'):
        path_tmpl += '.sph'

    for k in range(div[2]):
        for j in range(div[1]):
            for i in range(div[0]):
                xsph = sph_lst[k*div[0]*div[1] + j*div[0] + i]
                path = path_tmpl.format(I=i, J=j, K=k)
                if not xsph.save(path):
                    return False
    return True

    
if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('usage: {} infile.sph outfile_%I_%J_%K.sph I J K'.format(sys.argv[0]))
        sys.exit(1)
        
    org_sph = SPH.SPH()
    org_sph.load(sys.argv[1])
    div = [int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])]
    if not divide(org_sph, div, sys.argv[2]):
        print('divide SPH failed.')
        sys.exit(1)
    print('done.')
    sys.exit(0)

