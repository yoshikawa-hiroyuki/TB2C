import threading
import time

import TSData

def Loader(d):
    d.loadCheck(['uvw_010.sph', 'uvw_020.sph', 'uvw_030.sph'],
                '/Users/yoh/Works/Vtools/data/obstacle')

d = TSData.TSDataSph()
t = threading.Thread(target=Loader, args=([d]))
t.setDaemon(True)
t.start()

for i in range(10):
    time.sleep(0.3)
    print(d._curIdx)
    if not d._evt.is_set():
        break
    
t.join()
print(d._minMaxList)
print('done.')
