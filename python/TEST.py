import threading
import time

import TSDataSPH
from SPH_isosurf import SPH_isosurf
from SPH_filter import SPH_filter

def Loader(d):
    d.setupFiles(['uvw_010.sph', 'uvw_020.sph', 'uvw_030.sph'],
                '/Users/yoh/Works/Vtools/data/obstacle')

d = TSDataSPH.TSDataSPH()
t = threading.Thread(target=Loader, args=([d]))
t.setDaemon(True)
t.start()

for i in range(10):
    time.sleep(0.3)
    print(d.numSteps)
    if not d.is_working:
        break
t.join()

sphV = d.getDataIdx(2)
sphS = SPH_filter.vectorMag(sphV)
print(sphS._min, sphS._max)

v, f, n = SPH_isosurf.generate(sphS, 3.3)
objfile = open('/tmp/isosurf.obj', 'w')
SPH_isosurf.saveOBJ(objfile, v, f, n)
objfile.close()

print('done.')
