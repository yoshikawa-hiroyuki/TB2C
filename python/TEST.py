import threading
import time

import TSDataSPH
from SPH_isosurf import SPH_isosurf

def Loader(d):
    d.setupFiles(['uvw_010.sph', 'uvw_020.sph', 'uvw_030.sph'],
                '/Users/yoh/Works/Vtools/data/obstacle')

d = TSDataSPH.TSDataSPH()
t = threading.Thread(target=Loader, args=([d]))
t.setDaemon(True)
t.start()

for i in range(10):
    time.sleep(0.3)
    print(d.curStepIdx)
    if not d.is_working:
        break
    
t.join()

d.setCurStepIdx(2)
sph = d.getScalarSPH(TSDataSPH.TSDataSPH.VECMAG)
print(sph._min, sph._max)

v, f, n = SPH_isosurf.generate(sph, 3.3)
SPH_isosurf.saveOBJ('/tmp/isosurf.obj', v, f, n)

print('done.')
