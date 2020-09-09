import threading
import time

import TSDataSPH

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
print(d._minMaxList)
print('done.')
